
# Structural Characteristics of marvel (None)

*Last update: 2026-11-17*

![alt text](https://img.shields.io/badge/oas_version-unknown_vNone-orange.svg)
![alt text](https://img.shields.io/badge/openapi--spec--validator-False-red.svg)
![alt text](https://img.shields.io/badge/available_servers-0_of_0-lightgrey.svg)

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API and (2) server reachability. While the repository is often updated, the information might not be up-to-date with official API sources.

## Why is this API in Legacy?

This API was part of the benchmark until November 2026, when it was retired (i.e., moved from `/apis` to `/legacy/apis`) because it became unusable for the benchmark:

- The specification in `marvel-openapi.json` is not an OpenAPI or Swagger document: it is a pre-Swagger "swaggerVersion 1.0" document (the old Wordnik API Designer format, with top-level `apis` and `models` arrays) that no OAS tool or validator can parse (the CLI reports OAS family `unknown` with a `ValidatorDetectError`, and extracts 0 routes and 0 servers).
- The upstream API is dead. Every path of `https://gateway.marvel.com` (including `/v1/public/*`) returns HTTP 500 ("Internal server error"), the documentation endpoint that served the original document (`https://gateway.marvel.com/docs/public`) is down as well, and the developer portal (`https://developer.marvel.com`) now redirects to `https://www.marvel.com`, so the specification cannot be recovered or rebuilt from upstream.

The folder is kept, frozen, for reproducibility: the original document and the structural characteristics below remain useful for research based on API documentation rather than live calls (e.g., specification mining or testing tools against archived data).

## Usage Information

**Servers:**

| URL | Hosted | Available |
| --- | ------ | --------- |


**Authentication Methods:** No authentication required

**Rate Limiting:** False (no 429 status code response or rate limiting headers)

## Structural Information

**Total Paths:** 0

**Query Parameters:** 0

**Paths by Method:**

| Method | Paths |
| ------ | ----- |
| `GET` | 0 |
| `POST` | 0 |
| `PUT` | 0 |
| `PATCH` | 0 |
| `DELETE` | 0 |
| `HEAD` | 0 |
| `OPTIONS` | 0 |
| `TRACE` | 0 |
