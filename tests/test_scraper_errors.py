"""
Comprehensive scraper error handling and edge case tests.

Tests cover:
- Missing HTML elements
- Malformed data
- Empty/invalid results
- Exception handling paths
- Edge cases in parsing logic
"""

from peakbagger.scraper import PeakBaggerScraper


class TestParseSearchResultsErrors:
    """Tests for parse_search_results error handling."""

    def test_parse_search_results_no_header(self):
        """Test parsing when search results header is missing."""
        html = "<html><body><table class='gray'><tr><td>Data</td></tr></table></body></html>"
        results = PeakBaggerScraper.parse_search_results(html)

        assert results == []

    def test_parse_search_results_no_table_after_header(self):
        """Test parsing when table is missing after header."""
        html = "<html><body><h2>Peak Search Results</h2><p>Some text</p></body></html>"
        results = PeakBaggerScraper.parse_search_results(html)

        assert results == []

    def test_parse_search_results_insufficient_columns(self):
        """Test parsing rows with insufficient columns."""
        html = """
        <html><body>
        <h2>Peak Search Results</h2>
        <table class="gray">
            <tr><th>Type</th><th>Name</th></tr>
            <tr><td>Summit</td><td>Peak Name</td></tr>
        </table>
        </body></html>
        """
        results = PeakBaggerScraper.parse_search_results(html)

        # Should skip row with insufficient columns
        assert results == []

    def test_parse_search_results_no_peak_link(self):
        """Test parsing when peak link is missing."""
        html = """
        <html><body>
        <h2>Peak Search Results</h2>
        <table class="gray">
            <tr><th>Type</th><th>Name</th><th>Location</th><th>Range</th><th>Elevation</th></tr>
            <tr>
                <td>Summit</td>
                <td>Peak Name</td>
                <td>USA-WA</td>
                <td>Cascades</td>
                <td>10,000 ft</td>
            </tr>
        </table>
        </body></html>
        """
        results = PeakBaggerScraper.parse_search_results(html)

        # Should skip row without peak link
        assert results == []

    def test_parse_search_results_invalid_pid_format(self):
        """Test parsing when peak ID format is invalid."""
        html = """
        <html><body>
        <h2>Peak Search Results</h2>
        <table class="gray">
            <tr><th>Type</th><th>Name</th><th>Location</th><th>Range</th><th>Elevation</th></tr>
            <tr>
                <td>Summit</td>
                <td><a href="peak.aspx?id=invalid">Peak Name</a></td>
                <td>USA-WA</td>
                <td>Cascades</td>
                <td>10,000 ft</td>
            </tr>
        </table>
        </body></html>
        """
        results = PeakBaggerScraper.parse_search_results(html)

        # Should skip row with invalid PID
        assert results == []

    def test_parse_search_results_elevation_with_meters(self):
        """Test parsing elevation when meters are included."""
        html = """
        <html><body>
        <h2>Peak Search Results</h2>
        <table class="gray">
            <tr><th>Type</th><th>Name</th><th>Location</th><th>Range</th><th>Elevation</th></tr>
            <tr>
                <td>Summit</td>
                <td><a href="peak.aspx?pid=123">Test Peak</a></td>
                <td>USA-WA</td>
                <td>Cascades</td>
                <td>10,000 ft / 3048 m</td>
            </tr>
        </table>
        </body></html>
        """
        results = PeakBaggerScraper.parse_search_results(html)

        assert len(results) == 1
        assert results[0].elevation_ft == 10000
        assert results[0].elevation_m == 3048


