## REST APIs of the Benchmark

### Content

This folder contains all REST APIs of the benchmark. Each API has a folder, containing :

- An OpenAPI Specification, in the JSON format.
- A Postman Collection, in the JSON format (not always available).
- A README document, containing information regarding the REST API.

### Badges

Each API README contains two badges describing the state of the API at the date of the last monthly check (`Last Checked`):

- `OpenAPI Specification` badge:
    - `Valid` (green): The folder contains an OpenAPI Specification that can be parsed and is in the current OpenAPI format.
    - `Oudated` (orange): The folder contains an OpenAPI Specification, but it is in an older format (e.g., Swagger 2.0). A newer specification may be available upstream.
    - `Invalid` (red): No OpenAPI Specification was found in the folder, or the file cannot be parsed as JSON.

- `Server_URL` badge:
    - `Valid` (green): The server URL declared in the specification responded to an HTTP request during the last check.
    - `Invalid` (red): The server URL declared in the specification did not respond to an HTTP request during the last check.
    - `Local` (green): The API is deployed locally (see `Availability`), so its server URL is not checked online.
    - `Missing` (orange): The specification does not declare any server URL.

### Additional Information

- When trying to open the OpenAPI Specifications in Python (`with open(api, "r") as file:`), do not forget to add the parameter `encoding="utf-8-sig"`. This increases the reliability of UTF-8 encoding detection, as some specifications can contain specific characters.