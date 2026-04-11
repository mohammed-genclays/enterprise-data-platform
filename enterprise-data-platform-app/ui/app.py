import streamlit as st
import yaml
import os

st.title("Enterprise ETL Platform")

pipeline_name = st.text_input("Pipeline Name")
file_path = st.text_input("Source File Path")
scd_type = st.selectbox("SCD Type", [1, 2])

CONFIG_PATH = "/app/config/pipelines.yaml"

if st.button("Register Pipeline"):

    new_pipeline = {
        "pipeline_name": pipeline_name,
        "source": {
            "file_type": "csv",
            "path": file_path
        },
        "staging_table": f"staging.{pipeline_name}",
        "target_table": f"target.{pipeline_name}_dim",
        "scd_type": scd_type
    }

    # Load existing config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f) or {"pipelines": []}
    else:
        config = {"pipelines": []}

    # Prevent duplicates
    existing = [p["pipeline_name"] for p in config["pipelines"]]
    if pipeline_name in existing:
        st.error("Pipeline already exists")
    else:
        config["pipelines"].append(new_pipeline)
        with open(CONFIG_PATH, "w") as f:
            yaml.safe_dump(config, f)
        st.success("✅ Pipeline registered successfully")