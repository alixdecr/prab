import argparse
import json
import requests
import sys
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


def generate_api_characteristics():
    """
    Generates structural characteristics of provided APIs (paths of OAS files).
    """

    characteristics = {}

    for path in sorted(APIS_PATH.glob("*/*openapi.json")):
    
        # id
        id = path.parent.name

        print(f"Analyzing {id}")

        with open(path, "r", encoding="utf-8-sig") as file:
            spec = json.load(file)

        # oas validity
        try:
            validate(spec)
            oas_validity = ("valid", "")
        except Exception as e:
            error_name = type(e).__name__
            message = " ".join(str(e).split())
            oas_validity = ("invalid", error_name)
            print(f"-> {error_name} for {id}: {message[:60]}...")

        # title
        title = spec.get("info", {}).get("title") or "unknown"

        # oas version
        if spec.get("openapi"):
            oas_version = ("openapi", spec["openapi"])
        elif spec.get("swagger"):
            oas_version = ("swagger", spec["swagger"])
        else:
            oas_version = ("unknown", "")

        # availability
        availability = []
        servers = spec.get("servers", [])
            
        for server in servers:
            url = server.get("url", "")

            if "localhost" in url:
                availability.append((url, "local", ""))
            else:
                # check if the server is working
                try:
                    requests.head(url, timeout=5, allow_redirects=True)
                    available = "available"
                except Exception:
                    available = "not-available"
                    print(f"-> Server {url} is not available")
                
                availability.append((url, "online", available))

        # authentication
        security_schemes = list(spec.get("components", {}).get("securitySchemes", {}) or spec.get("securityDefinitions", {}))

        # rate limiting, routes, and query parameters
        rate_limiting = "no"
        routes = []
        query_parameters = set()
        
        for path, path_item in spec.get("paths", {}).items():

            for param in path_item.get("parameters", []):
                if param.get("in", "") == "query":
                    query_parameters.add(param.get("name"))

            for method, method_item in path_item.items():

                if not isinstance(method_item, dict):
                    continue

                routes.append((method, path))

                for param in method_item.get("parameters", []):
                    if param.get("in", "") == "query":
                        query_parameters.add(param.get("name"))

                for status in method_item.get("responses", {}):
                    if status == "429":
                        rate_limiting = "status-code"

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


def update_api_readmes():
    """
    Updates API READMEs.
    """

    date = datetime.now().strftime("%Y-%m-%d")

    with open(CHAR_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    for id, data in data.items():

        print(f"Updating {id} README")

        oas_version_badge_color = "brightgreen" if data["oas-version"][0] == "openapi" else "orange"
        oas_validity_badge_color = "brightgreen" if data["oas-validity"][0] == "valid" else "red"

        available_servers = sum(1 for s in data["availability"] if s[1] == "local" or s[2] == "available")
        total_servers = len(data["availability"])

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

        for server_data in data["availability"]:
            servers += f"\n| {server_data[0]} | {server_data[1]} | {server_data[2].replace("-", " ")} |"

        total_paths = len({route[1] for route in data["routes"]})

        methods = ""

        for method in ("get", "post", "put", "patch", "delete"):
            count = sum(1 for route in data["routes"] if route[0] == method)
            methods += f"\n| `{method.upper()}` | {count} |"

        markdown = f"""
# Structural Characteristics of {id} ({data["title"]})

*Last update: {date}*

![alt text](https://img.shields.io/badge/oas_version-{data["oas-version"][0]}_v{data["oas-version"][1]}-{oas_version_badge_color}.svg)
![alt text](https://img.shields.io/badge/openapi--spec--validator-{data["oas-validity"][0]}-{oas_validity_badge_color}.svg)
![alt text](https://img.shields.io/badge/available_servers-{available_servers}_of_{total_servers}-{server_badge_color}.svg)

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API and (2) server reachability. While the repository is often updated, the information might not be up-to-date with official API sources.

## Usage Information

**Servers:**

| URL | Hosted | Availability |
| --- | ------ | ------------ |{servers}

**Authentication Methods:** {", ".join(data["auth"]) or "no authentication required"}

**Rate Limiting:** {"yes" if data["rate-limiting"] == "status-code" else "no"}

## Structural Information

**Total Paths:** {total_paths}

**Query Parameters:** {len(data["query-parameters"])}

**Paths by Method:**

| Method | Paths |
| ------ | ----- |{methods}

"""

        out_path = APIS_PATH / id / "README.md"
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(markdown)


def _build_parser():
    """
    Builds the argv parser.
    """

    parser = argparse.ArgumentParser(description="CLI for PRAB, to filer or update APIs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate parser
    generate_parser = subparsers.add_parser("generate", help="Generate API structural characteristics by analyzing their documentation.")

    # update parser
    update_parser = subparsers.add_parser("update", help="Generate API READMEs by analyzing their documentation.")

    # filter parser
    filter_parser = subparsers.add_parser("filter", help="Filter APIs based on specified criteria.")
    filter_parser.add_argument("--availability", choices=ENUM_FIELDS["availability"])
    filter_parser.add_argument("--authentication", choices=ENUM_FIELDS["authentication"])
    filter_parser.add_argument("--pricing", choices=ENUM_FIELDS["pricing"])
    filter_parser.add_argument("--request-limits", choices=ENUM_FIELDS["request-limits"])

    return parser


def main(argv = None):
    """
    Entry point of the command line interface.

    Args:
        argv: Command line arguments (default: ``sys.argv[1:]``).
    """

    args = _build_parser().parse_args(argv)

    if args.command == "generate":
        generate_api_characteristics()

    elif args.command == "update":
        update_api_readmes()


if __name__ == "__main__":
    sys.exit(main())