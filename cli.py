import argparse
import json
import requests
from datetime import datetime
from openapi_spec_validator import validate
from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent
APIS_PATH = ROOT_PATH / "apis"
CHAR_PATH = APIS_PATH / "characteristics.json"
STATUS_PATH = ROOT_PATH / "STATUS.md"
README_PATH = ROOT_PATH / "README.md"
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")


def generate_api_characteristics() -> None:
    """
    Generates structural characteristics of provided APIs (paths of OAS files).
    """

    characteristics = {}

    for path in sorted(APIS_PATH.glob("*/*openapi.json")):

        # id
        id = path.parent.name

        print(f"Analyzing {id}")

        # oas
        spec = {}

        try:
            with open(path, "r", encoding="utf-8-sig") as file:
                spec = json.load(file)

            validate(spec)
            oas = {"validated": True, "error": None}

        except Exception as e:
            error_name = type(e).__name__
            oas = {"validated": False, "error": error_name}
            print(f"- {error_name}: {' '.join(str(e).split())[:60]}...")

        # oas version
        family = "openapi" if spec.get("openapi") else "swagger" if spec.get("swagger") else "unknown"
        oas["family"] = family
        oas["version"] = spec.get(family) # will be set to None if the family is unknown

        # title
        title = spec.get("info", {}).get("title")

        # servers
        servers = []
        _servers = spec.get("servers", [])

        # swagger 2.0 splits a server between host, basePath, and schemes
        if spec.get("swagger") and not spec.get("servers"):
            host = spec.get("host", "")

            if host:
                base_path = spec.get("basePath", "")
                schemes = spec.get("schemes", ["https"])

                if base_path and not base_path.startswith("/"):
                    base_path = f"/{base_path}"

                _servers = [{"url": f"{scheme}://{host}{base_path}"} for scheme in schemes]

        for server in _servers:
            url = server.get("url", "")

            if "localhost" in url:
                servers.append({"url": url, "hosted": "local", "available": True})
            else:
                # check if the server is working (HEAD, with a GET fallback for servers that do not support HEAD)
                for request_method in (requests.head, requests.get):
                    try:
                        request_method(url, timeout=5, allow_redirects=True, stream=True)
                        available = True
                        break
                    except Exception:
                        available = False
                        pass

                if not available:
                    print(f"- Server {url} is not available")

                servers.append({"url": url, "hosted": "online", "available": available})

        # authentication
        authentication = list(spec.get("components", {}).get("securitySchemes", {}) or spec.get("securityDefinitions", {})) or None

        # rate limiting, routes, and query parameters
        rate_limit = {"active": False, "reason": "no 429 status code response or rate limiting headers"}
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
                        rate_limit = {"active": True, "reason": "presence of 429 status code response"}

                    if isinstance(response, dict):
                        for header in response.get("headers", {}):
                            name = header.lower()
                            if "ratelimit" in name or "retry-after" in name:
                                rate_limit = {"active": True, "reason": "presence of rate limiting headers"}

        characteristics[id] = {
            "title": title,
            "oas": oas,
            "servers": servers,
            "authentication": authentication,
            "rate-limit": rate_limit,
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
        # oas info
        oas = chars["oas"]
        oas_version_badge_color = "brightgreen" if oas["family"] == "openapi" else "orange"
        oas_validity_badge_color = "brightgreen" if oas["validated"] else "red"

        # server info
        servers = chars["servers"]
        total_servers = len(servers)
        available_servers = sum(
            server["hosted"] == "local" or server["available"]
            for server in chars["servers"]
        )

        server_badge_color = (
            "lightgrey" if total_servers == 0 else
            "brightgreen" if available_servers == total_servers else
            "red" if available_servers == 0 else
            "orange"
        )

        server_text = "\n".join(
            f"| {server['url']} | {server['hosted']} | {str(server['available'])} |"
            for server in servers
        )

        # route info
        routes = chars["routes"]
        total_paths = len(set(route["path"] for route in chars["routes"]))

        methods_text = "\n".join(
            f"| `{method.upper()}` | {sum(route['method'] == method for route in routes)} |"
            for method in HTTP_METHODS
        )

        # other info
        rate_limit = chars["rate-limit"]
        rate_limit_text = f"{str(rate_limit['active'])} ({rate_limit['reason']})"
        authentication = ", ".join(chars["authentication"] or []) or "No authentication required"
        query_parameters = len(chars["query-parameters"])

        # badges
        badges = "\n".join([
            generate_badge("oas version", f"{oas['family']} v{oas['version']}", oas_version_badge_color),
            generate_badge("openapi-spec-validator", str(oas["validated"]), oas_validity_badge_color),
            generate_badge("available servers", f"{available_servers} of {total_servers}", server_badge_color),
        ])

        # markdown render
        markdown = f"""
# Structural Characteristics of {api_id} ({chars["title"]})

*Last update: {date}*

{badges}

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API and (2) server reachability. While the repository is often updated, the information might not be up-to-date with official API sources.

## Usage Information

**Servers:**

| URL | Hosted | Available |
| --- | ------ | --------- |
{server_text}

**Authentication Methods:** {authentication}

**Rate Limiting:** {rate_limit_text}

## Structural Information

**Total Paths:** {total_paths}

**Query Parameters:** {query_parameters}

**Paths by Method:**

| Method | Paths |
| ------ | ----- |
{methods_text}
"""

        out_path = APIS_PATH / api_id / "README.md"
        with open(out_path, "w", encoding="utf-8") as file:
            file.write(markdown)

        print(f"Saved {api_id} README to {out_path}")


def update_api_status() -> None:
    """
    Updates the benchmark status, and displays benchmark badges in the main README.
    """

    date = datetime.now().strftime("%Y-%m-%d")

    if not CHAR_PATH.is_file():
        print("No API characteristics found, generating them first")
        generate_api_characteristics()

    with open(CHAR_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    unreachable = []
    outdated = []
    invalid = []

    total_oas = len(data)
    total_servers = 0
    available_servers = 0
    up_to_date_oas = 0
    valid_oas = 0

    for api_id, chars in data.items():
        # unreachable
        for server in chars["servers"]:
            total_servers += 1

            if server["hosted"] == "local" or server["available"]:
                available_servers += 1
            else:
                unreachable.append(f"`{api_id}` (`{server['url']}`)")

        # outdated
        if chars["oas"]["family"] == "openapi":
            up_to_date_oas += 1
        else:
            outdated.append(f"`{api_id}` (`{chars['oas']['family']} v{chars['oas']['version']}`)")

        # invalid
        if not chars["oas"]["validated"]:
            invalid.append(f"`{api_id}` (`{chars['oas']['error']}`)")
        else:
            valid_oas += 1

    # STATUS.md generation
    status_text = f"# Benchmark Status\n\n*Last update: {date}*\n"

    sections = [
        ("Unreachable Servers", unreachable, "- All servers are reachable."),
        ("Outdated OAS Formats", outdated, "- No OAS file is outdated."),
        ("OAS Validation Fails (with `openapi-spec-validator`)", invalid, "- All OAS files passed validation."),
    ]

    for title, items, empty_message in sections:
        status_text += f"\n## {title}\n"

        if items:
            status_text += "".join(f"- {item}\n" for item in items)
        else:
            status_text += f"{empty_message}\n"

    with open(STATUS_PATH, "w", encoding="utf-8") as file:
        file.write(status_text)

    print(f"Saved benchmark status to {STATUS_PATH}")

    # README.md badges
    servers_pct = round(100 * available_servers / total_servers) if total_servers else 0
    up_to_date_pct = round(100 * up_to_date_oas / total_oas) if total_oas else 0
    valid_oas_pct = round(100 * valid_oas / total_oas) if total_oas else 0

    with open(README_PATH, "r", encoding="utf-8") as file:
        readme_text = file.read()

    apis_badge = generate_badge("apis", str(total_oas), "blue")
    servers_badge = generate_badge("reachable servers", f"{servers_pct}%", get_percentage_color(servers_pct))
    up_to_date_badge = generate_badge("openapi v3", f"{up_to_date_pct}%", get_percentage_color(up_to_date_pct))
    valid_oas_badge = generate_badge("openapi-spec-validator", f"{valid_oas_pct}%", get_percentage_color(valid_oas_pct))

    badges = f"{apis_badge} {servers_badge} {up_to_date_badge} {valid_oas_badge}"

    # if the first line of the README is already a badge section, replace it, otherwise add a new line
    lines = readme_text.splitlines()

    if lines and "img.shields.io" in lines[0]:
        lines[0] = badges
        readme_text = "\n".join(lines) + "\n"
    else:
        readme_text = f"{badges}\n\n{readme_text}"

    with open(README_PATH, "w", encoding="utf-8") as file:
        file.write(readme_text)

    print(f"Saved benchmark status badges to {README_PATH}")


def generate_badge(label: str, message: str, color: str) -> str:
    """
    Generates a shields.io badge in Markdown format.

    Args:
        label: Left side of the badge.
        message: Right side of the badge.
        color: Color of the right side of the badge.

    Returns:
        Markdown of the badge.
    """

    label = label.replace("-", "--").replace(" ", "_").replace("%", "%25")
    message = message.replace("-", "--").replace(" ", "_").replace("%", "%25")

    return f"![alt text](https://img.shields.io/badge/{label}-{message}-{color}.svg)"


def get_percentage_color(percentage: float) -> str:
    """
    Picks a color based on a percentage value.

    Args:
        percentage: Percentage value between 0 and 100.

    Returns:
        Percentage color.
    """

    if percentage == 100:
        return "brightgreen"
    elif percentage >= 75:
        return "yellowgreen"
    elif percentage >= 50:
        return "orange"
    else:
        return "red"


def build_parser() -> argparse.ArgumentParser:
    """
    Builds the argv parser.
    """

    parser = argparse.ArgumentParser(description="CLI for PRAB.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # update parser
    update_parser = subparsers.add_parser("update", help="Updates APIs by generating their characteristics, READMEs, and global status.")

    return parser


def main(argv: list[str] | None = None) -> None:
    """
    Entry point of the command line interface.

    Args:
        argv: Command line arguments.
    """

    args = build_parser().parse_args(argv)

    if args.command == "update":
        generate_api_characteristics()
        update_api_readmes()
        update_api_status()


if __name__ == "__main__":
    main()