class TestParsePeakDetailErrors:
    """Tests for parse_peak_detail error handling."""

    def test_parse_peak_detail_no_h1(self):
        """Test parsing when H1 tag is missing."""
        html = "<html><body><p>Some content</p></body></html>"
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        assert peak is None

    def test_parse_peak_detail_attribute_error(self):
        """Test handling of AttributeError during parsing."""
        # Malformed HTML that might cause AttributeError
        html = """
        <html><body>
        <h1>Test Peak, WA</h1>
        <h2>Elevation: 10,000 feet, 3048 meters</h2>
        </body></html>
        """
        # This should handle any AttributeError gracefully
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        # Should return a peak object with basic info
        assert peak is not None
        assert peak.pid == "123"
        assert peak.name == "Test Peak"

    def test_parse_peak_detail_country_canada(self):
        """Test parsing when country is Canada."""
        html = """
        <html><body>
        <h1>Test Peak, BC</h1>
        <h2>Elevation: 10,000 feet, 3048 meters</h2>
        <table class="gray">
            <tr><td>Country:</td><td>Canada</td></tr>
        </table>
        </body></html>
        """
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        assert peak is not None
        assert peak.country == "Canada"

    def test_parse_peak_detail_country_mexico(self):
        """Test parsing when country is Mexico."""
        html = """
        <html><body>
        <h1>Test Peak, Chihuahua</h1>
        <h2>Elevation: 10,000 feet, 3048 meters</h2>
        <table class="gray">
            <tr><td>Country:</td><td>Mexico</td></tr>
        </table>
        </body></html>
        """
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        assert peak is not None
        assert peak.country == "Mexico"

    def test_parse_peak_detail_value_error(self):
        """Test handling of ValueError during parsing."""
        # HTML with invalid numeric values
        html = """
        <html><body>
        <h1>Test Peak, WA</h1>
        <h2>Elevation: invalid feet, meters</h2>
        </body></html>
        """
        # Should handle ValueError gracefully
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        # Should return a peak with basic info, no elevation
        assert peak is not None
        assert peak.elevation_ft is None

    def test_parse_peak_detail_type_error(self):
        """Test handling of TypeError during parsing."""
        # Malformed HTML structure that might cause TypeError
        html = """
        <html><body>
        <h1>Test Peak, WA</h1>
        </body></html>
        """
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        # Should handle TypeError gracefully
        assert peak is not None

    def test_parse_peak_detail_generic_exception(self):
        """Test handling of unexpected exceptions during parsing."""
        # Empty HTML
        html = ""
        peak = PeakBaggerScraper.parse_peak_detail(html, "123")

        # Should return None on unexpected errors
        assert peak is None


class TestParsePeakAscentsErrors:
    """Tests for parse_peak_ascents error handling."""

    def test_parse_peak_ascents_no_valid_table(self):
        """Test parsing when no valid table is found."""
        html = """
        <html><body>
        <table><tr><td>No data</td></tr></table>
        </body></html>
        """
        ascents = PeakBaggerScraper.parse_peak_ascents(html)

        assert ascents == []

    def test_parse_peak_ascents_missing_required_columns(self):
        """Test parsing when Climber or Date columns are missing."""
        html = """
        <html><body>
        <table>
            <tr><td>&nbsp;</td></tr>
            <tr>
                <th>Something</th>
                <th>Other</th>
                <th>Columns</th>
            </tr>
            <tr><td>Data</td><td>More</td><td>Stuff</td></tr>
        </table>
        </body></html>
        """
        ascents = PeakBaggerScraper.parse_peak_ascents(html)

        assert ascents == []

    def test_parse_peak_ascents_no_climber_link(self):
        """Test parsing rows without climber link."""
        html = """
        <html><body>
        <table>
            <tr><td>&nbsp;</td></tr>
            <tr>
                <th>Climber</th>
                <th>Ascent Date</th>
            </tr>
            <tr>
                <td>No Link Here</td>
                <td><a href="ascent.aspx?aid=123">2024-01-01</a></td>
            </tr>
        </table>
        </body></html>
        """
        ascents = PeakBaggerScraper.parse_peak_ascents(html)

        # Should skip rows without climber link
        assert ascents == []

    def test_parse_peak_ascents_no_date_link(self):
        """Test parsing rows without date link."""
        html = """
        <html><body>
        <table>
            <tr><td>&nbsp;</td></tr>
            <tr>
                <th>Climber</th>
                <th>Ascent Date</th>
            </tr>
            <tr>
                <td><a href="climber.aspx?cid=456">John Doe</a></td>
                <td>No Link</td>
            </tr>
        </table>
        </body></html>
        """
        ascents = PeakBaggerScraper.parse_peak_ascents(html)

        # Should skip rows without date link
        assert ascents == []

    def test_parse_peak_ascents_invalid_ascent_id(self):
        """Test parsing when ascent ID is invalid."""
        html = """
        <html><body>
        <table>
            <tr><td>&nbsp;</td></tr>
            <tr>
                <th>Climber</th>
                <th>Ascent Date</th>
            </tr>
            <tr>
                <td><a href="climber.aspx?cid=456">John Doe</a></td>
                <td><a href="ascent.aspx?id=invalid">2024-01-01</a></td>
            </tr>
        </table>
        </body></html>
        """
        ascents = PeakBaggerScraper.parse_peak_ascents(html)

        # Should skip rows with invalid ascent ID
        assert ascents == []


