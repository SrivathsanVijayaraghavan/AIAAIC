import streamlit as st
import datetime
from core.queries import get_available_filter_options

def render_global_sidebar():
    """
    Renders the persistent global filter sidebar and updates st.session_state.
    """
    if 'global_filters' not in st.session_state:
        st.session_state.global_filters = {}
        
    st.sidebar.header("🎛️ Analysis Filters")
    st.sidebar.markdown("Filters applied here affect **all charts and tables** globally.")

    # Get available list constraints
    sectors_list, harms_list = get_available_filter_options()
    
    current_year = datetime.datetime.now().year
    
    # Year Range
    st.sidebar.subheader("Date Range")
    start_y = st.sidebar.number_input("Start Year", min_value=2000, max_value=current_year, value=2010, step=1)
    end_y = st.sidebar.number_input("End Year", min_value=2000, max_value=current_year, value=current_year, step=1)
    
    # Sectors
    st.sidebar.subheader("Sectors")
    selected_sectors = st.sidebar.multiselect("Filter by Affected Sectors", options=sectors_list, default=[])
    
    # Harm Types
    st.sidebar.subheader("Harm Types")
    selected_harms = st.sidebar.multiselect("Filter by Harm Types", options=harms_list, default=[])

    st.session_state.global_filters = {
        "start_year": start_y,
        "end_year": end_y,
        "sectors": selected_sectors,
        "harm_types": selected_harms
    }

    if st.sidebar.button("Reset Filters"):
        st.session_state.global_filters = {
            "start_year": 2010,
            "end_year": current_year,
            "sectors": [],
            "harm_types": []
        }
        st.rerun()

def get_current_filters():
    return st.session_state.get('global_filters', {})

def _hashable_filters(filters):
    if not filters:
        return None
    return tuple(sorted(
        (k, tuple(v) if isinstance(v, list) else v)
        for k, v in filters.items()
    ))
