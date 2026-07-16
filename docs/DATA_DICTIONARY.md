# AIAAIC Data Dictionary & Mapping

This document maps the raw Google Sheets columns to our SQLite schema.

## Source verification

The spreadsheet export URL is defined in `ingestion/sources.py` (not hardcoded
in fetch logic). It was verified against:

- [AIAAIC user guide](https://www.aiaaic.org/aiaaic-repository/user-guide) — references downloading the spreadsheet
- Academic/third-party citations of the same spreadsheet ID
- Live export test returning a valid XLSX payload

Re-verify against the user guide if ingestion fails. Licensing and usage
constraints are documented in `docs/METHODOLOGY.md`.

## Raw Source (Incidents Sheet)
The raw dataset has a two-row header structure located at rows index 1 and 2 in the Excel file.

| Excel Column Index | Raw Column Name (Row 1/2) | Target SQLite Field (`incidents` / junction tables) | Notes |
|---|---|---|---|
| 0 | `AIAAIC ID#` | `aiaaic_record_id` | Primary reference |
| 1 | `Headline` | `title`, `description` | We use this as the title (and short description) |
| 2 | `Occurred` | `incident_date` | Often just a year. Requires normalization to standard date (e.g. YYYY-01-01) |
| 3 | `Deployer` | `incident_companies` (role='Deployer') | Multi-valued |
| 4 | `Developer` | `incident_companies` (role='Developer') | Multi-valued |
| 10 | `Jurisdiction` (under Impacted area) | `incident_countries` | Multi-valued |
| 11 | `Sector` (under Impacted area) | `incident_sectors` | Multi-valued |
| 12 | `Individual` (under External harm) | `incident_harm_types` | Multi-valued (Needs parsing) |
| 13 | `Societal` (under External harm) | `incident_harm_types` | Multi-valued (Needs parsing) |
| 14 | `Environmental` (under External harm) | `incident_harm_types` | Multi-valued (Needs parsing) |
| 17 | `Summary/links` | `source_url` | Single or multiple URLs |

## Null/Missing Field Handling
As per the AIAAIC ToU and public access limits, some fields on "impacts" and "collections" may be missing due to premium tier restrictions. The database schema accepts nulls for all analytical dimension tables. Any multi-valued fields parsed will drop empty/NaN segments safely.
