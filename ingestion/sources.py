"""
Verified AIAAIC data source configuration.

The spreadsheet ID below was confirmed against:
- AIAAIC user guide (https://www.aiaaic.org/aiaaic-repository/user-guide)
- Academic citations (e.g. Maastricht University, digitalresponsibility.ch)
- Live export test (HTTP 200, valid XLSX payload)

AIAAIC does not publish a single documented CSV export URL on their site.
The Google Sheet is the primary machine-readable access path referenced in
the user guide ("download the spreadsheet"). Re-verify this ID if ingestion fails.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AIAAICSource:
    name: str
    spreadsheet_id: str
    canonical_page_url: str
    user_guide_url: str
    terms_url: str
    license: str
    incidents_sheet_gid: str

    @property
    def view_url(self) -> str:
        return (
            f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit"
            f"?gid={self.incidents_sheet_gid}"
        )

    @property
    def xlsx_export_url(self) -> str:
        return (
            f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
            f"/export?format=xlsx"
        )

    @property
    def csv_export_url(self) -> str:
        return (
            f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
            f"/export?format=csv&gid={self.incidents_sheet_gid}"
        )


AIAAIC_SOURCE = AIAAICSource(
    name="AIAAIC Repository",
    spreadsheet_id="1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI",
    canonical_page_url="https://www.aiaaic.org/aiaaic-repository",
    user_guide_url="https://www.aiaaic.org/aiaaic-repository/user-guide",
    terms_url="https://www.aiaaic.org/aiaaic-repository/user-guide",
    license="CC BY-SA 4.0",
    incidents_sheet_gid="888071280",
)

USAGE_TERMS_SUMMARY = """
AIAAIC data is licensed CC BY-SA 4.0 but must be used substantially in the
public interest. Commercial redistribution or adaptation (e.g. risk-management
products) is not permitted. Adapted work must retain the same license.
See: https://www.aiaaic.org/aiaaic-repository/user-guide
""".strip()
