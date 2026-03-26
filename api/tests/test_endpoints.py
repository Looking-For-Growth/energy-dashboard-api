import os

os.environ.setdefault("APP_DEVELOPMENT", "true")

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.text == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "200 OK" in response.text


def test_docs_redirect():
    response = client.get("/docs/", follow_redirects=False)
    assert response.status_code == 200


# --- Carbon Intensity Endpoints ---


MOCK_INTENSITY_RESPONSE = {
    "data": [
        {
            "from": "2023-10-01T12:00Z",
            "to": "2023-10-01T12:30Z",
            "intensity": {"actual": 200, "forecast": 195, "index": "moderate"},
        }
    ]
}


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_current_carbon_intensity_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_current_intensity.return_value = MOCK_INTENSITY_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/current/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    entry = data[0]
    # Verify flattened shape matches old Django serializer output
    assert entry["from_datetime"] == "2023-10-01T12:00:00Z"
    assert entry["to_datetime"] == "2023-10-01T12:30:00Z"
    assert entry["actual"] == 200
    assert entry["forecast"] == 195
    assert entry["index"] == "Moderate"
    assert entry["region"] is None
    assert entry["postcode_prefix"] is None
    # Verify no nested intensity object
    assert "intensity" not in entry
    assert "from" not in entry
    assert "to" not in entry


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_latest_carbon_intensity_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_current_intensity.return_value = MOCK_INTENSITY_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/latest/")
    assert response.status_code == 200
    data = response.json()
    # Latest returns a single object, not a list
    assert isinstance(data, dict)
    assert data["from_datetime"] == "2023-10-01T12:00:00Z"
    assert data["actual"] == 200
    assert data["region"] is None


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_today_carbon_intensity_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_intensity_today.return_value = MOCK_INTENSITY_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/today/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["from_datetime"] == "2023-10-01T12:00:00Z"
    assert data[0]["actual"] == 200


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_carbon_intensity_by_date_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_intensity_date.return_value = MOCK_INTENSITY_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/date/2023-10-01/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["from_datetime"] == "2023-10-01T12:00:00Z"


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_regional_carbon_intensity(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_regional_current.return_value = {"data": []}
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/regional/")
    assert response.status_code == 200


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_carbon_intensity_stats_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_statistics.return_value = {
        "data": {"min": 50, "max": 300, "average": 175.5}
    }
    mock_service_class.return_value = mock_service

    response = client.get(
        "/api/v1/carbon-intensity/stats/2023-10-01T00:00Z/2023-10-02T00:00Z/"
    )
    assert response.status_code == 200
    data = response.json()
    # Verify flattened stats shape matches old Django serializer
    assert data["from_datetime"] == "2023-10-01T00:00Z"
    assert data["to_datetime"] == "2023-10-02T00:00Z"
    assert data["min_intensity"] == 50
    assert data["max_intensity"] == 300
    assert data["average_intensity"] == 175.5
    assert data["block_hours"] is None
    # Verify no raw field names
    assert "min" not in data
    assert "max" not in data
    assert "average" not in data


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_carbon_intensity_list_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_intensity_between.return_value = MOCK_INTENSITY_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/carbon-intensity/?from=2023-10-01&to=2023-10-02")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["from_datetime"] == "2023-10-01T12:00:00Z"
    assert data[0]["actual"] == 200


# --- Generation Mix Endpoints ---


MOCK_GENERATION_RESPONSE = {
    "data": {
        "from": "2023-10-01T12:00Z",
        "to": "2023-10-01T12:30Z",
        "generationmix": [
            {"fuel": "gas", "perc": 45.3},
            {"fuel": "nuclear", "perc": 20.1},
            {"fuel": "wind", "perc": 25.4},
        ],
    }
}


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_generation_mix_latest_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_current_generation.return_value = MOCK_GENERATION_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/generation-mix/latest/")
    assert response.status_code == 200
    data = response.json()
    # Verify flattened shape matches old Django serializer
    assert isinstance(data, dict)
    assert data["from_datetime"] == "2023-10-01T12:00:00Z"
    assert data["to_datetime"] == "2023-10-01T12:30:00Z"
    assert isinstance(data["fuel_mix"], dict)
    assert data["fuel_mix"]["gas"] == 45.3
    assert data["fuel_mix"]["nuclear"] == 20.1
    assert data["fuel_mix"]["wind"] == 25.4
    # Verify no raw generationmix array
    assert "generationmix" not in data


@patch("routers.carbon_intensity.CarbonIntensityService")
def test_generation_mix_list_shape(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_current_generation.return_value = MOCK_GENERATION_RESPONSE
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/generation-mix/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["fuel_mix"]["gas"] == 45.3


# --- Octopus Endpoints ---


@patch("routers.octopus.OctopusService")
def test_list_grid_supply_points(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_grid_supply_points.return_value = {
        "results": [{"group_id": "_A"}, {"group_id": "_B"}]
    }
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/grid-supply-point/")
    assert response.status_code == 200


@patch("routers.octopus.OctopusService")
def test_gsp_by_postcode(mock_service_class):
    mock_service = MagicMock()
    mock_service.get_grid_supply_point_by_postcode.return_value = "C"
    mock_service_class.return_value = mock_service

    response = client.get("/api/v1/grid-supply-point/by-postcode/?postcode=SW1A1AA")
    assert response.status_code == 200
    assert response.json() == {"group_id": "C"}
