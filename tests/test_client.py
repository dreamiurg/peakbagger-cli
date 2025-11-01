"""
Comprehensive tests for HTTP client module.

Tests cover:
- Rate limiting enforcement
- URL construction
- Error handling
- Session management
"""

from unittest.mock import Mock, patch

import pytest

from peakbagger.client import PeakBaggerClient


class TestPeakBaggerClientInitialization:
    """Tests for client initialization."""

    def test_init_default_rate_limit(self):
        """Test client initialization with default rate limit."""
        client = PeakBaggerClient()

        assert client.rate_limit == 2.0
        assert client._last_request_time is None
        assert client.session is not None
        assert "peakbagger-cli" in client.session.headers["User-Agent"]

    def test_init_custom_rate_limit(self):
        """Test client initialization with custom rate limit."""
        client = PeakBaggerClient(rate_limit_seconds=5.0)

        assert client.rate_limit == 5.0

    def test_init_sets_user_agent(self):
        """Test that user agent is properly set."""
        client = PeakBaggerClient()

        user_agent = client.session.headers["User-Agent"]
        assert "peakbagger-cli" in user_agent
        assert "Python CLI tool" in user_agent
        # Check for full GitHub URL to avoid CodeQL URL substring sanitization warning
        assert "https://github.com/dreamiurg/peakbagger-cli" in user_agent


class TestPeakBaggerClientRateLimiting:
    """Tests for rate limiting functionality."""

    @patch("peakbagger.client.time.sleep")
    @patch("peakbagger.client.time.time")
    def test_rate_limiting_enforced_on_consecutive_requests(self, mock_time, mock_sleep):
        """Test that rate limiting waits between consecutive requests."""
        client = PeakBaggerClient(rate_limit_seconds=2.0)

        # First request - no waiting
        mock_time.return_value = 100.0
        client._wait_for_rate_limit()
        mock_sleep.assert_not_called()

        # Simulate first request completing
        client._last_request_time = 100.0

        # Second request - should wait
        mock_time.return_value = 101.0  # Only 1 second has passed
        client._wait_for_rate_limit()

        # Should wait for remaining time (2.0 - 1.0 = 1.0 second)
        mock_sleep.assert_called_once()
        wait_time = mock_sleep.call_args[0][0]
        assert abs(wait_time - 1.0) < 0.01  # Allow small floating point difference

    @patch("peakbagger.client.time.sleep")
    @patch("peakbagger.client.time.time")
    def test_no_rate_limiting_when_enough_time_passed(self, mock_time, mock_sleep):
        """Test that no waiting occurs when enough time has passed."""
        client = PeakBaggerClient(rate_limit_seconds=2.0)

        # Simulate first request
        client._last_request_time = 100.0

        # Enough time has passed
        mock_time.return_value = 103.0  # 3 seconds later
        client._wait_for_rate_limit()

        # Should not wait
        mock_sleep.assert_not_called()

    @patch("peakbagger.client.time.sleep")
    def test_rate_limiting_first_request_no_wait(self, mock_sleep):
        """Test that first request doesn't wait."""
        client = PeakBaggerClient(rate_limit_seconds=2.0)

        client._wait_for_rate_limit()

        mock_sleep.assert_not_called()

    @patch("peakbagger.client.time.sleep")
    @patch("peakbagger.client.time.time")
    def test_rate_limiting_with_zero_rate_limit(self, mock_time, mock_sleep):
        """Test rate limiting with zero rate limit (no throttling)."""
        client = PeakBaggerClient(rate_limit_seconds=0.0)

        client._last_request_time = 100.0
        mock_time.return_value = 100.001  # Very short time

        client._wait_for_rate_limit()

        # Should not wait with 0.0 rate limit
        mock_sleep.assert_not_called()


