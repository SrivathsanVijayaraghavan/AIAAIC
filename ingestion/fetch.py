import os

import requests

from ingestion.sources import AIAAIC_SOURCE, USAGE_TERMS_SUMMARY


def fetch_aiaaic_data(
    out_path: str = "data/raw/temp_aiaaic.xlsx",
    source=AIAAIC_SOURCE,
) -> str:
    """
    Download the latest AIAAIC spreadsheet export.

    Source URLs are defined in ingestion/sources.py and must be re-verified
    against https://www.aiaaic.org/aiaaic-repository/user-guide if this fails.
    """
    url = source.xlsx_export_url
    print(f"Fetching {source.name} from documented export URL...")
    print(f"Canonical source: {source.canonical_page_url}")
    print(f"License: {source.license} (public-interest use; see METHODOLOGY.md)")

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to fetch AIAAIC data from {url}. "
            f"Re-check the spreadsheet ID in ingestion/sources.py against "
            f"{source.user_guide_url}. Original error: {exc}"
        ) from exc

    content_type = response.headers.get("content-type", "")
    if "spreadsheet" not in content_type and "octet-stream" not in content_type:
        raise RuntimeError(
            f"Unexpected response type '{content_type}' from {url}. "
            "The spreadsheet ID may have changed or access may be restricted."
        )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(response.content)

    print(f"Saved raw export ({len(response.content):,} bytes) to {out_path}")
    return out_path


def print_usage_reminder() -> None:
    print(USAGE_TERMS_SUMMARY)


if __name__ == "__main__":
    print_usage_reminder()
    fetch_aiaaic_data()
