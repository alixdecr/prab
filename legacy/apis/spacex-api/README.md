# Structural Characteristics of spacex-api (r/SpaceX API V4)

*Last update: 2026-11-16*

![alt text](https://img.shields.io/badge/oas_version-openapi_v3.0.0-brightgreen.svg)
![alt text](https://img.shields.io/badge/openapi--spec--validator-valid-brightgreen.svg)
![alt text](https://img.shields.io/badge/available_servers-0_of_1-red.svg)

**Disclaimer:** All information provided is based on an analysis of (1) the content provided in the OAS file of the API and (2) server reachability. While the repository is often updated, the information might not be up-to-date with official API sources.

## Why is this API in Legacy?

This API was part of the benchmark until November 2026, when it was retired (i.e., moved from `/apis` to `/legacy/apis`) because it became unusable for the benchmark:

- The upstream host `https://api.spacexdata.com` is shut down. Its domain still resolves (to a CDN front), but requests time out, and no path of the API (`/v3/*`, `/v4/*`) answers anymore.
- The upstream project ([`r-spacex/SpaceX-API`](https://github.com/r-spacex/SpaceX-API)) was archived on GitHub (June 2026), and its data export and self-hosting instructions (Docker) were removed, so the API cannot be deployed locally either.

The folder is kept, frozen, for reproducibility: the OpenAPI Specification, Postman Collection, and the structural characteristics below remain useful for research based on API documentation rather than live calls (e.g., specification mining or testing tools against archived data).

## Usage Information

**Servers:**

| URL | Hosted | Availability |
| --- | ------ | ------------ |
| https://api.spacexdata.com | online | not available |

**Authentication Methods:** apikeyAuth

**Rate Limiting:** no

## Structural Information

**Total Paths:** 41

**Query Parameters:** 0

**Paths by Method:**

| Method | Paths |
| ------ | ----- |
| `GET` | 29 |
| `POST` | 21 |
| `PUT` | 0 |
| `PATCH` | 13 |
| `DELETE` | 11 |
| `HEAD` | 0 |
| `OPTIONS` | 0 |
| `TRACE` | 0 |

