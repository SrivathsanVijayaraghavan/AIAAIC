"""
Offline ingestion pipeline: fetch -> extract -> clean -> normalize -> load.

Run manually to refresh data/incidents.db. Not invoked at Streamlit runtime.
"""

from ingestion.clean import clean_data
from ingestion.extract import extract_incidents
from ingestion.fetch import fetch_aiaaic_data, print_usage_reminder
from ingestion.load import load_data
from ingestion.normalize import normalize_data
from ingestion.sources import AIAAIC_SOURCE


def run_pipeline() -> None:
    print("=" * 60)
    print("AI Incident Analytics — ingestion pipeline")
    print("=" * 60)
    print_usage_reminder()
    print()

    fetch_aiaaic_data()
    extract_incidents()
    clean_data()
    normalize_data()
    load_data(source=AIAAIC_SOURCE)

    print()
    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()
