# Methodology & Data Caveats

## Data source

This dashboard ingests the **AIAAIC Repository** — an independent, grassroots,
public-interest collection of AI, algorithmic, and automation incidents and
controversies.

| Item | Value |
|---|---|
| Canonical page | https://www.aiaaic.org/aiaaic-repository |
| User guide | https://www.aiaaic.org/aiaaic-repository/user-guide |
| Machine-readable format | Google Sheets spreadsheet (Incidents tab) |
| Refresh cadence (v1) | Manual — re-run `ingestion/run_pipeline.py` |

The spreadsheet ID is maintained in `ingestion/sources.py` and was verified
against AIAAIC's user guide, third-party academic citations, and a live export
test. If ingestion fails, re-check the user guide before updating the ID.

## Licensing and terms of use

AIAAIC content is available under **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**.

Additional restrictions from the [AIAAIC user guide](https://www.aiaaic.org/aiaaic-repository/user-guide):

- Data should be used **substantially in the public interest** (UK Data Protection Act 2018 framing).
- Data must **not** be adapted or redistributed for **commercial purposes** (e.g. risk-management or text-analysis products).
- Adapted or remixed work must be **republished under CC BY-SA 4.0** with attribution to the AIAAIC Repository.

**Attribution requirement for this dashboard:** cite the [AIAAIC Repository](https://www.aiaaic.org/aiaaic-repository) with a prominent link when publishing findings derived from this tool.

## Platform limitations

The repository exists on **two platforms** (website + spreadsheet). As of the
November 2025 user-guide update, the former "Premium Membership" tier for
hidden impact/collection fields has been **removed**. Some fields may still be
sparse or absent on individual records — the schema tolerates nulls rather than
dropping incidents.

Fields we ingest from the public Incidents sheet include sector, jurisdiction,
harm taxonomies, companies, and source links. We do **not** assume access to
any non-public or website-only fields.

## Known data biases and caveats

Per AIAAIC's own guidance, treat quantitative results carefully:

1. **Not comprehensive** — coverage has geographic and topical gaps.
2. **Media-driven selection** — incidents typically require mainstream media coverage unless the source is highly credible.
3. **English-language bias** — most entries draw on English-language reporting.
4. **Taxonomy overlaps** — harm types, sectors, and ethical issues are non-hierarchical and may overlap.
5. **Inconsistent nomenclature** — company names, countries, and dates vary in quality; we apply normalization but cannot eliminate all ambiguity.
6. **Multi-valued fields** — one incident may map to multiple sectors, harms, or countries; counts are **tag-level** (a single incident can increment multiple categories).

## How we define metrics

| Metric | Definition |
|---|---|
| **Incident count** | One row per AIAAIC record ID in the Incidents sheet |
| **Sector / harm / country counts** | Junction-table counts; multi-tagged incidents contribute to each tag |
| **Company counts** | Separate tallies for Developer and Deployer roles |
| **Year trends** | Based on the `Occurred` field; year-only values default to Jan 1; missing dates excluded from time-series |
| **Top sector / harm** | Highest junction-table frequency under current filters |

## Export scope (v1)

v1 supports **CSV export only** of the currently filtered incident set.
PDF export is deferred to a future release (requires a separate rendering library).

## Refresh metadata

The `_metadata` table in `data/incidents.db` stores `last_refreshed_at`,
`total_incidents`, `source_url`, and `license` from the most recent pipeline run.
