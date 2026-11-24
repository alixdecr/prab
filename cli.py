import argparse
import utils
from datetime import datetime, timezone
from jsonref import replace_refs
from typing import cast
from openapi_spec_validator import validate
from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent
APIS_PATH = ROOT_PATH / "apis"
CHAR_PATH = ROOT_PATH / "characteristics.json"
SOURCES_PATH = ROOT_PATH / "sources.json"
STATUS_PATH = ROOT_PATH / "STATUS.md"
README_PATH = ROOT_PATH / "README.md"
HTTP_METHODS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")


def generate_api_characteristics(only: list[str] | None = None) -> None:
    """
    Generates structural characteristics of provided APIs (paths of OAS files).

    Args:
        only: If set, only generate characteristics for the specified API ids (keep the other characteristics entries as is if existing).
    """

    # load existing characteristics if they exist
    characteristics = {}

    if only and CHAR_PATH.is_file():
        characteristics = utils.load_json(CHAR_PATH)

    # one OAS file is analyzed per API: an openapi file if the folder has one, otherwise a swagger file
    paths = []

    for folder in sorted(APIS_PATH.iterdir()):
        if not folder.is_dir():
            continue

        openapi_paths = sorted(folder.glob("*openapi*"))

        if openapi_paths:
            candidates = [path for path in openapi_paths if path.suffix.lower() == ".json"]
        else:
            candidates = [path for path in sorted(folder.glob("*swagger*")) if path.suffix.lower() == ".json"]

        if not candidates:
            continue

        if len(candidates) > 1:
            print(f"{folder.name} has multiple OAS files, will analyze only {candidates[0].name}")

        paths.append(candidates[0])

    for path in sorted(paths):
        # api id
        api_id = path.parent.name

        if only and api_id not in only:
            continue

        print(f"Analyzing {api_id} -> {path.name}")

        # loading
        try:
            spec = utils.load_json(path)
        except Exception as e:
            print(f"- Failed to load specification ({type(e).__name__})")
            spec = {}

        # oas validation
        try:
            validate(spec)
            oas = {"validated": True, "error": None}
        except Exception as e:
            error_name = type(e).__name__
            oas = {"validated": False, "error": error_name}
            print(f"- Failed to validate specification ({error_name})")

        # json dereferencing
        try:
            spec = cast(dict, replace_refs(spec, proxies=False, loader=lambda uri: {}))
        except Exception as e:
            print(f"- Failed to dereference json ({type(e).__name__})")

        # oas version
        if spec.get("openapi"):
            family = "openapi"
        elif spec.get("swagger"):
            family = "swagger"
            print(f"- Deprecated documentation format: swagger")
        else:
            family = "unknown"
            print("- Unknown documentation format")

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

            result = utils.check_server(url)
            servers.append(result)

            if not result["available"]:
                print(f"- Server {url} is not available")

        # authentication
        authentication = list(spec.get("components", {}).get("securitySchemes", {}) or spec.get("securityDefinitions", {})) or None

        # rate limiting, routes, and query parameters
        rate_limit = {"active": False, "reason": "no 429 status code response or rate limiting headers"}
        routes = []
        query_parameters = set()

        for route_path, path_item in spec.get("paths", {}).items():
            if not isinstance(path_item, dict):
                continue

            for param in path_item.get("parameters", []):
                if param.get("in", "") == "query" and param.get("name"):
                    query_parameters.add(param.get("name"))

            for method, method_item in path_item.items():
                if method not in HTTP_METHODS or not isinstance(method_item, dict):
                    continue

                routes.append({"method": method, "path": route_path})

                for param in method_item.get("parameters", []):
                    if param.get("in", "") == "query" and param.get("name"):
                        query_parameters.add(param.get("name"))

                for status_code, response in method_item.get("responses", {}).items():
                    if status_code == "429":
                        rate_limit = {"active": True, "reason": "presence of 429 status code response"}

                    if isinstance(response, dict):
                        for header in response.get("headers", {}):
                            name = header.lower()
                            if "ratelimit" in name or "retry-after" in name:
                                rate_limit = {"active": True, "reason": "presence of rate limiting headers"}

        characteristics[api_id] = {
            "title": title,
            "oas": oas,
            "servers": servers,
            "authentication": authentication,
            "rate-limit": rate_limit,
            "routes": routes,
            "query-parameters": sorted(query_parameters)
        }

    utils.save_json(CHAR_PATH, characteristics)
    print(f"Saved API characteristics to {CHAR_PATH}")


