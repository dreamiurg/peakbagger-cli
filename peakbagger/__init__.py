"""PeakBagger CLI - A command-line interface for PeakBagger.com"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("peakbagger")
except PackageNotFoundError:
    # Package is not installed (e.g., running from source during development)
    __version__ = "0.0.0.dev"
