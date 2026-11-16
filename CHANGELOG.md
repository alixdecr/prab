# Changelogs

The APIs of the benchmark are checked and updated on a monthly basis with `python cli.py update`.
Each entry reports unreachable servers, outdated API documentation formats (Swagger), and OAS validation failures. The most recent checks come first.

## 2026-11-16

- **Unreachable servers:**
    - `amadeus-hotel (https://test.api.amadeus.com)`
    - `dhl-shipment-tracking (https://api-test.dhl.com/track)`
    - `fdic (/api)`
    - `foursquare (500x500)`
    - `kafka-rest-proxy ({protocol}://{address}:{port}/v3)`
    - `kafka-rest-proxy ({protocol}://{address}:{port}/kafka/v3)`
    - `kafka-rest-proxy (https://pkc-00000.region.provider.confluent.cloud/kafka/v3)`
    - `realworld-app (https://api.realworld.io/api)`
    - `senzing ({protocol}://{host}:{port}{path})`
    - `spacex-api (https://api.spacexdata.com)`
    - `ur-codebin (http://urcodebin.live)`

- **Outdated OAS formats:**
    - `bing-web-search (swagger v2.0)`
    - `catwatch (swagger v2.0)`
    - `cyclotron (swagger v2.0)`
    - `digdag (swagger v2.0)`
    - `features-service (swagger v2.0)`
    - `genome-nexus (swagger v2.0)`
    - `gestao-hospital (swagger v2.0)`
    - `languagetool (swagger v2.0)`
    - `ocvn (swagger v2.0)`
    - `ohsome (swagger v2.0)`
    - `omdb (swagger v2.0)`
    - `proxyprint (swagger v2.0)`
    - `refuge-restrooms (swagger v2.0)`
    - `rest-ncs (swagger v2.0)`
    - `rest-news (swagger v2.0)`
    - `rest-scs (swagger v2.0)`
    - `scout-api (swagger v2.0)`

- **OAS validation fails:**
    - `catwatch (OpenAPIValidationError)`
    - `cwa-verification-server (OpenAPIValidationError)`
    - `cyclotron (OpenAPIValidationError)`
    - `dhl-shipment-tracking (OpenAPIValidationError)`
    - `digdag (OpenAPIValidationError)`
    - `disease-sh (OpenAPIValidationError)`
    - `fdic (Unresolvable)`
    - `features-service (OpenAPIValidationError)`
    - `gbif-species (OpenAPIValidationError)`
    - `genome-nexus (OpenAPIValidationError)`
    - `graphhopper (OpenAPIValidationError)`
    - `marvel (ValidatorDetectError)`
    - `ocvn (PointerToNowhere)`
    - `proxyprint (OpenAPIValidationError)`
    - `rest-ncs (OpenAPIValidationError)`
    - `rest-news (OpenAPIValidationError)`
    - `scout-api (OpenAPIValidationError)`
    - `senzing (OpenAPIValidationError)`
    - `ur-codebin (OpenAPIValidationError)`
    - `yelp (OpenAPIValidationError)`

## 2026-11 MAJOR UPDATE

- Added a new CLI (`cli.py`) to update the tool, which can be used with the `python cli.py` command (`--help` for all sub-commands and parameters).
- API filtering has been removed (for now) and is currently being integrated into the new CLI.
- Moved the initial evaluation data and old structural characteristics into the `legacy/` folder, as the current state of the APIs diverge from it.
- New `README.md` structure for all APIs.
- New monthly check, no changes.

## 2026-10

- Server URLs became unreachable: `amadeus-hotel`, `dhl-shipment-tracking`.
- Server URL reachable again: `open-brewery-db` (unreachable since 2026-07).

## 2026-07

- Server URL became unreachable: `open-brewery-db`.

## 2026-05

- No changes.

## 2026-03

- No changes.

## 2025-12

- No changes.

## 2025-10

- No changes.

## 2025-09

- No changes, first monthly check.
