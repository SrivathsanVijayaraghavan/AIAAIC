import pandas as pd
from core.db import execute_query

def _build_filter_sql(filters, table_alias="i"):
    """
    Builds the WHERE clause and params for global filters.
    """
    if not filters:
        return "", []
    
    where_clauses = []
    params = []
    
    if filters.get("start_year"):
        where_clauses.append(f"strftime('%Y', {table_alias}.incident_date) >= ?")
        params.append(str(filters["start_year"]))
        
    if filters.get("end_year"):
        where_clauses.append(f"strftime('%Y', {table_alias}.incident_date) <= ?")
        params.append(str(filters["end_year"]))
        
    if filters.get("sectors") and len(filters["sectors"]) > 0:
        placeholders = ",".join("?" for _ in filters["sectors"])
        where_clauses.append(f"{table_alias}.incident_id IN (SELECT isec.incident_id FROM incident_sectors isec JOIN sectors s ON isec.sector_id = s.sector_id WHERE s.name IN ({placeholders}))")
        params.extend(filters["sectors"])
        
    if filters.get("harm_types") and len(filters["harm_types"]) > 0:
        placeholders = ",".join("?" for _ in filters["harm_types"])
        where_clauses.append(f"{table_alias}.incident_id IN (SELECT iharm.incident_id FROM incident_harm_types iharm JOIN harm_types h ON iharm.harm_type_id = h.harm_type_id WHERE h.name IN ({placeholders}))")
        params.extend(filters["harm_types"])
        
    if not where_clauses:
        return "", []
        
    return " AND " + " AND ".join(where_clauses), params


def get_stats_overview(filters=None):
    """
    Returns summary statistics for the dashboard based on filters.
    """
    filt_sql, params = _build_filter_sql(filters, "i")
    
    query = f'''
    WITH filtered_incidents AS (
        SELECT i.incident_id, i.incident_date FROM incidents i
        WHERE 1=1 {filt_sql}
    )
    SELECT 
        (SELECT COUNT(*) FROM filtered_incidents) as total_incidents,
        (SELECT MIN(strftime('%Y', incident_date)) FROM filtered_incidents WHERE incident_date IS NOT NULL) as min_year,
        (SELECT MAX(strftime('%Y', incident_date)) FROM filtered_incidents WHERE incident_date IS NOT NULL) as max_year,
        (SELECT s.name 
         FROM filtered_incidents fi 
         JOIN incident_sectors iss ON fi.incident_id = iss.incident_id 
         JOIN sectors s ON iss.sector_id = s.sector_id 
         GROUP BY s.name ORDER BY COUNT(*) DESC LIMIT 1) as top_sector,
        (SELECT h.name 
         FROM filtered_incidents fi 
         JOIN incident_harm_types ih ON fi.incident_id = ih.incident_id 
         JOIN harm_types h ON ih.harm_type_id = h.harm_type_id 
         GROUP BY h.name ORDER BY COUNT(*) DESC LIMIT 1) as top_harm_type
    '''
    
    # We duplicate params for each subselect that uses filtered_incidents if we were using text insertion, 
    # but WITH clause handles it at the top level! 
    df = execute_query(query, tuple(params))
    return df.iloc[0] if not df.empty else None


