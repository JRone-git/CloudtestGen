import pytest
import asyncio
import requests
import aiohttp  # For async API testing

# Constants for testing
CLOUD_API_BASE_URL = "https://example-cloud-api.com"  # Replace with actual base URL of your cloud service
RESOURCE_ENDPOINT = f"{CLOUD_API_BASE_URL}/resources"  # Endpoint for resource management
HEADERS = {"Authorization": "Bearer your_token_here"}  # Authentication headers


@pytest.fixture(scope="module")
def setup_cloud_resource():
    """
    Fixture to create a cloud resource before tests and clean it up afterward.
    - Creates a resource (e.g., a VM instance).
    - Yields the resource ID for use in tests.
    - Deletes the resource after the test suite completes.
    """
    resource_data = {"name": "test-instance", "type": "vm", "region": "us-east-1"}
    # Create the resource
    response = requests.post(RESOURCE_ENDPOINT, json=resource_data, headers=HEADERS)
    assert response.status_code == 201, "Failed to create resource"
    resource_id = response.json().get("id")  # Extract resource ID from response
    
    # Provide the resource ID to the tests
    yield resource_id
    
    # Cleanup the resource after tests are done
    requests.delete(f"{RESOURCE_ENDPOINT}/{resource_id}", headers=HEADERS)


@pytest.mark.asyncio
async def test_api_response_format():
    """
    Test the format and content of the cloud service API response.
    - Ensures the API returns a 200 status.
    - Validates that the response contains a 'status' field with the value 'OK'.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(CLOUD_API_BASE_URL, headers=HEADERS) as resp:
            assert resp.status == 200, "API did not return a 200 status code"
            data = await resp.json()  # Parse JSON response
            assert "status" in data, "Response is missing the 'status' field"
            assert data["status"] == "OK", "Unexpected API status"


@pytest.mark.parametrize("input_data,expected_status", [
    ({"name": "test-instance", "type": "vm"}, 201),  # Valid input
    ({"name": "", "type": "vm"}, 400),             # Missing name
    ({"type": "vm"}, 400),                         # Missing name field entirely
])
def test_create_resource(input_data, expected_status):
    """
    Parameterized test for creating a cloud resource with various inputs.
    - Tests valid and invalid input scenarios.
    - Validates that the API returns the expected HTTP status code.
    """
    response = requests.post(RESOURCE_ENDPOINT, json=input_data, headers=HEADERS)
    assert response.status_code == expected_status, f"Unexpected status: {response.status_code}"


def test_resource_is_running(setup_cloud_resource):
    """
    Test that the cloud resource is in a 'running' state after creation.
    - Uses the resource ID provided by the fixture.
    - Validates that the resource status is 'running'.
    """
    resource_id = setup_cloud_resource
    # Fetch the resource details
    response = requests.get(f"{RESOURCE_ENDPOINT}/{resource_id}", headers=HEADERS)
    assert response.status_code == 200, "Failed to retrieve resource details"
    resource_status = response.json().get("status")  # Extract resource status
    assert resource_status == "running", f"Resource is not running, status: {resource_status}"