class TestParseAscentDetailErrors:
    """Tests for parse_ascent_detail error handling."""

    def test_parse_ascent_detail_no_h1(self):
        """Test parsing when H1 tag is missing."""
        html = "<html><body><p>Some content</p></body></html>"
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        assert ascent is None

    def test_parse_ascent_detail_no_peak_name_in_title(self):
        """Test parsing when title format is unexpected."""
        html = """
        <html><body>
        <h1>Some Other Title</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Date:</b></td><td>2024-01-01</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should still parse with basic info
        assert ascent is not None
        assert ascent.peak_name is None

    def test_parse_ascent_detail_no_climber_name(self):
        """Test parsing when climber name is missing."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: No Link</h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Date:</b></td><td>2024-01-01</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should return None if no climber name
        assert ascent is None

    def test_parse_ascent_detail_no_table(self):
        """Test parsing when data table is missing."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should return None if no table
        assert ascent is None

    def test_parse_ascent_detail_single_cell_row_no_trip_report(self):
        """Test parsing single-cell row without trip report."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td colspan="2">Some other content</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should parse basic info
        assert ascent is not None
        assert ascent.trip_report_text is None

    def test_parse_ascent_detail_single_cell_without_colspan(self):
        """Test parsing row with single cell (no colspan)."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td>Single cell</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should skip rows with single cell
        assert ascent is not None

    def test_parse_ascent_detail_date_value_error(self):
        """Test handling of ValueError in date parsing."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Date:</b></td><td>Invalid Date Format</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle date parsing error gracefully
        assert ascent is not None
        # Date should remain None if parsing fails
        assert ascent.date is None

    def test_parse_ascent_detail_route_with_label_variants(self):
        """Test parsing route with different label variants."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Route Name:</b></td><td>Standard Route</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should parse route from "Route Name" label
        assert ascent is not None
        assert ascent.route == "Standard Route"

    def test_parse_ascent_detail_route_empty_string(self):
        """Test parsing route when it's an empty string."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Route:</b></td><td></td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should set route to None if empty
        assert ascent is not None
        assert ascent.route is None

    def test_parse_ascent_detail_elevation_gain_no_match(self):
        """Test parsing elevation gain when format doesn't match."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Elevation Gain:</b></td><td>Unknown</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle missing elevation gain
        assert ascent is not None
        assert ascent.elevation_gain_ft is None

    def test_parse_ascent_detail_distance_no_match(self):
        """Test parsing distance when format doesn't match."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Distance:</b></td><td>Not specified</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle missing distance
        assert ascent is not None
        assert ascent.distance_mi is None

    def test_parse_ascent_detail_duration_no_match(self):
        """Test parsing duration when format doesn't match."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Duration:</b></td><td>Unknown</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle missing duration
        assert ascent is not None
        assert ascent.duration_hours is None

    def test_parse_ascent_detail_duration_hm_format(self):
        """Test parsing duration in H:MM format."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Duration:</b></td><td>4:30</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should parse H:MM format
        assert ascent is not None
        assert ascent.duration_hours == 4.5

    def test_parse_ascent_detail_attribute_error(self):
        """Test handling of AttributeError during parsing."""
        # Malformed HTML
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle AttributeError gracefully
        assert ascent is None or isinstance(ascent.ascent_id, str)

    def test_parse_ascent_detail_value_error(self):
        """Test handling of ValueError during parsing."""
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        <table class="gray" width="49%" align="left">
            <tr><td><b>Elevation:</b></td><td>Invalid ft / Invalid m</td></tr>
        </table>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle ValueError gracefully
        assert ascent is None or ascent.elevation_ft is None

    def test_parse_ascent_detail_type_error(self):
        """Test handling of TypeError during parsing."""
        # Empty HTML that might cause TypeError
        html = """
        <html><body>
        <h1>Ascent of Test Peak on 2024-01-01</h1>
        <h2>Climber: <a href="climber.aspx?cid=456">John Doe</a></h2>
        </body></html>
        """
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should handle TypeError gracefully
        assert ascent is None

    def test_parse_ascent_detail_generic_exception(self):
        """Test handling of unexpected exceptions during parsing."""
        # Completely empty HTML
        html = ""
        ascent = PeakBaggerScraper.parse_ascent_detail(html, "123")

        # Should return None on unexpected errors
        assert ascent is None
