import os
from .utils import read_and_simplify_schema, use_api

# Define the path to your schema file (relative to project root when run from there)
SCHEMA_FILE_PATH = "./sample_schema.json"

# Define a dictionary of test parameters for different operations
# You'll need to customize this based on the actual parameters
# required by each API endpoint in your simplified schema.
TEST_PARAMS = {
    "CountryCountryInfo": {
        "path_params": {"countryCode": "US"},
        "description": "Get country info for United States"
    },
    "CountryAvailableCountries": {
        "description": "Get all available countries"
    },
    "LongWeekendLongWeekend": {
        "path_params": {"year": 2025, "countryCode": "GB"},
        "query_params": {"availableBridgeDays": 0},
        "description": "Get long weekends for GB in 2025"
    },
    "PublicHolidayPublicHolidaysV3": {
        "path_params": {"year": 2024, "countryCode": "DE"},
        "description": "Get public holidays for Germany in 2024"
    },
    "PublicHolidayIsTodayPublicHoliday": {
        "path_params": {"countryCode": "FR"},
        "query_params": {"offset": 1}, # Example: adjust for a different timezone
        "description": "Check if today is public holiday in France"
    },
    "PublicHolidayNextPublicHolidays": {
        "path_params": {"countryCode": "JP"},
        "description": "Get next public holidays for Japan"
    },
    "PublicHolidayNextPublicHolidaysWorldwide": {
        "description": "Get next public holidays worldwide"
    },
    "VersionGetVersion": {
        "description": "Get API version info"
    }
}

def run_all_api_tests(schema_file: str):
    """
    Reads the simplified schema, iterates through each operation,
    and runs a test API call, reporting success/failure.
    """
    print(f"--- Running API Tests from schema: {schema_file} ---")

    simplified_schema = read_and_simplify_schema(schema_file)

    if not simplified_schema:
        print("Error: Failed to load or simplify schema. Cannot run tests.")
        return

    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    # Convert list of operations to a dict for easier lookup by name
    simplified_schema_dict = {op['name']: op for op in simplified_schema}

    for operation_name, test_config in TEST_PARAMS.items():
        total_tests += 1
        print(f"\nTesting: {operation_name} ({test_config.get('description', 'No description')})...")

        # Get the actual simplified schema entry for this operation
        schema_entry = simplified_schema_dict.get(operation_name)

        if not schema_entry:
            print(f"  SKIP: Operation '{operation_name}' not found in the loaded schema.")
            failed_tests += 1
            continue

        response = use_api(
            simplified_schema_entry=schema_entry,
            path_params=test_config.get("path_params") or {},
            query_params=test_config.get("query_params") or {},
            body_data=test_config.get("body_data") or {},
            headers=test_config.get("headers") or {}
        )

        # use_api returns a string (JSON or error message)
        if response and not response.strip().startswith(("Error:", "API Error", "Connection Error", "Timeout Error")):
            print(f"  PASS: {operation_name}")
            passed_tests += 1
        else:
            print(f"  FAIL: {operation_name} - {response[:200] if response else 'No response'}")
            failed_tests += 1

    print("\n--- Test Summary ---")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    if failed_tests > 0:
        print("Some tests failed. Check logs above for details.")
    else:
        print("All tests passed successfully!")

if __name__ == "__main__":
    # Ensure the sample_schema.json exists for the test to run (path relative to cwd, typically project root)
    if not os.path.exists(SCHEMA_FILE_PATH):
        print(f"Error: '{SCHEMA_FILE_PATH}' not found. Run from project root.")
        print("You need to save the full OpenAPI JSON content (from previous step) into this file.")
    else:
        run_all_api_tests(SCHEMA_FILE_PATH)
