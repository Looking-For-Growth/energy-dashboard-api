import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from services.api_clients import CarbonIntensityService


class CarbonIntensityTests(unittest.TestCase):
    def setUp(self):
        self.service = CarbonIntensityService()

    @patch("services.base_client.requests.request")
    def test_get_current_intensity(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_current_intensity()
        self.assertEqual(result, {"data": "dummy"})
        mock_request.assert_called_once()
        self.assertIn("intensity", mock_request.call_args[1]["url"])

    @patch("services.base_client.requests.request")
    def test_get_intensity_today(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_intensity_today()
        self.assertEqual(result, {"data": "dummy"})
        self.assertIn("intensity/date", mock_request.call_args[1]["url"])

    @patch("services.base_client.requests.request")
    def test_get_current_generation(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_current_generation()
        self.assertEqual(result, {"data": "dummy"})
        self.assertIn("generation", mock_request.call_args[1]["url"])

    @patch("services.base_client.requests.request")
    def test_get_regional_current(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_regional_current()
        self.assertEqual(result, {"data": "dummy"})
        self.assertIn("regional", mock_request.call_args[1]["url"])

    @patch("services.base_client.requests.request")
    def test_get_intensity_between(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_intensity_between(
            datetime(2023, 10, 1, 12, 0), datetime(2023, 10, 2, 12, 0)
        )
        self.assertEqual(result, {"data": "dummy"})

    @patch("services.base_client.requests.request")
    def test_get_statistics(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_statistics(
            datetime(2023, 10, 1), datetime(2023, 10, 2)
        )
        self.assertEqual(result, {"data": "dummy"})

    @patch("services.base_client.requests.request")
    def test_get_intensity_date(self, mock_request):
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "dummy"}
        mock_request.return_value = mock_response

        result = self.service.get_intensity_date(datetime(2023, 10, 1))
        self.assertEqual(result, {"data": "dummy"})