def update_api_readmes(date: str, only: list[str] | None = None) -> None:
    """
    Updates API READMEs.

    Args:
        date: YYYY-MM-DD date string of the update.
        only: If set, only update the READMEs of the specified API ids.
    """

    data = utils.load_json(CHAR_PATH)
    sources = utils.load_json(SOURCES_PATH)

    for api_id, chars in data.items():
        if only and api_id not in only:
            continue

        # oas info
        oas = chars["oas"]
        oas_version_badge_color = "brightgreen" if oas["family"] == "openapi" else "orange"
        oas_validity_badge_color = "brightgreen" if oas["validated"] else "red"
        oas_validity_text = "pass" if oas["validated"] else "fail"

        # server info
        servers = chars["servers"]
        total_servers = len(servers)
        available_servers = sum(utils.is_server_available(server) for server in servers)

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
        total_paths = len(set(route["path"] for route in routes))

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
            utils.generate_badge("oas version", f"{oas['family']} v{oas['version']}", oas_version_badge_color),
            utils.generate_badge("openapi-spec-validator", oas_validity_text, oas_validity_badge_color),
            utils.generate_badge("available servers", f"{available_servers} of {total_servers}", server_badge_color),
        ])

        # official info from sources.json
        source = sources.get(api_id, {})
        availability_source = source.get("availability", {})
        authentication_source = source.get("authentication", {})
        rate_limit_source = source.get("rate-limit", {})
        pricing = source.get("pricing", {})

        # official documentation urls as markdown links
        doc_url = source.get("doc")
        documentation_url = f"[{doc_url}]({doc_url})" if doc_url else "Unknown"

        oas_url_source = source.get("oas")
        oas_url = f"[{oas_url_source}]({oas_url_source})" if oas_url_source else "Unknown"

        code_url_source = availability_source.get("code")
        code_url = f"[{code_url_source}]({code_url_source})" if code_url_source else "Unknown"

        availability_official = str(availability_source.get("type", "Unknown"))
        official_servers = ", ".join(f"`{url}`" for url in availability_source.get("servers", [])) or "Unknown"

        # official authentication
        authentication_official = str(authentication_source.get("required", "Unknown"))

        if authentication_source.get("source"):
            authentication_official += f" ([source]({authentication_source['source']}))"

        # official rate limit, with the quota if provided
        required = rate_limit_source.get("required", "Unknown")
        quota = rate_limit_source.get("quota") or {}

        if quota.get("value") is not None:
            required = f"{required} (quota: {quota['value']} per {quota.get('per')})"

        rate_limit_official = str(required)

        if rate_limit_source.get("source"):
            rate_limit_official += f" ([source]({rate_limit_source['source']}))"

        # official pricing
        pricing_official = str(pricing.get("type", "Unknown"))

        if pricing.get("source"):
            pricing_official += f" ([source]({pricing['source']}))"

        # markdown render
        markdown = f"""
# Structural Characteristics of {api_id} ({chars["title"]})

*Last update: {date}*

{badges}

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API, (2) server reachability, and (3) official API URLs. While the repository is often updated, the information might not be up-to-date with official API sources.

**Documentation URL:** {documentation_url}

**OAS File URL:** {oas_url}

## Availability

**Official Availability:** {availability_official}

**Official Servers:** {official_servers}

**Source Code URL:** {code_url}

## Servers

| URL | Hosted | Available |
| --- | ------ | --------- |
{server_text}

## Authentication

**Documented:** {authentication}

**Official:** {authentication_official}

## Rate Limiting

**Documented:** {rate_limit_text}

**Official:** {rate_limit_official}

## Pricing

**Official:** {pricing_official}

## Structure

**Total Paths:** {total_paths}

**Query Parameters:** {query_parameters}

**Paths by Method:**

| Method | Paths |
| ------ | ----- |
{methods_text}
"""

        out_path = APIS_PATH / api_id / "README.md"
        utils.save_text(out_path, markdown)
        print(f"Saved {api_id} README to {out_path}")


