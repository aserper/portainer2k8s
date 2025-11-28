import unittest
from unittest.mock import MagicMock, patch
from portainer_to_k8s import PortainerClient

class TestPortainerClientEndpoints(unittest.TestCase):

    @patch('portainer_to_k8s.requests.Session')
    def test_get_endpoints_legacy(self, mock_session_cls):
        """Test fetching endpoints with legacy API."""
        mock_session = mock_session_cls.return_value
        
        # Mock response for /api/endpoints
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Id": 1, "Name": "local"}, {"Id": 2, "Name": "remote"}]
        mock_session.get.return_value = mock_response
        
        client = PortainerClient("http://portainer.local", api_key="test")
        endpoints = client.get_endpoints()
        
        self.assertEqual(len(endpoints), 2)
        self.assertEqual(endpoints[0]["Name"], "local")
        mock_session.get.assert_called_with("http://portainer.local/api/endpoints", params={"limit": 100}, timeout=15)

    @patch('portainer_to_k8s.requests.Session')
    def test_get_endpoints_fallback(self, mock_session_cls):
        """Test fetching endpoints with fallback to environments API."""
        mock_session = mock_session_cls.return_value
        
        # Mock 404 for /api/endpoints
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404
        
        # Mock 200 for /api/environments
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = [{"Id": 1, "Name": "local-env"}]
        
        # Configure side_effect for sequential calls
        mock_session.get.side_effect = [mock_response_404, mock_response_200]
        
        client = PortainerClient("http://portainer.local", api_key="test")
        endpoints = client.get_endpoints()
        
        self.assertEqual(len(endpoints), 1)
        self.assertEqual(endpoints[0]["Name"], "local-env")
        
        # Verify calls
        from unittest.mock import call
        expected_calls = [
            call("http://portainer.local/api/endpoints", params={"limit": 100}, timeout=15),
            call("http://portainer.local/api/environments", params={"limit": 100}, timeout=15)
        ]
        mock_session.get.assert_has_calls(expected_calls)

if __name__ == '__main__':
    unittest.main()
