import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

import pycountry

from ingestion.sources import AIAAIC_SOURCE


def load_data(
    normalized_path="data/raw/aiaaic_normalized.csv",
    db_path="data/incidents.db",
    source=AIAAIC_SOURCE,
):
    print("Loading data to SQLite...")
    df = pd.read_csv(normalized_path)
    df = df.fillna('')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create Schema
    cursor.executescript('''
        DROP TABLE IF EXISTS incidents;
        DROP TABLE IF EXISTS sectors;
        DROP TABLE IF EXISTS harm_types;
        DROP TABLE IF EXISTS companies;
        DROP TABLE IF EXISTS countries;
        DROP TABLE IF EXISTS incident_sectors;
        DROP TABLE IF EXISTS incident_harm_types;
        DROP TABLE IF EXISTS incident_companies;
        DROP TABLE IF EXISTS incident_countries;
        DROP TABLE IF EXISTS _metadata;
        
        CREATE TABLE incidents (
            incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            incident_date DATE,
            source_url TEXT,
            aiaaic_record_id TEXT,
            ingested_at DATETIME
        );
        CREATE TABLE sectors (sector_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
        CREATE TABLE harm_types (harm_type_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE);
        CREATE TABLE companies (company_id INTEGER PRIMARY KEY AUTOINCREMENT, canonical_name TEXT UNIQUE);
        CREATE TABLE countries (country_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, iso_code TEXT UNIQUE);
        
        CREATE TABLE incident_sectors (incident_id INTEGER, sector_id INTEGER, FOREIGN KEY(incident_id) REFERENCES incidents(incident_id), FOREIGN KEY(sector_id) REFERENCES sectors(sector_id));
        CREATE TABLE incident_harm_types (incident_id INTEGER, harm_type_id INTEGER, FOREIGN KEY(incident_id) REFERENCES incidents(incident_id), FOREIGN KEY(harm_type_id) REFERENCES harm_types(harm_type_id));
        CREATE TABLE incident_companies (incident_id INTEGER, company_id INTEGER, role TEXT, FOREIGN KEY(incident_id) REFERENCES incidents(incident_id), FOREIGN KEY(company_id) REFERENCES companies(company_id));
        CREATE TABLE incident_countries (incident_id INTEGER, country_id INTEGER, FOREIGN KEY(incident_id) REFERENCES incidents(incident_id), FOREIGN KEY(country_id) REFERENCES countries(country_id));
        
        CREATE TABLE _metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        );

        -- Indexes for junction table foreign keys
        CREATE INDEX idx_incident_sectors_sector ON incident_sectors(sector_id);
        CREATE INDEX idx_incident_sectors_incident ON incident_sectors(incident_id);
        CREATE INDEX idx_incident_harm_types_harm ON incident_harm_types(harm_type_id);
        CREATE INDEX idx_incident_harm_types_incident ON incident_harm_types(incident_id);
        CREATE INDEX idx_incident_companies_company ON incident_companies(company_id);
        CREATE INDEX idx_incident_companies_incident ON incident_companies(incident_id);
        CREATE INDEX idx_incident_countries_country ON incident_countries(country_id);
        CREATE INDEX idx_incident_countries_incident ON incident_countries(incident_id);
        CREATE INDEX idx_incidents_date ON incidents(incident_date);
    ''')
    
    _VALID_TABLES = {
        'sectors': ('sector_id', 'name'),
        'harm_types': ('harm_type_id', 'name'),
        'companies': ('company_id', 'canonical_name'),
        'countries': ('country_id', 'iso_code'),
    }

    # Helper to insert and get ID
    def get_or_create(table, id_col, column, value, extra_col=None, extra_val=None):
        if not value or not str(value).strip(): return None
        value = str(value).strip()
        
        # Validation to prevent SQL injection from programmatic schema misuse
        if table not in _VALID_TABLES:
            raise ValueError(f"Invalid table: {table}")
        if _VALID_TABLES[table] != (id_col, column):
            raise ValueError(f"Invalid table columns provided for {table}")
        if extra_col and extra_col not in ['name']:  # currently only countries has an extra_col
            raise ValueError(f"Invalid extra_col: {extra_col}")

        # Now safe to interpolate
        cursor.execute(f"SELECT {id_col} FROM {table} WHERE {column} = ?", (value,))
        res = cursor.fetchone()
        if res: return res[0]
        
        if extra_col and extra_val:
            cursor.execute(f"INSERT INTO {table} ({column}, {extra_col}) VALUES (?, ?)", (value, extra_val))
        else:
            cursor.execute(f"INSERT INTO {table} ({column}) VALUES (?)", (value,))
        return cursor.lastrowid
        
    ingested_at = datetime.now().isoformat()
    
    total_added = 0
    # Process rows
    for idx, row in df.iterrows():
        date_val = row.get('incident_date', '')
        if not str(date_val).strip(): date_val = None
        
        cursor.execute('''
            INSERT INTO incidents (title, incident_date, source_url, aiaaic_record_id, ingested_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (row.get('title',''), date_val, row.get('source_url', ''), row.get('aiaaic_record_id', ''), ingested_at))
        inc_id = cursor.lastrowid
        total_added += 1
        
        # Sectors
        for s in str(row.get('sectors','')).split(';'):
            s_id = get_or_create('sectors', 'sector_id', 'name', s)
            if s_id: cursor.execute("INSERT INTO incident_sectors VALUES (?, ?)", (inc_id, s_id))
            
        # Harm Types
        for h in str(row.get('combined_harm_types','')).split(';'):
            h_id = get_or_create('harm_types', 'harm_type_id', 'name', h)
            if h_id: cursor.execute("INSERT INTO incident_harm_types VALUES (?, ?)", (inc_id, h_id))
            
        # Companies
        for c in str(row.get('deployer_companies','')).split(';'):
            c_id = get_or_create('companies', 'company_id', 'canonical_name', c)
            if c_id: cursor.execute("INSERT INTO incident_companies VALUES (?, ?, ?)", (inc_id, c_id, 'Deployer'))
        for c in str(row.get('developer_companies','')).split(';'):
            c_id = get_or_create('companies', 'company_id', 'canonical_name', c)
            if c_id: cursor.execute("INSERT INTO incident_companies VALUES (?, ?, ?)", (inc_id, c_id, 'Developer'))
            
        # Countries
        for iso in str(row.get('countries_iso','')).split(';'):
            iso = iso.strip()
            # Resolve human-readable country name from ISO code
            country_name = iso  # fallback
            try:
                country_obj = pycountry.countries.get(alpha_3=iso)
                if country_obj:
                    country_name = country_obj.name
            except Exception:
                pass
            c_id = get_or_create('countries', 'country_id', 'iso_code', iso, 'name', country_name)
            if c_id: cursor.execute("INSERT INTO incident_countries VALUES (?, ?)", (inc_id, c_id))

    metadata = {
        "total_incidents": str(total_added),
        "last_refreshed_at": ingested_at,
        "source_url": source.canonical_page_url,
        "source_spreadsheet_id": source.spreadsheet_id,
        "license": source.license,
        "usage_terms": "Public-interest use only; not for commercial redistribution.",
    }
    for key, value in metadata.items():
        cursor.execute("INSERT INTO _metadata (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    conn.close()
    print(f"Data loaded to SQLite. Total incidents: {total_added}")

if __name__ == "__main__":
    load_data()