def update_api_status(date: str) -> None:
    """
    Updates the benchmark status, and displays benchmark badges in the main README.

    Args:
        date: YYYY-MM-DD date string of the update.
    """

    data = utils.load_json(CHAR_PATH)

    # unreachable servers
    servers = [(api_id, server) for api_id, chars in data.items() for server in chars["servers"]]
    total_servers = len(servers)
    available_servers = sum(utils.is_server_available(server) for _, server in servers)
    unreachable = [f"`{api_id}` (`{server['url']}`)" for api_id, server in servers if not utils.is_server_available(server)]

    # outdated and invalid OAS files
    outdated = [f"`{api_id}` (`{chars['oas']['family']} v{chars['oas']['version']}`)" for api_id, chars in data.items() if chars["oas"]["family"] != "openapi"]
    invalid = [f"`{api_id}` (`{chars['oas']['error']}`)" for api_id, chars in data.items() if not chars["oas"]["validated"]]

    # STATUS.md
    status_text = f"# Benchmark Status\n\n*Last update: {date}*\n"

    sections = [
        ("Unreachable Servers", unreachable, "- All servers are reachable. Local servers are flagged as reachable by default."),
        ("Outdated OAS Formats", outdated, "- No OAS file is outdated."),
        ("OAS Validation Fails (with `openapi-spec-validator`)", invalid, "- All OAS files passed validation."),
    ]

    for title, items, empty_message in sections:
        status_text += f"\n## {title}\n"

        if items:
            status_text += "".join(f"- {item}\n" for item in items)
        else:
            status_text += f"{empty_message}\n"

    utils.save_text(STATUS_PATH, status_text)
    print(f"Saved benchmark status to {STATUS_PATH}")

    # README.md
    readme_text = utils.load_text(README_PATH)

    # badges
    total_oas = len(data)
    servers_pct = round(100 * available_servers / total_servers) if total_servers else 0
    up_to_date_pct = round(100 * (total_oas - len(outdated)) / total_oas) if total_oas else 0
    valid_oas_pct = round(100 * (total_oas - len(invalid)) / total_oas) if total_oas else 0

    apis_badge = utils.generate_badge("apis", str(total_oas), "blue")
    servers_badge = utils.generate_badge("reachable servers", f"{servers_pct}%", utils.get_percentage_color(servers_pct))
    up_to_date_badge = utils.generate_badge("openapi v3", f"{up_to_date_pct}%", utils.get_percentage_color(up_to_date_pct))
    valid_oas_badge = utils.generate_badge("openapi-spec-validator", f"{valid_oas_pct}%", utils.get_percentage_color(valid_oas_pct))
    badges = f"{apis_badge} {servers_badge} {up_to_date_badge} {valid_oas_badge}"

    # if the first line of the README is already a badge section, replace it, otherwise add a new line
    lines = readme_text.splitlines()

    if lines and "img.shields.io" in lines[0]:
        lines[0] = badges
        readme_text = "\n".join(lines) + "\n"
    else:
        readme_text = f"{badges}\n\n{readme_text}"

    utils.save_text(README_PATH, readme_text)
    print(f"Saved benchmark status badges to {README_PATH}")