def get_incidents_by_year(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT strftime('%Y', i.incident_date) as year, COUNT(*) as count 
    FROM incidents i
    WHERE i.incident_date IS NOT NULL {filt_sql}
    GROUP BY year 
    ORDER BY year ASC
    '''
    return execute_query(query, tuple(params))


def get_incidents_list(limit=1000, offset=0, search_term=None, filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    
    base_query = f"SELECT i.incident_id, i.title, i.incident_date, i.source_url, i.aiaaic_record_id FROM incidents i WHERE 1=1 {filt_sql}"
    
    if search_term:
        base_query += " AND LOWER(i.title) LIKE LOWER(?)"
        params.append(f"%{search_term}%")
        
    base_query += " ORDER BY i.incident_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return execute_query(base_query, tuple(params))


def get_incidents_export(search_term=None, filters=None):
    """
    Returns full incident list suitable for CSV export (no pagination limit).
    """
    filt_sql, params = _build_filter_sql(filters, "i")
    
    base_query = f"SELECT i.incident_id, i.aiaaic_record_id, i.title, i.incident_date, i.source_url FROM incidents i WHERE 1=1 {filt_sql}"
    
    if search_term:
        base_query += " AND LOWER(i.title) LIKE LOWER(?)"
        params.append(f"%{search_term}%")
        
    base_query += " ORDER BY i.incident_date DESC"
    
    return execute_query(base_query, tuple(params))


def get_stats_by_sector(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT s.name as sector, COUNT(iss.incident_id) as count 
    FROM incidents i
    JOIN incident_sectors iss ON i.incident_id = iss.incident_id
    JOIN sectors s ON iss.sector_id = s.sector_id 
    WHERE 1=1 {filt_sql}
    GROUP BY s.name 
    ORDER BY count DESC
    '''
    return execute_query(query, tuple(params))


def get_stats_by_harm_type(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT h.name as harm_type, COUNT(ih.incident_id) as count 
    FROM incidents i
    JOIN incident_harm_types ih ON i.incident_id = ih.incident_id
    JOIN harm_types h ON ih.harm_type_id = h.harm_type_id 
    WHERE 1=1 {filt_sql}
    GROUP BY h.name 
    ORDER BY count DESC
    '''
    return execute_query(query, tuple(params))


def get_stats_by_country(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT c.name, c.iso_code, COUNT(ic.incident_id) as count 
    FROM incidents i
    JOIN incident_countries ic ON i.incident_id = ic.incident_id
    JOIN countries c ON ic.country_id = c.country_id 
    WHERE 1=1 {filt_sql}
    GROUP BY c.iso_code, c.name 
    ORDER BY count DESC
    '''
    return execute_query(query, tuple(params))


def get_stats_by_company(role=None, filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT c.canonical_name as company, COUNT(ic.incident_id) as count 
    FROM incidents i
    JOIN incident_companies ic ON i.incident_id = ic.incident_id
    JOIN companies c ON ic.company_id = c.company_id 
    WHERE 1=1 {filt_sql}
    '''
    if role:
        query += ' AND ic.role = ? '
        params.append(role)
        
    query += ' GROUP BY c.canonical_name ORDER BY count DESC LIMIT 50'
    return execute_query(query, tuple(params))


def get_sector_harm_matrix(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT 
        s.name as sector, 
        h.name as harm_type, 
        COUNT(DISTINCT i.incident_id) as count
    FROM incidents i
    JOIN incident_sectors isec ON i.incident_id = isec.incident_id
    JOIN sectors s ON isec.sector_id = s.sector_id
    JOIN incident_harm_types iharm ON i.incident_id = iharm.incident_id
    JOIN harm_types h ON iharm.harm_type_id = h.harm_type_id
    WHERE 1=1 {filt_sql}
    GROUP BY s.name, h.name
    HAVING count > 0
    '''
    return execute_query(query, tuple(params))


def get_yoy_sector_trends(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT 
        strftime('%Y', i.incident_date) as year, 
        s.name as sector, 
        COUNT(isec.incident_id) as count
    FROM incidents i
    JOIN incident_sectors isec ON i.incident_id = isec.incident_id
    JOIN sectors s ON isec.sector_id = s.sector_id
    WHERE i.incident_date IS NOT NULL {filt_sql}
    GROUP BY year, s.name
    HAVING count > 0
    ORDER BY year ASC, count DESC
    '''
    return execute_query(query, tuple(params))


def get_yoy_harm_trends(filters=None):
    filt_sql, params = _build_filter_sql(filters, "i")
    query = f'''
    SELECT 
        strftime('%Y', i.incident_date) as year, 
        h.name as harm_type, 
        COUNT(iharm.incident_id) as count
    FROM incidents i
    JOIN incident_harm_types iharm ON i.incident_id = iharm.incident_id
    JOIN harm_types h ON iharm.harm_type_id = h.harm_type_id
    WHERE i.incident_date IS NOT NULL {filt_sql}
    GROUP BY year, h.name
    HAVING count > 0
    ORDER BY year ASC, count DESC
    '''
    return execute_query(query, tuple(params))


def get_available_filter_options():
    """
    Returns unique values for sectors, harm_types for populating the filter UI.
    """
    sectors = execute_query("SELECT name FROM sectors ORDER BY name")['name'].tolist()
    harms = execute_query("SELECT name FROM harm_types ORDER BY name")['name'].tolist()
    return sectors, harms

def get_metadata():
    """Returns database metadata"""
    return execute_query("SELECT key, value FROM _metadata")
