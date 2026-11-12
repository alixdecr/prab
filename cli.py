import argparse
import json
import requests
from datetime import datetime
from openapi_spec_validator import validate
from openapi_spec_validator.validation.exceptions import OpenAPIValidationError
from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent
APIS_PATH = ROOT_PATH / "apis"
CHAR_PATH = APIS_PATH / "characteristics.json"

ENUM_FIELDS = {
    "availability": ("local", "online", "both"),
    "authentication": ("key", "no"),
    "pricing": ("no", "optional", "yes"),
    "request-limits": ("no", "yes"),
}

HTTP_METHODS = (
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "options",
    "trace",
)

RATE_LIMIT_HEADERS = (
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
    "ratelimit-limit",
    "ratelimit-remaining",
    "ratelimit-reset",
    "retry-after",
)


def generate_api_characteristics() -> None:
    """
    Generates structural characteristics of provided APIs (paths of OAS files).
    """

    characteristics = {}

    for path in sorted(APIS_PATH.glob("*/*openapi.json")):

        # id
        id = path.parent.name

        print(f"Analyzing {id}")

        # oas validity
        spec = {}

        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                spec = json.load(file)

            validate(spec)
            oas_validity = {"status": "valid", "detail": ""}

        except Exception as e:
            error_name = type(e).__name__
            oas_validity = {"status": "invalid", "detail": error_name}
            print(f"-> {error_name} for {id}: {' '.join(str(e).split())[:60]}...")

        # title
        title = spec.get("info", {}).get("title") or "unknown"

        # oas version
        if spec.get("openapi"):
            oas_version = {"family": "openapi", "version": spec["openapi"]}
        elif spec.get("swagger"):
            oas_version = {"family": "swagger", "version": spec["swagger"]}
        else:
            oas_version = {"family": "unknown", "version": ""}

        # availability
        availability = []
        servers = spec.get("servers", [])

        # swagger 2.0 splits a server between host, basePath, and schemes
        if spec.get("swagger") and not spec.get("servers"):
            host = spec.get("host", "")

            if host:
                base_path = spec.get("basePath", "")
                schemes = spec.get("schemes", ["https"])

                if base_path and not base_path.startswith("/"):
                    base_path = f"/{base_path}"

                servers = [{"url": f"{scheme}://{host}{base_path}"} for scheme in schemes]

        for server in servers:
            url = server.get("url", "")

            if "localhost" in url:
                availability.append({"url": url, "hosted": "local", "status": ""})
            else:
                # check if the server is working
                try:
                    requests.head(url, timeout=5, allow_redirects=True)
                    available = "available"
                except Exception:
                    available = "not-available"
                    print(f"-> Server {url} is not available")

                availability.append({"url": url, "hosted": "online", "status": available})

        # authentication
        security_schemes = list(spec.get("components", {}).get("securitySchemes", {}) or spec.get("securityDefinitions", {}))

        # rate limiting, routes, and query parameters
        rate_limiting = {"status": "no", "reason": ""}
        routes = []
        query_parameters = set()

        for path, path_item in spec.get("paths", {}).items():

            for param in path_item.get("parameters", []):
                if param.get("in", "") == "query":
                    query_parameters.add(param.get("name"))

            for method, method_item in path_item.items():

                if method not in HTTP_METHODS or not isinstance(method_item, dict):
                    continue

                routes.append({"method": method, "path": path})

                for param in method_item.get("parameters", []):
                    if param.get("in", "") == "query":
                        query_parameters.add(param.get("name"))

                for status_code, response in method_item.get("responses", {}).items():
                    if status_code == "429":
                        rate_limiting = {"status": "yes", "reason": "status-code"}
                    elif rate_limiting["status"] == "no" and isinstance(response, dict):
                        headers = [name.lower() for name in response.get("headers", {}) or {}]
                        if any(header in RATE_LIMIT_HEADERS for header in headers):
                            rate_limiting = {"status": "yes", "reason": "headers"}

        characteristics[id] = {
            "title": title,
            "oas-validity": oas_validity,
            "oas-version": oas_version,
            "availability": availability,
            "auth": security_schemes,
            "rate-limiting": rate_limiting,
            "routes": routes,
            "query-parameters": sorted(query_parameters)
        }

    with open(CHAR_PATH, "w", encoding="utf-8") as file:
        json.dump(characteristics, file, indent=4)

    print(f"Saved API characteristics to {CHAR_PATH}")


