![alt text](https://img.shields.io/badge/apis-60-blue.svg) ![alt text](https://img.shields.io/badge/reachable_servers-100%25-brightgreen.svg) ![alt text](https://img.shields.io/badge/openapi_v3-100%25-brightgreen.svg) ![alt text](https://img.shields.io/badge/openapi--spec--validator-100%25-brightgreen.svg)

# PRAB: Public REST API Benchmark

This GitHub repository contains a Public REST API Benchmark (PRAB). The benchmark contains the OpenAPI Specification (OAS), Postman Collection (when applicable), and various structural characteristics (HTTP method distribution, authentication method, routes and query parameters, etc.) of publicly available REST APIs. It is aimed to be used by researchers, testers, developers, and users alike, to support work in the REST API domain and its literature. For instance, a new testing tool can leverage the OpenAPI Specifications provided in this repository.

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

## Content

PRAB contains the following:

- `apis/`: Folder containing all APIs of the benchmark. Each API has a sub-folder, containing a global overview in `README.md`, an OpenAPI Specification (OAS) in `<api-name>-openapi.json`, and optionally a Postman Collection or other useful files.
- `legacy/`: Folder containing legacy content (cf. **Legacy** section for more details).
- `characteristics.json`: File containing the structural characteristics of the APIs.
- `sources.json` (WIP): File containing the source URLs for the benchmark specifications.
- `cli.py`: File containing the main Python code for the CLI.
- `utils.py`: File containing utility code for the CLI.
- `requirements.txt`: File containing the Python requirements for the CLI.
- `STATUS.md`: File containing the latest status of the benchmark. It is separated into different sections: **Unreachable Servers**, **Outdated OAS Formats**, and **OAS Validation Fails**. This content is useful to check for outdated APIs and to update them accordingly.

Work in progress:

- [x] CLI
- [ ] CLI advanced filtering
- [ ] API pricing information
- [ ] API sources

## CLI Setup

The CLI uses Python v3.10 or later. To set it up, enter the following commands in a terminal at the root of the repository:

1. Create a Python virtual environment:

    ```
    python -m venv .venv
    ```

2. Activate the virtual environment, depending on your operating system:

    - Linux / macOS (Bash or Zsh): `source .venv/bin/activate`
    - Windows (Command Prompt): `.venv\Scripts\activate.bat`
    - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
    - Windows (Git Bash): `source .venv/Scripts/activate`

3. Install the dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Use the CLI:

    ```
    python cli.py <commands>
    ```

    To list available CLI commands, you may use `python cli.py --help`.

5. Example:

    For instance, if you add a new API folder in `apis/my-api/` containing `my-api-openapi.json`, you can generate its README and update the benchmark status with:

    ```
    python cli.py update --only my-api
    ```

    Or, if you want to update all APIs contained in `apis/`:

    ```
    python cli.py update
    ```

    You can also filter APIs based on criteria:

    ```
    python cli.py filter --hosted local
    ```

## Actionable Insights and Guidance on Using the Benchmark

The main outcome of this research is our benchmark backed by a systematic mapping study. Our goal was not to evaluate the design quality of REST APIs but to provide an unbiased and comprehensive benchmark containing documentation and structural characteristics of public REST APIs. The benchmark is aimed to be used by users, testers, and researchers in their evaluations. We cannot assert that a certain API is *better* compared to another API in the benchmark. Indeed, as REST is not a standard but rather an architectural style, there are multiple ways to implement a REST API. As a result, the structure of a REST API can drastically change from one API to another API. For instance, an API could contain a single GET route with various usable query parameters (e.g., a `/users` route with the query parameters `id`, `name`, `age`). On the other hand, an API could contain a lot of different specialized GET routes without any query parameters (e.g., the routes `/user/{id}`, `/user/{name}`, `/user/{age}`).

Moreover, REST APIs utilize different HTTP methods depending on their application domain. For instance, APIs specialized in retrieving data (e.g., a weather API to retrieve the current weather, precipitation index, or weekly forecast) would contain various routes with the GET HTTP method. Other APIs specialized in sending data (e.g., a booking API to book a hotel room, order food, or send a payment) would contain various routes with the POST HTTP method. Similarly, update-heavy APIs would utilize the PATCH (modify parts of a resource) and PUT (create or replace a resource) HTTP methods.

Therefore, we leave the selection of APIs up to the benchmark users but provide concrete metrics to support evidence-based API selection. For instance, a tool for REST API security testing might require the evaluation of APIs that allow data to be sent to the server (i.e., with the POST HTTP method). The evaluation of such a tool would utilize a subset of our benchmark, comprising APIs with a high distribution of POST methods. Consequently, the structural characteristics provided in our benchmark enable researchers to filter the APIs they find relevant (i.e., that match specific experimental needs).

For research involving source code analysis, we include URLs for downloading (local) or using (online) the REST APIs. Our quality criteria excluded non-deployable APIs. Fuzzing research also cares about request rate limits, pricing, and authentication mechanisms, which we also include. Finally, we provide up-to-date documentation in both OpenAPI/Postman formats, which testing tools can leverage. We did not include API source code in our benchmark but rather reference it via respective URLs (GitHub repositories, website downloads, etc.).

## Legacy

The repository also contains a `legacy/` folder with the initial evaluation data of the benchmark (as reported in our research paper), and APIs that were retired from the benchmark:

- `apis/`: APIs that were part of the benchmark but were retired (i.e., moved out of `/apis`), kept for reproducibility. An API is retired when it becomes unusable for the benchmark (e.g., its servers are permanently unreachable and it cannot be deployed locally). Each retired API keeps its original folder content (OpenAPI Specification, optional Postman Collection, README with structural characteristics).
- `structural-characteristics.json`: The structural characteristics at the time of the initial evaluation (the current, up-to-date version is `apis/characteristics.json` along with the data in individual API `README.md` files).
- `structural-characteristics-outdated.pdf` and `visualisation/`: The frozen table and visualisations from the paper, kept for reproducibility.
- `study-data/`: The study data associated with the research paper. You can find the following files:
    - `found-papers.md`: Contains the research papers that were found with our search string, in our systematic mapping study.
    - `selected-papers.md`: Contains the research papers that were accepted in our systematic mapping study.
    - `study-apis.md`: Contains the REST APIs that were found in the research papers (from `selected-papers.md`).
