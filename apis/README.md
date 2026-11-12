## REST APIs of the Benchmark

### Content

This folder contains all REST APIs of the benchmark. Each API has a folder, containing :

- An OpenAPI Specification, in the JSON format.
- A Postman Collection, in the JSON format (not always available).
- A README document, containing information regarding the REST API.

### Badges

Each API README contains three badges describing the state of the API at the date of the last monthly check (`Last update`):

- `oas_version` badge: The OpenAPI format of the specification found in the folder.
    - `openapi_v<x.y.z>` (green): The specification is in a current OpenAPI format.
    - `swagger_v<x.y>` or `unknown` (orange): The specification is in an older format (e.g., Swagger 2.0), or its format could not be determined. A newer specification may be available upstream.

- `openapi-spec-validator` badge: The validity of the OpenAPI Specification found in the folder.
    - `valid` (green): A specification was found, can be parsed as JSON, and passes validation.
    - `invalid` (red): No specification was found in the folder, or the file cannot be parsed or validated.

- `available_servers` badge: The server URLs declared in the specification that responded to an HTTP request during the last check (`x` out of `y`).
    - `y_of_y` (green): All declared server URLs responded, or the API is deployed locally (so its server URLs are not checked online).
    - `0_of_y` (red): None of the declared server URLs responded during the last check.
    - `x_of_y` (orange): Some, but not all, declared server URLs responded during the last check.
    - `0_of_0` (grey): The specification does not declare any server URL.

### Additional Information

- When trying to open the OpenAPI Specifications in Python (`with open(api, "r") as file:`), do not forget to add the parameter `encoding="utf-8-sig"`. This increases the reliability of UTF-8 encoding detection, as some specifications can contain specific characters.