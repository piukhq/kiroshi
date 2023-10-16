"""Configuration for tests."""

from pytest_html import report as pytest_report


def pytest_html_report_title(report: pytest_report) -> None:
    """Configure the HTML Report Title."""
    report.title = "Kiroshi Image Server Tests"
