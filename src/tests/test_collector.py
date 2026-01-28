import json
from unittest.mock import patch, MagicMock
from src.collector import fetch_site

def test_fetch_site_success():
    fake_response = MagicMock()
    fake_response.status_code = 200
    

    with patch("src.collector.requests.get", return_value=fake_response):
        with patch("src.collector.r.publish") as mock_publish:
            fetch_site("https://example.com")
            assert mock_publish.called is True
            args, _ = mock_publish.call_args
            payload = json.loads(args[1])
            assert payload["site"] == "https://example.com"
            assert payload["response_time"] is not None
            assert payload["status_code"] == 200
            # assert mock_publish.call_args[0][1] == json.dumps({
            #     "site": "https://example.com",
            #     "response_time": fake_response.elapsed.total_seconds(),
            #     "status_code": 200,
            #     "error": None
            # })

def test_fetch_site_failure():
    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.error = "Connection refused"

    with patch("src.collector.requests.get", return_value=fake_response):
        with patch("src.collector.r.publish") as mock_publish:
            fetch_site("https://example.com")
            assert mock_publish.called is True
            args, _ = mock_publish.call_args
            payload = json.loads(args[1])
            assert payload["site"] == "https://example.com"
            assert payload["response_time"] is not None
            assert payload["status_code"] == 500
            # assert mock_publish.call_args[0][1] == json.dumps({
            #     "site": "https://example.com",
            #     "response_time": fake_response.elapsed.total_seconds(),
            #     "status_code": 500,
            #     "error": None
            # })