def filter_apis(criteria: dict) -> None:
    """
    Filters APIs based on the provided criteria and prints the matching API ids.

    Args:
        criteria: Dict of criteria.
    """

    print(f"Filtering APIs with the following criteria: {criteria}")

    data = utils.load_json(CHAR_PATH)
    sources = utils.load_json(SOURCES_PATH)
    matches = []

    for api_id, chars in data.items():

        can_add = True

        if criteria.get("hosted"):
            can_add &= any(server["hosted"] == criteria["hosted"] for server in chars["servers"])

        if criteria.get("no_auth"):
            can_add &= chars["authentication"] is None and not sources[api_id]["authentication"]["required"]

        if criteria.get("no_limit"):
            can_add &= not chars["rate-limit"]["active"] and not sources[api_id]["rate-limit"]["required"]

        if criteria.get("no_pricing"):
            can_add &= sources[api_id]["pricing"]["type"] == "free"

        # "is not None" allows 0 as a valid filter value for min or max
        if criteria.get("min_routes") is not None:
            can_add &= len(chars["routes"]) >= criteria["min_routes"]

        if criteria.get("max_routes") is not None:
            can_add &= len(chars["routes"]) <= criteria["max_routes"]

        if criteria.get("min_params") is not None:
            can_add &= len(chars["query-parameters"]) >= criteria["min_params"]

        if criteria.get("max_params") is not None:
            can_add &= len(chars["query-parameters"]) <= criteria["max_params"]

        if can_add:
            matches.append(api_id)

    print(f"Filtered {len(matches)} APIs:")

    if matches:
        print("\n".join(sorted(matches)))
    else:
        print("No API matches the given filter")


def convert_apis(path: str | None = None, api_ids: list[str] | None = None) -> None:
    """
    Converts YAML files into JSON copies.

    Args:
        path: If set, path of the file to convert.
        api_ids: If set, ids of the APIs whose folder YAML files are converted.
    """

    suffix = "y*ml"
    paths = []

    if path:
        paths.append(Path(path))

    elif api_ids:
        for api_id in api_ids:
            api_paths = sorted((APIS_PATH / api_id).glob(f"*.{suffix}"))

            if not api_paths:
                print(f"No relevant file to convert for {api_id}")

            paths.extend(api_paths)

    for convert_path in paths:
        out_path = utils.convert_yaml_to_json(convert_path)

        if out_path:
            print(f"Created a JSON copy at {out_path}")
        else:
            print(f"Unable to convert {convert_path}")


def build_parser() -> argparse.ArgumentParser:
    """
    Builds the argv parser.
    """

    parser = argparse.ArgumentParser(description="CLI for PRAB.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # update parser
    update_parser = subparsers.add_parser("update", help="Update APIs by generating their characteristics, READMEs, and global status.")
    update_parser.add_argument("-o", "--only", nargs="+", metavar="API_ID", help="Only update the specified APIs.")

    # filter parser
    filter_parser = subparsers.add_parser("filter", help="Filter APIs by specified criteria.")
    filter_parser.add_argument("--hosted", choices=("local", "online"), help="Filter APIs by hosting.")
    filter_parser.add_argument("--no-auth", action="store_true", help="Filter APIs with no authentication.")
    filter_parser.add_argument("--no-limit", action="store_true", help="Filter APIs with no rate limiting.")
    filter_parser.add_argument("--no-pricing", action="store_true", help="Filter APIs with no pricing.")
    filter_parser.add_argument("--min-routes", type=int, metavar="MIN_AMOUNT", help="Filter APIs with a minimum amount of routes (inclusive).")
    filter_parser.add_argument("--max-routes", type=int, metavar="MAX_AMOUNT",help="Filter APIs with a maximum amount of routes (inclusive).")
    filter_parser.add_argument("--min-params", type=int, metavar="MIN_AMOUNT", help="Filter APIs with a minimum amount of query parameters (inclusive).")
    filter_parser.add_argument("--max-params", type=int, metavar="MAX_AMOUNT",help="Filter APIs with a maximum amount of query parameters (inclusive).")

    # convert parser
    convert_parser = subparsers.add_parser("convert", help="Convert YAML to JSON.")
    exclusive = convert_parser.add_mutually_exclusive_group(required=True)
    exclusive.add_argument("-p", "--path", help="Path of the file to convert.")
    exclusive.add_argument("-a", "--apis", nargs="+", metavar="API_ID", help="Convert YAML files for the specified APIs.")

    return parser


def main(argv: list[str] | None = None) -> None:
    """
    Entry point of the command line interface.

    Args:
        argv: Command line arguments.
    """

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    args = build_parser().parse_args(argv)

    if args.command == "update":
        generate_api_characteristics(args.only)
        update_api_readmes(date, args.only)
        update_api_status(date)

    elif args.command == "filter":
        filter_apis(vars(args))

    elif args.command == "convert":
        convert_apis(args.path, args.apis)

if __name__ == "__main__":
    main()
