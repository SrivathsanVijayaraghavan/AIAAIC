import pandas as pd
import os

def extract_incidents(
    excel_path='data/raw/temp_aiaaic.xlsx', 
    csv_path='data/raw/aiaaic_incidents.csv'
):
    print("Reading 'Incidents' sheet from excel...")
    # Read without header then slice
    df = pd.read_excel(excel_path, sheet_name='Incidents', header=None)
    
    # The actual data seems to start at row index 2 (or row index 3 if there's a blank). We saw data started with AIAAIC2264
    # We can filter out rows that don't look like AIAAIC IDs in column 0
    df = df[df[0].astype(str).str.startswith('AIAAIC')]
    
    # Rename columns by index explicitly
    col_names = {
        0: 'aiaaic_record_id',
        1: 'title',
        2: 'incident_date',
        3: 'deployer_companies',
        4: 'developer_companies',
        5: 'system_name',
        6: 'technology',
        7: 'purpose',
        8: 'news_trigger',
        9: 'ethical_issue',
        10: 'countries',
        11: 'sectors',
        12: 'harm_type_individual',
        13: 'harm_type_societal',
        14: 'harm_type_environmental',
        15: 'consequences',
        16: 'responses',
        17: 'source_url'
    }
    
    # Drop any extra columns beyond 17
    df = df.drop(columns=[col for col in df.columns if col not in col_names])
    df = df.rename(columns=col_names)
        
    df.to_csv(csv_path, index=False)
    print(f"Extraction successful: {len(df)} rows saved to {csv_path}")

if __name__ == "__main__":
    extract_incidents()
