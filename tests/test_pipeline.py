import os
import sqlite3
import pandas as pd
from unittest.mock import patch
from ingestion.extract import extract_incidents
from ingestion.clean import clean_data
from ingestion.normalize import normalize_data
from ingestion.load import load_data

def test_full_pipeline_integration(tmp_path):
    # Setup dummy raw data paths using tmp_path isolating the test
    raw_dir = tmp_path / "data" / "raw"
    db_dir = tmp_path / "data"
    mappings_dir = tmp_path / "data" / "mappings"
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(db_dir, exist_ok=True)
    os.makedirs(mappings_dir, exist_ok=True)

    # 1. Mock the company and country mapping files
    pd.DataFrame({
        'alias_of': ['fake open ai'],
        'canonical_name': ['OpenAI']
    }).to_csv(mappings_dir / "company_aliases.csv", index=False)
    
    pd.DataFrame({
        'country_name': ['United States'],
        'iso_code': ['USA']
    }).to_csv(mappings_dir / "country_codes.csv", index=False)

    # 2. Create fixture XLSX as it would be fetched from Google Sheets
    fixture_df = pd.DataFrame([
        # Headers (row 0 in pandas, read without headers first)
        ['Record ID', 'Headline', 'Date', 'Deployer', 'Developer', 'System', 'Tech', 'Purpose', 'News', 'Ethics', 'Countries', 'Sectors', 'Harm Indiv', 'Harm Soc', 'Harm Env', 'Cons', 'Resp', 'URL'],
        ['AIAAIC001', 'Test Incident 1', '2022-01-01', 'Fake Open AI', 'Fake Open AI', 'GPT', 'LLM', 'AI', 'N', 'E', 'United States', 'Healthcare; Education', 'Bias', 'Privacy', '', 'C', 'R', 'https://t.co'],
        ['AIAAIC002', 'Test Incident 2', '2023', 'Another Corp', '', 'Sys', 'Robotics', 'Mfg', 'N', 'E', 'Germany', 'Manufacturing', '', '', 'Pollution', 'C', 'R', 'https://t.co'],
    ])
    
    # Needs to be saved as exactly what the extract layer expects structure-wise
    temp_xlsx = raw_dir / "temp_aiaaic.xlsx"
    with pd.ExcelWriter(temp_xlsx) as writer:
        fixture_df.to_excel(writer, sheet_name='Incidents', index=False, header=False)


    # Run Pipeline dynamically passing our temporary paths
    extract_out = str(raw_dir / 'aiaaic_incidents.csv')
    extract_incidents(excel_path=str(temp_xlsx), csv_path=extract_out)

    clean_out = str(raw_dir / 'aiaaic_cleaned.csv')
    clean_data(raw_path=extract_out, out_path=clean_out)
    
    norm_out = str(raw_dir / 'aiaaic_normalized.csv')
    normalize_data(cleaned_path=clean_out, out_path=norm_out, mappings_dir=str(mappings_dir))
    
    db_path = str(db_dir / 'incidents.db')
    load_data(normalized_path=norm_out, db_path=db_path)

    # Assertions on pipeline generated database
    conn = sqlite3.connect(db_path)

    c = conn.cursor()
    
    # 2 Incidents total loaded
    assert c.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 2
    # Verify titles
    titles = [row[0] for row in c.execute("SELECT title FROM incidents ORDER BY incident_id").fetchall()]
    assert titles == ['Test Incident 1', 'Test Incident 2']
    
    # 3 Sectors
    sectors = [row[0] for row in c.execute("SELECT name FROM sectors ORDER BY name").fetchall()]
    assert sectors == ['Education', 'Healthcare', 'Manufacturing']
    
    # Verify OpenAI alias was resolved
    companies = [row[0] for row in c.execute("SELECT canonical_name FROM companies").fetchall()]
    assert len(companies) > 0
    
    # Verify Country ISO code USA maps accurately
    countries = c.execute("SELECT name, iso_code FROM countries WHERE iso_code='USA'").fetchone()
    assert countries[0] == "United States"
    assert countries[1] == "USA"
    
    conn.close()
