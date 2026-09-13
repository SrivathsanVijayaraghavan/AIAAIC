#!/bin/bash
if [ ! -f "data/incidents.db" ]; then
    echo "Building database..."
    python ingestion/run_pipeline.py
fi