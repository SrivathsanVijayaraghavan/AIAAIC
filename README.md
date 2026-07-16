---
title: AIAAIC Incidents Dashboard
emoji: 📊
colorFrom: pink
colorTo: red
sdk: streamlit
sdk_version: 1.30.0
app_file: app/Home.py
pinned: false
---

# AIAAIC Incidents Analytics

Open source dashboard visualizing AI and algorithmic incidents from the AIAAIC dataset.

## Local Setup

1. `pip install -r requirements.txt`
2. Run data pipeline to populate SQLite: `python run_pipeline.py`
3. Launch Streamlit UI: `streamlit run app/Home.py`