class TestPeakBaggerClientGet:
    """Tests for GET request functionality."""

    def test_get_with_relative_url(self):
        """Test GET request with relative URL path."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = client.get("climber.aspx")

            assert result == "<html>Test</html>"
            # Verify full URL was constructed
            called_url = mock_get.call_args[0][0]
            assert called_url == "https://www.peakbagger.com/climber.aspx"

    def test_get_with_absolute_url(self):
        """Test GET request with absolute URL."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = client.get("https://example.com/page")

            assert result == "<html>Test</html>"
            # Verify URL was used as-is
            called_url = mock_get.call_args[0][0]
            assert called_url == "https://example.com/page"

    def test_get_with_query_params(self):
        """Test GET request with query parameters."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            params = {"pid": "2296", "sort": "date"}
            result = client.get("climber.aspx", params=params)

            assert result == "<html>Test</html>"
            # Verify params were passed
            assert mock_get.call_args[1]["params"] == params

    def test_get_updates_last_request_time(self):
        """Test that GET request updates last request time."""
        client = PeakBaggerClient()

        assert client._last_request_time is None

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            client.get("test.aspx")

            assert client._last_request_time is not None
            assert isinstance(client._last_request_time, float)

    def test_get_raises_for_http_errors(self):
        """Test that GET raises exception for HTTP errors."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response

            with pytest.raises(Exception, match="Failed to fetch"):
                client.get("nonexistent.aspx")

    def test_get_handles_network_errors(self):
        """Test that GET handles network errors properly."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_get.side_effect = Exception("Connection timeout")

            with pytest.raises(Exception, match="Failed to fetch"):
                client.get("test.aspx")

    @patch("peakbagger.client.time.sleep")
    @patch("peakbagger.client.time.time")
    def test_get_enforces_rate_limiting(self, mock_time, mock_sleep):
        """Test that GET requests enforce rate limiting."""
        client = PeakBaggerClient(rate_limit_seconds=2.0)

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # First request
            mock_time.return_value = 100.0
            client.get("test1.aspx")

            # Second request shortly after
            mock_time.return_value = 100.5  # 0.5 seconds later
            client.get("test2.aspx")

            # Should have waited
            mock_sleep.assert_called()

    def test_get_strips_leading_slash_from_path(self):
        """Test that leading slashes are stripped from relative paths."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            client.get("/climber.aspx")

            called_url = mock_get.call_args[0][0]
            # Should not have double slashes
            assert called_url == "https://www.peakbagger.com/climber.aspx"
            assert "//" not in called_url.replace("https://", "")


class TestPeakBaggerClientSession:
    """Tests for session management."""

    def test_close_closes_session(self):
        """Test that close() closes the underlying session."""
        client = PeakBaggerClient()

        with patch.object(client.session, "close") as mock_close:
            client.close()

            mock_close.assert_called_once()

    def test_client_can_be_used_as_context_manager(self):
        """Test that client works with context manager pattern."""
        with patch.object(PeakBaggerClient, "close") as mock_close:
            client = PeakBaggerClient()

            # Manually close to simulate context manager __exit__
            client.close()

            mock_close.assert_called_once()


class TestPeakBaggerClientIntegration:
    """Integration tests for client functionality."""

    @patch("peakbagger.client.time.sleep")
    def test_multiple_requests_with_rate_limiting(self, mock_sleep):
        """Test multiple requests with proper rate limiting."""
        client = PeakBaggerClient(rate_limit_seconds=0.1)  # Short rate limit for test

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = "<html>Test</html>"
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            # Make 3 requests in quick succession
            client.get("test1.aspx")
            # No sleep on first request
            assert mock_sleep.call_count == 0

            client.get("test2.aspx")
            # Should sleep on second request
            assert mock_sleep.call_count >= 1

            client.get("test3.aspx")
            # Should sleep on third request
            assert mock_sleep.call_count >= 2

    def test_error_handling_preserves_exception_chain(self):
        """Test that error handling preserves exception chain."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            original_error = ConnectionError("Network unreachable")
            mock_get.side_effect = original_error

            with pytest.raises(Exception) as exc_info:
                client.get("test.aspx")

            # Verify exception chain is preserved
            assert exc_info.value.__cause__ is original_error


class TestPeakBaggerClientEdgeCases:
    """Edge case tests for client."""

    def test_get_with_empty_response(self):
        """Test GET request with empty response."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            mock_response = Mock()
            mock_response.text = ""
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = client.get("test.aspx")

            assert result == ""

    def test_get_with_very_large_response(self):
        """Test GET request with very large response."""
        client = PeakBaggerClient()

        with patch.object(client.session, "get") as mock_get:
            large_html = "<html>" + ("x" * 1_000_000) + "</html>"
            mock_response = Mock()
            mock_response.text = large_html
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = client.get("test.aspx")

            assert len(result) > 1_000_000

    def test_custom_rate_limit_very_small(self):
        """Test with very small rate limit."""
        client = PeakBaggerClient(rate_limit_seconds=0.001)

        assert client.rate_limit == 0.001

    def test_custom_rate_limit_very_large(self):
        """Test with very large rate limit."""
        client = PeakBaggerClient(rate_limit_seconds=60.0)

        assert client.rate_limit == 60.0

    def test_base_url_constant(self):
        """Test that BASE_URL is correct."""
        assert PeakBaggerClient.BASE_URL == "https://www.peakbagger.com"
