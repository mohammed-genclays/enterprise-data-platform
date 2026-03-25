import streamlit as st
import yaml

st.title("Enterprise ETL Platform")

pipeline_name = st.text_input("Pipeline Name")
file_path = st.text_input("Source File Path")
scd_type = st.selectbox("SCD Type", [1,2])

if st.button("Register Pipeline"):
    new_pipeline = {
        "pipeline_name": pipeline_name,
        "source": {"file_type": "csv", "path": file_path},
        "staging_table": f"staging.{pipeline_name}",
        "target_table": f"target.{pipeline_name}_dim",
        "scd_type": scd_type
    }

    with open("/app/config/pipelines.yaml", "a") as f:
        yaml.dump({"pipelines":[new_pipeline]}, f)

    st.success("✅ Pipeline registered successfully")