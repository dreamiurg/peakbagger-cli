"""PeakBagger - Python library and CLI for PeakBagger.com data.

Quick start::

    from peakbagger import PeakBagger

    with PeakBagger() as pb:
        results = pb.search("Mount Rainier")
        peak = pb.get_peak("2296")
        ascents = pb.get_ascents("2296")
        ascent = pb.get_ascent("12963")
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("peakbagger")
except PackageNotFoundError:
    # Package is not installed (e.g., running from source during development)
    __version__ = "0.0.0.dev"

from peakbagger.api import PeakBagger
from peakbagger.models import Ascent, AscentStatistics, Peak, SearchResult

__all__ = [
    "Ascent",
    "AscentStatistics",
    "Peak",
    "PeakBagger",
    "SearchResult",
    "__version__",
]
