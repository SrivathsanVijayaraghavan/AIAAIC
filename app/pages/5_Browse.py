import streamlit as st
import pandas as pd
from core.queries import get_incidents_list, get_incidents_export
from app.components.filters import render_global_sidebar, get_current_filters, _hashable_filters

st.set_page_config(page_title="Browse Incidents", page_icon="🔍", layout="wide")
render_global_sidebar()

st.title("🔍 Browse Incidents")
st.markdown("Search and filter the raw incident database.")
st.markdown("___")

search_term = st.text_input("Search (Headline text):", "", placeholder="e.g. 'Facial recognition'")

# Export button
@st.cache_data(ttl=600, show_spinner=False)
def get_csv(search, filter_key):
    filters = dict(filter_key) if filter_key else None
    if filters:
        for k in ('sectors', 'harm_types'):
            if k in filters:
                filters[k] = list(filters[k])
    export_df = get_incidents_export(search_term=search, filters=filters)
    return export_df.to_csv(index=False).encode('utf-8')

csv_data = get_csv(search_term if search_term else None, _hashable_filters(get_current_filters()))
st.download_button(
    label="⬇️ Download Filtered Results (CSV)",
    data=csv_data,
    file_name="aiaaic_export.csv",
    mime="text/csv",
)


if 'offset' not in st.session_state:
    st.session_state.offset = 0
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

if search_term != st.session_state.last_search:
    st.session_state.offset = 0
    st.session_state.last_search = search_term

col1, col2, col3, _ = st.columns([1, 1, 1, 6])
with col1:
    if st.button("⬅️ Previous") and st.session_state.offset >= 50:
        st.session_state.offset -= 50
with col2:
    st.write(f"Showing {st.session_state.offset} to {st.session_state.offset + 50}")
with col3:
    if st.button("Next ➡️"):
        st.session_state.offset += 50

# Fetch data dynamically (no caching here to allow instant search & pagination)
df = get_incidents_list(limit=50, offset=st.session_state.offset, search_term=search_term if search_term else None, filters=get_current_filters())

if df is not None and not df.empty:
    # Formatting for display
    display_df = df.copy()
    display_df['incident_date'] = pd.to_datetime(display_df['incident_date']).dt.strftime('%b %d, %Y')
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "incident_id": st.column_config.NumberColumn("ID", format="%d"),
            "aiaaic_record_id": st.column_config.TextColumn("AIAAIC Ref"),
            "title": st.column_config.TextColumn("Headline (Title)"),
            "incident_date": "Date",
            "source_url": st.column_config.LinkColumn("Source Link")
        }
    )
else:
    st.warning("No incidents match these filters.")
