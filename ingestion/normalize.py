import pandas as pd
import pycountry
import os

def normalize_data(
    cleaned_path="data/raw/aiaaic_cleaned.csv", 
    out_path="data/raw/aiaaic_normalized.csv",
    mappings_dir="data/mappings"
):
    print("Normalizing data...")
    df = pd.read_csv(cleaned_path)
    
    df = df.fillna('')
    
    # Load aliases
    company_aliases_path = os.path.join(mappings_dir, 'company_aliases.csv')
    company_aliases = pd.read_csv(company_aliases_path)
    alias_dict = dict(zip(company_aliases['alias_of'].str.lower(), company_aliases['canonical_name']))
    
    def resolve_companies(comp_str):
        comp_str = str(comp_str)
        if not comp_str.strip():
            return ""
        comps = [c.strip() for c in comp_str.split(';') if c.strip()]
        resolved = []
        for c in comps:
            r = alias_dict.get(c.lower(), c)
            resolved.append(r)
        return '; '.join(list(set(resolved)))
        
    if 'deployer_companies' in df.columns:
        df['deployer_companies'] = df['deployer_companies'].apply(resolve_companies)
    if 'developer_companies' in df.columns:
        df['developer_companies'] = df['developer_companies'].apply(resolve_companies)
    
    # Country ISO mapping
    country_codes_path = os.path.join(mappings_dir, 'country_codes.csv')
    country_overrides_df = pd.read_csv(country_codes_path)
    country_overrides = dict(zip(country_overrides_df['country_name'].str.lower(), country_overrides_df['iso_code']))
    
    
    def map_country(c):
        c = c.strip()
        cl = c.lower()
        if cl in country_overrides:
            return country_overrides[cl]
        try:
            return pycountry.countries.search_fuzzy(c)[0].alpha_3
        except:
            return ""
            
    def resolve_countries(c_str):
        c_str = str(c_str)
        if not c_str.strip():
            return ""
        countries = [c.strip() for c in c_str.split(';') if c.strip()]
        resolved = set()
        for c in countries:
            iso = map_country(c)
            if iso: resolved.add(iso)
        return '; '.join(list(resolved))
        
    if 'countries' in df.columns:
        df['countries_iso'] = df['countries'].apply(resolve_countries)
    
    df.to_csv(out_path, index=False)
    print(f"Normalized data saved to {out_path}")
    return out_path

if __name__ == "__main__":
    normalize_data()
