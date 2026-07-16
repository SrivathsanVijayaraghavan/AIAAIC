import pandas as pd
import numpy as np

def clean_data(raw_path="data/raw/aiaaic_incidents.csv", out_path="data/raw/aiaaic_cleaned.csv"):
    """
    Cleans raw incident data by standardizing dates and unifying harm columns.
    """
    print(f"Loading raw data from {raw_path}")
    
    # Read the custom extracted schema 
    df = pd.read_csv(raw_path)
    
    print(f"Data shape before cleaning: {df.shape}")
    
    # Ensure there are no fully blank rows
    df = df.dropna(how='all')
    
    # Deduplicate by AIAAIC ID if it exists 
    if 'aiaaic_record_id' in df.columns:
        df = df.dropna(subset=['aiaaic_record_id'])
        df = df.drop_duplicates(subset=['aiaaic_record_id'])
        
    print(f"Data shape after deduplication: {df.shape}")
    
    # --- Clean Dates ---
    def parse_date(d):
        if pd.isna(d):
            return None
        d = str(d).strip()
        if len(d) == 4 and d.isdigit():
            # Just a year, assume Jan 1
            return f"{d}-01-01"
        try:
            return pd.to_datetime(d).strftime("%Y-%m-%d")
        except:
            # Fallback for weird strings
            return None

    if 'incident_date' in df.columns:
        df['incident_date'] = df['incident_date'].apply(parse_date)

    # --- Clean Text Fields ---
    text_cols = ['title', 'source_url', 'deployer_companies', 'developer_companies', 'countries', 'sectors']
    
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).replace('nan', '').str.strip()
            
    # --- Combine Harm Types ---
    # The raw sheet split harms by Individual, Societal, Environmental
    # We will combine them into a single comma-separated list of harm types for junction extraction
    def combine_harms(row):
        harms = []
        for col in ['harm_type_individual', 'harm_type_societal', 'harm_type_environmental']:
            if col in df.columns and pd.notna(row[col]) and str(row[col]).strip() != 'nan':
                harms.extend([h.strip() for h in str(row[col]).split(';')])
        
        # Remove empty string
        harms = [h for h in harms if h]
        return '; '.join(list(set(harms)))  # Deduplicate

    df['combined_harm_types'] = df.apply(combine_harms, axis=1)

    # Drop the temporary distinct columns
    drop_cols = ['harm_type_individual', 'harm_type_societal', 'harm_type_environmental']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])
    
    # Fill any remaining NaNs with empty strings instead of np.nan
    df = df.fillna('')
    
    df.to_csv(out_path, index=False)
    print(f"Cleaned data saved to {out_path}")
    return out_path

if __name__ == "__main__":
    clean_data()
