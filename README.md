# PRAB: Public REST API Benchmark

![alt text](https://img.shields.io/badge/Benchmark_Contains-62_REST_APIs-blue.svg)

This GitHub repository contains a Public REST API Benchmark (PRAB). The benchmark contains the OpenAPI Specification (OAS), Postman Collection (when applicable), and various structural characteristics (HTTP method distribution, authentication method, routes and query parameters, etc.) of over 60 publicly available REST APIs. It is aimed to be used by researchers, testers, developers, and users alike, to assist in the REST API domain/literature. For instance, a new testing tool can leverage the OpenAPI Specifications provided in this repository.

The repository was created by [Alix Decrop](https://orcid.org/0009-0007-2641-5983) and [Sara Eraso](https://orcid.org/0009-0002-7637-3869).

## Citation

If you use this tool in your research or find it useful in your work, please cite our paper:

Decrop, A., Eraso, S., Devroey, X. and Perrouin, G., 2025. A Public Benchmark of REST APIs. In 2025 IEEE/ACM 22nd International Conference on Mining Software Repositories (MSR) (pp. 421-433). IEEE.

```bibtex
@inproceedings{decrop2025public,
    title={A Public Benchmark of REST APIs},
    author={Decrop, Alix and Eraso, Sara and Devroey, Xavier and Perrouin, Gilles},
    booktitle={2025 IEEE/ACM 22nd International Conference on Mining Software Repositories (MSR)},
    pages={421--433},
    year={2025},
    organization={IEEE}
}
```

## Changelog

The APIs of the benchmark are checked and updated on a monthly basis:

- **2026-11 MAJOR UPDATE**:
    - Added a new CLI (`cli.py`) to update the tool, which can be used with the `python cli.py` command (`--help` for all sub-commands and parameters).
    - API filtering has been removed (for now) and is currently being integrated into the new CLI.
    - Moved the initial evaluation data and old structural characteristics into the `legacy/` folder, as the current state of the APIs diverge from it.
    - New `README.md` structure for all APIs.
    - New monthly check, no changes.
- **2026-10**:
    - Server URLs became unreachable: `amadeus-hotel`, `dhl-shipment-tracking`.
    - Server URL reachable again: `open-brewery-db` (unreachable since 2026-07).
- **2026-07**:
    - Server URL became unreachable: `open-brewery-db`.
- **2026-05**: No changes.
- **2026-03**: No changes.
- **2025-12**: No changes.
- **2025-10**: No changes.
- **2025-09**: No changes, first monthly check.

## Getting Started

The main content of the benchmark can be found in the `/apis` folder. At the moment, each REST API of the benchmark has its sub-folder, containing a README with its structural characteristics and, when available, an OpenAPI Specification (in the JSON format). Certain APIs also have an available Postman Collection.

The structural characteristics of all benchmark APIs are available in machine-readable format in `apis/characteristics.json`, represented by an API identifier (the name of the folder in `/apis`). This enables the selection of the APIs that match experimental needs. The OpenAPI Specifications themselves can then be loaded (where available) from `/apis/<identifier>/<identifier>-openapi.json` (do not forget `encoding="utf-8-sig"`, see `/apis/README.md`).

## Additional Content

The repository also contains a `legacy/` folder with the initial evaluation data of the benchmark (as reported in our research paper):

- `structural-characteristics.json`: The structural characteristics at the time of the initial evaluation (the current, up-to-date version is `apis/characteristics.json` along with the data in individual API `README.md` files).
- `structural-characteristics-outdated.pdf` and `visualisation/`: The frozen table and visualisations from the paper, kept for reproducibility.
- `study-data/`: The study data associated with the research paper. You can find the following files:
    - `found-papers.md`: Contains the research papers that were found with our search string, in our systematic mapping study.
    - `selected-papers.md`: Contains the research papers that were accepted in our systematic mapping study.
    - `study-apis.md`: Contains the REST APIs that were found in the research papers (from `selected-papers.md`).
 
## Actionable Insights and Guidance on Using the Benchmark

The main outcome of this research is our benchmark backed by a systematic mapping study. Our goal was not to evaluate the design quality of REST APIs but to provide an unbiased and comprehensive benchmark containing documentation and structural characteristics of over 60 public REST APIs. The benchmark is aimed to be used by users, testers, and researchers in their evaluations. We cannot assert that a certain API is *better* compared to another API in the benchmark. Indeed, as REST is not a standard but rather an architectural style, there are multiple ways to implement a REST API. Indeed, the structure of a REST API can drastically change from one API to another API. For instance, an API could contain a single GET route with various usable query parameters (e.g., a `/users` route with the query parameters `id`, `name`, `age`). On the other hand, an API could contain a lot of different specialized GET routes without any query parameters (e.g., the routes `/user/{id}`, `/user/{name}`, `/user/{age}`).

Moreover, REST APIs utilize different HTTP methods depending on their application domain. For instance, APIs specialized in retrieving data (e.g., a weather API to retrieve the current weather, precipitation index, or weekly forecast) would contain various routes with the GET HTTP method. Other APIs specialized in sending data (e.g., a booking API to book a hotel room, order food, or send a payment) would contain various routes with the POST HTTP method. Similarly, update-heavy APIs would utilize the PATCH (modify parts of a resource) and PUT (create or replace a resource) HTTP methods.

Therefore, we leave the selection of APIs up to the benchmark users but provide concrete metrics to support evidence-based API selection. For instance, a tool for REST API security testing might require the evaluation of APIs that allow data to be sent to the server (i.e., with the POST HTTP method). The evaluation of such a tool would utilize a subset of our benchmark, comprising APIs with a high distribution of POST methods. In consequence, the structural characteristics provided in our benchmark enable researchers to filter the APIs they find relevant (i.e., that match specific experimental needs), without the necessity to utilize all 62 APIs.

For research implying source code analysis, we include URLs for downloading (local) or using (online) the REST APIs. Our quality criteria excluded non-deployable APIs. Fuzzing research also cares about request rate limits, pricing, and authentication mechanisms, which we also include. Finally, we provide up-to-date documentation in both OpenAPI/Postman formats, which testing tools can leverage. We did not include API source code in our benchmark but rather reference it via respective URLs (GitHub repositories, website downloads, etc.).