import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import os
from pathlib import Path  # noqa: F811 – re-import after sys.path fix
from app.components.filters import render_global_sidebar
from core.queries import get_metadata

st.set_page_config(page_title="Methodology", page_icon="📚", layout="wide")

st.title("📚 Methodology & Terms")
st.markdown("___")

metadata_df = get_metadata()
if metadata_df is not None and not metadata_df.empty:
    meta_dict = dict(zip(metadata_df['key'], metadata_df['value']))
    st.info(f"**Database Last Refreshed:** {meta_dict.get('last_refreshed_at', 'Unknown')} \n\n"
            f"**Usage Terms:** {meta_dict.get('usage_terms', 'Public-interest use only.')} \n\n"
            f"**License:** {meta_dict.get('license', 'CC BY-SA 4.0')}")

# Load and render METHODOLOGY.md
project_root = Path(__file__).resolve().parent.parent.parent
methodology_path = project_root / "docs" / "METHODOLOGY.md"

try:
    with open(methodology_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    st.markdown(md_content)
except FileNotFoundError:
    st.warning("METHODOLOGY.md file could not be found.")
