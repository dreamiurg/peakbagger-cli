"""Tests for the high-level PeakBagger API."""

from unittest.mock import MagicMock, patch

import pytest

from peakbagger import Ascent, Peak, PeakBagger, SearchResult

SEARCH_HTML = """<html><body>
<h2>Peak Search Results</h2>
<table class="gray">
<tr><th>Type</th><th>Peak</th><th>Location</th><th>Range</th><th>Elevation</th></tr>
<tr>
  <td>Summit</td>
  <td><a href="peak.aspx?pid=2296">Mount Rainier</a></td>
  <td>USA-WA</td>
  <td>Cascade Range</td>
  <td>14,411 ft / 4392 m</td>
</tr>
</table>
</body></html>"""

PEAK_HTML = """<html><body>
<h1>Mount Rainier, Washington</h1>
<h2>Elevation: 14,411 feet, 4392 meters</h2>
<p>Prominence: 13,210 ft, 4027 m</p>
<p>True Isolation: 1,326.0 mi, 2134.3 km</p>
<p>47.87967, -121.72616 (Dec Deg)</p>
United States
<p>Total ascents/attempts logged by registered Peakbagger.com users: <b>4388</b></p>
</body></html>"""

ASCENT_HTML = """<html><body>
<h1>Ascent of Mount Rainier on July 4, 2020</h1>
<h2>Climber: <a href="climber.aspx?cid=999">John Doe</a></h2>
<table class="gray" width="49%" align="left">
<tr><td><b>Date</b></td><td>Saturday, July 4, 2020</td></tr>
<tr><td><b>Ascent Type</b></td><td>Successful Summit Attained</td></tr>
<tr><td><b>Peak</b></td><td><a href="peak.aspx?pid=2296">Mount Rainier</a></td></tr>
</table>
</body></html>"""


def _make_client_mock(html: str) -> MagicMock:
    mock = MagicMock()
    mock.get.return_value = html
    return mock


class TestPeakBaggerSearch:
    def test_search_returns_results(self):
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock(SEARCH_HTML)):
            pb = PeakBagger()
            results = pb.search("Mount Rainier")

        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].name == "Mount Rainier"
        assert results[0].pid == "2296"
        assert results[0].elevation_ft == 14411

    def test_search_empty_results(self):
        empty_html = "<html><body><h2>Peak Search Results</h2></body></html>"
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock(empty_html)):
            pb = PeakBagger()
            results = pb.search("xyznonexistent")

        assert results == []

    def test_search_passes_query_to_client(self):
        mock_client = _make_client_mock(SEARCH_HTML)
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client):
            pb = PeakBagger()
            pb.search("Denali")

        mock_client.get.assert_called_once_with("/search.aspx", params={"ss": "Denali", "tid": "M"})


class TestPeakBaggerGetPeak:
    def test_get_peak_returns_peak(self):
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock(PEAK_HTML)):
            pb = PeakBagger()
            peak = pb.get_peak("2296")

        assert isinstance(peak, Peak)
        assert peak.pid == "2296"
        assert peak.name == "Mount Rainier"
        assert peak.elevation_ft == 14411

    def test_get_peak_accepts_int_id(self):
        mock_client = _make_client_mock(PEAK_HTML)
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client):
            pb = PeakBagger()
            pb.get_peak(2296)

        mock_client.get.assert_called_once_with("/peak.aspx", params={"pid": "2296"})

    def test_get_peak_returns_none_on_bad_html(self):
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock("<html/>")):
            pb = PeakBagger()
            peak = pb.get_peak("9999")

        assert peak is None


class TestPeakBaggerGetAscents:
    ASCENTS_HTML = """<html><body>
<table>
<tr><td></td></tr>
<tr><th>Climber</th><th>Ascent Date</th></tr>
<tr>
  <td><a href="climber.aspx?cid=1">Alice</a></td>
  <td><a href="ascent.aspx?aid=100">2024-06-15</a></td>
</tr>
</table>
</body></html>"""

    def test_get_ascents_passes_correct_params(self):
        mock_client = _make_client_mock(self.ASCENTS_HTML)
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client):
            pb = PeakBagger()
            pb.get_ascents("2296")

        mock_client.get.assert_called_once_with(
            "/climber/PeakAscents.aspx",
            params={"pid": "2296", "sort": "ascentdate", "u": "ft", "y": "9999"},
        )

    def test_get_ascents_returns_list(self):
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock("<html/>")):
            pb = PeakBagger()
            result = pb.get_ascents("2296")

        assert isinstance(result, list)


class TestPeakBaggerGetAscent:
    def test_get_ascent_returns_ascent(self):
        with patch("peakbagger.api.PeakBaggerClient", return_value=_make_client_mock(ASCENT_HTML)):
            pb = PeakBagger()
            ascent = pb.get_ascent("12963")

        assert isinstance(ascent, Ascent)
        assert ascent.ascent_id == "12963"
        assert ascent.climber_name == "John Doe"
        assert ascent.date == "2020-07-04"

    def test_get_ascent_accepts_int_id(self):
        mock_client = _make_client_mock(ASCENT_HTML)
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client):
            pb = PeakBagger()
            pb.get_ascent(12963)

        mock_client.get.assert_called_once_with("/climber/ascent.aspx", params={"aid": "12963"})


class TestPeakBaggerLifecycle:
    def test_close_delegates_to_client(self):
        mock_client = _make_client_mock("")
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client):
            pb = PeakBagger()
            pb.close()

        mock_client.close.assert_called_once()

    def test_context_manager_closes_on_exit(self):
        mock_client = _make_client_mock("")
        with patch("peakbagger.api.PeakBaggerClient", return_value=mock_client), PeakBagger():
            pass

        mock_client.close.assert_called_once()

    def test_context_manager_closes_on_exception(self):
        mock_client = _make_client_mock("")
        with (
            patch("peakbagger.api.PeakBaggerClient", return_value=mock_client),
            pytest.raises(ValueError),
            PeakBagger(),
        ):
            raise ValueError("test error")

        mock_client.close.assert_called_once()

    def test_custom_rate_limit_passed_to_client(self):
        with patch("peakbagger.api.PeakBaggerClient") as mock_cls:
            mock_cls.return_value = _make_client_mock("")
            PeakBagger(rate_limit_seconds=5.0)

        mock_cls.assert_called_once_with(rate_limit_seconds=5.0)


class TestPublicImports:
    def test_all_public_types_importable(self):
        from peakbagger import Ascent, AscentStatistics, Peak, PeakBagger, SearchResult

        assert PeakBagger is not None
        assert Peak is not None
        assert SearchResult is not None
        assert Ascent is not None
        assert AscentStatistics is not None

    def test_version_importable(self):
        from peakbagger import __version__

        assert isinstance(__version__, str)
        assert len(__version__) > 0