def update_api_readmes() -> None:
    """
    Updates API READMEs.
    """

    date = datetime.now().strftime("%Y-%m-%d")

    if not CHAR_PATH.is_file():
        print("No API characteristics found, generating them first")
        generate_api_characteristics()

    with open(CHAR_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    for api_id, chars in data.items():

        print(f"Updating {api_id} README")

        oas_version_badge_color = "brightgreen" if chars["oas-version"]["family"] == "openapi" else "orange"
        oas_validity_badge_color = "brightgreen" if chars["oas-validity"]["status"] == "valid" else "red"

        available_servers = sum(1 for s in chars["availability"] if s["hosted"] == "local" or s["status"] == "available")
        total_servers = len(chars["availability"])

        if total_servers == 0:
            server_badge_color = "lightgrey"
        else:
            if available_servers == total_servers:
                server_badge_color = "brightgreen"
            elif available_servers == 0:
                server_badge_color = "red"
            else:
                server_badge_color = "orange"

        servers = ""

        for server_data in chars["availability"]:
            servers += f"\n| {server_data['url']} | {server_data['hosted']} | {server_data['status'].replace('-', ' ')} |"

        total_paths = len({route["path"] for route in chars["routes"]})

        methods = ""

        for method in HTTP_METHODS:
            count = sum(1 for route in chars["routes"] if route["method"] == method)
            methods += f"\n| `{method.upper()}` | {count} |"

        if chars["rate-limiting"]["reason"] == "status-code":
            rate_limiting_text = "yes (a 429 status code is defined in the OAS file)"
        elif chars["rate-limiting"]["reason"] == "headers":
            rate_limiting_text = "yes (rate limit headers are defined in the OAS file)"
        else:
            rate_limiting_text = "no"

        markdown = f"""
# Structural Characteristics of {api_id} ({chars["title"]})

*Last update: {date}*

![alt text](https://img.shields.io/badge/oas_version-{chars["oas-version"]["family"]}_v{chars["oas-version"]["version"]}-{oas_version_badge_color}.svg)
![alt text](https://img.shields.io/badge/openapi--spec--validator-{chars["oas-validity"]["status"]}-{oas_validity_badge_color}.svg)
![alt text](https://img.shields.io/badge/available_servers-{available_servers}_of_{total_servers}-{server_badge_color}.svg)

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API and (2) server reachability. While the repository is often updated, the information might not be up-to-date with official API sources.

## Usage Information

**Servers:**

| URL | Hosted | Availability |
| --- | ------ | ------------ |{servers}

**Authentication Methods:** {", ".join(chars["auth"]) or "no authentication required"}

**Rate Limiting:** {rate_limiting_text}

## Structural Information

**Total Paths:** {total_paths}

**Query Parameters:** {len(chars["query-parameters"])}

**Paths by Method:**

| Method | Paths |
| ------ | ----- |{methods}

"""

        out_path = APIS_PATH / api_id / "README.md"
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(markdown)


def _build_parser() -> argparse.ArgumentParser:
    """
    Builds the argv parser.
    """

    parser = argparse.ArgumentParser(description="CLI for PRAB, to filter or update APIs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # update parser
    update_parser = subparsers.add_parser("update", help="Generate API structural characteristics and READMEs by analyzing their documentation.")

    # filter parser
    filter_parser = subparsers.add_parser("filter", help="Filter APIs based on specified criteria.")
    filter_parser.add_argument("--availability", choices=ENUM_FIELDS["availability"])
    filter_parser.add_argument("--authentication", choices=ENUM_FIELDS["authentication"])
    filter_parser.add_argument("--pricing", choices=ENUM_FIELDS["pricing"])
    filter_parser.add_argument("--request-limits", choices=ENUM_FIELDS["request-limits"])

    return parser


def main(argv: list[str] | None = None) -> None:
    """
    Entry point of the command line interface.

    Args:
        argv: Command line arguments (default: ``sys.argv[1:]``).
    """

    args = _build_parser().parse_args(argv)

    if args.command == "update":
        generate_api_characteristics()
        update_api_readmes()


if __name__ == "__main__":
    main()
