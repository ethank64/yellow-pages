import json
import yaml
import requests

def simplify_openapi_schema(openapi_schema: dict) -> list:
    """
    Transforms a raw OpenAPI schema into a simplified, custom format.
    The returned object is a list of simplified API operation objects.
    Each object contains: {
        "name": str,
        "tags": list,
        "url": str, # This will now contain the full link
        "method": str,
        "parameters": list,
        "responses": dict
    }
    """
    simplified_api_list = []

    base_url_from_schema = "http://localhost"
    servers = openapi_schema.get("servers")
    if servers and isinstance(servers, list) and len(servers) > 0:
        base_url_from_schema = servers[0].get("url", base_url_from_schema)
        if base_url_from_schema.endswith('/'):
            base_url_from_schema = base_url_from_schema.rstrip('/')

    paths = openapi_schema.get("paths", {})

    for path, path_item in paths.items():
        cleaned_path = path if path.startswith('/') else '/' + path

        for method, operation in path_item.items():
            if method not in ["get", "post", "put", "delete", "patch", "head", "options", "trace"]:
                continue

            name = operation.get("operationId", f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}")

            parameters = []
            all_parameters = path_item.get("parameters", []) + operation.get("parameters", [])
            for param in all_parameters:
                simplified_param = {
                    "name": param.get("name"),
                    "in": param.get("in"),
                    "description": param.get("description"),
                    "required": param.get("required", False),
                    "type": param.get("schema", {}).get("type")
                }
                parameters.append(simplified_param)

            responses = {}
            for status_code, response_obj in operation.get("responses", {}).items():
                simplified_response = {
                    "description": response_obj.get("description")
                }
                content = response_obj.get("content", {})
                if "application/json" in content:
                    schema_ref = content["application/json"].get("schema", {}).get("$ref")
                    if schema_ref:
                        simplified_response["schema_ref"] = schema_ref
                elif "text/json" in content:
                    schema_ref = content["text/json"].get("schema", {}).get("$ref")
                    if schema_ref:
                        simplified_response["schema_ref"] = schema_ref
                elif "text/plain" in content:
                     schema_ref = content["text/plain"].get("schema", {}).get("$ref")
                     if schema_ref:
                        simplified_response["schema_ref"] = schema_ref

                responses[status_code] = simplified_response

            full_url_for_operation = f"{base_url_from_schema}{cleaned_path}"

            simplified_api_list.append({
                "name": name,
                "tags": operation.get("tags", []),
                "url": full_url_for_operation,
                "method": method.upper(),
                "parameters": parameters,
                "responses": responses
            })
    return simplified_api_list

def read_and_simplify_schema(file_path: str) -> list:
    """
    Reads an OpenAPI schema from a JSON/YAML file and returns
    a list of simplified API operation objects.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                openapi_data = json.load(f)
            except json.JSONDecodeError:
                f.seek(0)
                openapi_data = yaml.safe_load(f)

        return simplify_openapi_schema(openapi_data)

    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return []
    except (json.JSONDecodeError, yaml.YAMLError) as e:
        print(f"Error parsing schema file '{file_path}': {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading or simplifying schema: {e}")
        return []


def print_simplified_schema(simplified_schema: list):
    """
    Prints the simplified API schema (list of operations) in a nicely
    formatted JSON-like string.
    """
    print(json.dumps(simplified_schema, indent=2))

# *** CORRECTED `use_api` FUNCTION FOR DYNAMIC TOOL USE ***
def use_api(
    simplified_schema_entry: dict, # This is the crucial change: takes the specific entry
    path_params: dict = None,
    query_params: dict = None,
    body_data: dict = None,
    headers: dict = None
) -> str: # Return type is string for tool output
    """
    Calls an API endpoint based on a single simplified schema entry.

    Args:
        simplified_schema_entry: A dictionary representing a single API operation
                                 from your simplified schema. The 'url' field
                                 in this dict should already contain the full link.
        path_params: A dictionary of key-value pairs for path parameters.
        query_params: A dictionary of key-value pairs for query parameters.
        body_data: A dictionary for the request body (for POST/PUT/PATCH).
        headers: A dictionary of custom headers to send with the request.

    Returns:
        str: The JSON response as a string, or an error message.
    """
    if path_params is None:
        path_params = {}
    if query_params is None:
        query_params = {}
    if body_data is None: # Ensure body_data is a dict if not provided
        body_data = {}
    if headers is None:
        headers = {}

    full_url = simplified_schema_entry.get("url")
    method = simplified_schema_entry.get("method", "GET").upper()
    operation_name = simplified_schema_entry.get("name", "Unknown Operation") # For logging/error messages

    if not full_url:
        return f"Error: 'url' missing for operation '{operation_name}' in simplified schema entry."

    # 1. Substitute path parameters in the full_url
    # This loop remains the same, as the 'url' in simplified_schema_entry still has placeholders
    for param_name, param_value in path_params.items():
        placeholder = "{" + param_name + "}"
        if placeholder in full_url:
            full_url = full_url.replace(placeholder, str(param_value))

    # Basic validation: Check if all required path parameters were actually substituted
    for param_def in simplified_schema_entry.get("parameters", []):
        if param_def.get("in") == "path" and param_def.get("required"):
            if "{" + param_def["name"] + "}" in full_url:
                 return f"Error: Required path parameter '{param_def['name']}' was not provided or substituted in URL for operation '{operation_name}': {full_url}."

    print(f"\n--- Tool Calling: {method} {full_url} ---") # Log tool call for verbose agent output

    # 2. Make the request using the requests library
    try:
        if method == "GET":
            response = requests.get(full_url, params=query_params, headers=headers)
        elif method == "POST":
            response = requests.post(full_url, params=query_params, json=body_data, headers=headers)
        elif method == "PUT":
            response = requests.put(full_url, params=query_params, json=body_data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(full_url, params=query_params, headers=headers)
        elif method == "PATCH":
            response = requests.patch(full_url, params=query_params, json=body_data, headers=headers)
        else:
            return f"Error: Unsupported HTTP method '{method}' for operation '{operation_name}'."

        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Attempt to parse JSON response, otherwise return raw text
        try:
            return json.dumps(response.json(), indent=2)
        except json.JSONDecodeError:
            return response.text # Return raw text if not JSON

    except requests.exceptions.HTTPError as e:
        return f"API Error (Status {e.response.status_code}): {e.response.text.strip()}"
    except requests.exceptions.ConnectionError as e:
        return f"Connection Error: {e}"
    except requests.exceptions.Timeout as e:
        return f"Timeout Error: {e}"
    except requests.exceptions.RequestException as e:
        return f"An unexpected error occurred: {e}"


# --- Example Usage (Main Section) of utils.py is removed from here ---
# It's better to run tests or main logic from a separate file.
if __name__ == "__main__":
    print("This utils.py file contains helper functions.")
    print("Please run `main.py` or `test_api_calls.py` to see them in action.")
    # Example of how to use read_and_simplify_schema if needed for quick check
    # SCHEMA_FILE_PATH = "./sample_schema.json"
    # simplified_data = read_and_simplify_schema(SCHEMA_FILE_PATH)
    # if simplified_data:
    #     print_simplified_schema(simplified_data)
