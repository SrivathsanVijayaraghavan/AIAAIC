"""
Tests for core.queries — these now run without a Streamlit context
since the core layer has zero Streamlit imports.
"""
from core.queries import (
    get_stats_overview,
    get_incidents_by_year,
    get_incidents_list,
    get_incidents_export,
    get_stats_by_sector,
    get_stats_by_harm_type,
    get_stats_by_country,
    get_stats_by_company,
    get_sector_harm_matrix,
    get_yoy_sector_trends,
    get_yoy_harm_trends,
    get_available_filter_options,
    get_metadata,
)

def test_get_stats_overview():
    res = get_stats_overview()
    assert res is not None
    assert 'total_incidents' in res
    assert res['total_incidents'] > 0

def test_get_stats_overview_with_filters():
    # Empty query should not error
    res_empty_db = get_stats_overview(filters={"start_year": 2999})
    assert res_empty_db is not None
    assert res_empty_db['total_incidents'] == 0

def test_get_incidents_by_year():
    res = get_incidents_by_year()
    assert not res.empty
    assert 'year' in res.columns
    assert 'count' in res.columns

def test_get_incidents_list():
    res = get_incidents_list(limit=5)
    assert not res.empty
    assert len(res) <= 5
    assert 'title' in res.columns

def test_get_incidents_list_empty_search():
    res = get_incidents_list(limit=5, search_term="")
    assert not res.empty

def test_get_incidents_list_search():
    """Test that LOWER()-based search works."""
    res = get_incidents_list(limit=10, search_term="AI")
    assert 'title' in res.columns

def test_get_incidents_export():
    res = get_incidents_export(search_term="AI")
    assert 'title' in res.columns
    assert 'aiaaic_record_id' in res.columns

def test_get_stats_by_sector():
    res = get_stats_by_sector()
    assert not res.empty
    assert 'sector' in res.columns

def test_get_stats_by_sector_filtered():
    res = get_stats_by_sector(filters={"start_year": 2020})
    assert not res.empty

def test_get_stats_by_harm_type():
    res = get_stats_by_harm_type()
    assert not res.empty
    assert 'harm_type' in res.columns

def test_get_stats_by_country():
    res = get_stats_by_country()
    assert not res.empty
    assert 'name' in res.columns

def test_get_stats_by_company():
    res = get_stats_by_company()
    assert not res.empty
    assert 'company' in res.columns

def test_get_stats_by_company_roles():
    res_dev = get_stats_by_company(role="Developer")
    res_dep = get_stats_by_company(role="Deployer")
    # Just checking it executes correctly
    assert 'company' in res_dev.columns
    assert 'company' in res_dep.columns

def test_get_sector_harm_matrix():
    res = get_sector_harm_matrix()
    assert not res.empty
    assert 'sector' in res.columns
    assert 'harm_type' in res.columns

def test_get_yoy_sector_trends():
    res = get_yoy_sector_trends()
    assert not res.empty
    assert 'year' in res.columns
    assert 'sector' in res.columns

def test_get_yoy_harm_trends():
    res = get_yoy_harm_trends()
    assert not res.empty
    assert 'year' in res.columns
    assert 'harm_type' in res.columns

def test_get_available_filter_options():
    sectors, harms = get_available_filter_options()
    assert isinstance(sectors, list)
    assert isinstance(harms, list)

def test_get_metadata():
    res = get_metadata()
    assert not res.empty
