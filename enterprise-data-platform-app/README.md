# enterprise-data-platform
End-to-end enterprise data platform on GCP

Welcome! 👋
This repository contains a production‑ready, end‑to‑end Enterprise Data Platform built using modern, industry‑standard tools on Google Cloud Platform (GCP).
This project is deliberately designed so that:

⭐ Beginners can learn step by step
⭐ The same code can be promoted to production
⭐ Non‑technical users can trigger ETL via a UI


📌 What Problem Does This Solve?
Organizations usually receive data in many formats from many sources. This platform:
✅ Ingests data from Google Cloud Storage (GCS)
✅ Supports multiple file formats
✅ Applies enterprise‑grade transformations
✅ Implements all Slowly Changing Dimension (SCD) types
✅ Creates a secure data warehouse layer
✅ Exposes analytics‑ready views
✅ Orchestrates everything using Apache Airflow


Architecture Overview

GCS (Raw Files)
      │
      ▼
Staging Dataset (BigQuery)
      │
      ▼
Target Dataset (Transform + SCD)
      │
      ▼
Warehouse Dataset (Masked Views)
      │
      ▼
BI Dashboards (Looker / Looker Studio)



Project Structure

enterprise-data-platform/
│
├── airflow/          # Airflow DAGs (orchestration)
├── spark/            # Spark ingestion & transformation logic
├── sql/              # BigQuery SQL (SCDs, transforms, views)
├── ui/               # Streamlit UI (non‑technical users)
├── config/           # Metadata‑driven pipeline definitions
├── docker/           # Local runtime (Docker Compose)
├── terraform/        # Infrastructure as Code (GCP)
└── README.md         # You are here


Supported File Types
Category	        Formats	
Flat Files	        CSV, TSV, TXT	
Structured	        XLS, XLSX, SQL	
Semi‑Structured	    JSON, XML	
Big Data	        Parquet, ORC, Avro	


Supported SCD Types

✅ SCD Type 0 – No changes
✅ SCD Type 1 – Overwrite history
✅ SCD Type 2 – Full history
✅ SCD Type 3 – Limited history
✅ SCD Type 4 – Separate history table
✅ SCD Type 6 – Hybrid approach


Transformations Covered

Data Cleansing

Null handling
Duplicate removal
Data validation
Standardization
Trimming & padding
Invalid record filtering
Data Type & Format

Data type casting
Date & timezone conversions
Boolean normalization
Unit conversions
Structural

Column rename
Column reorder
Add / drop columns


Security & Governance
✅ PII / SPII masking using BigQuery views
✅ Hashing & encryption for sensitive fields
✅ Column‑level & row‑level security ready


Who Is This For?

Role	            How They Use It	
Beginner Engineer	Learn real enterprise ETL patterns	
Data Engineer	    Extend & productionize pipelines	
Analyst	            Query clean warehouse views	
Non‑Tech User	    Trigger ETL via UI	


🚀 How to Use This Repository (High‑Level)

Clone the GitHub repository
Run local environment using Docker
Configure pipelines via YAML
Trigger ETL via Airflow or UI
Test results locally
Deploy infrastructure using Terraform
(Detailed step‑by‑step instructions will be added progressively.)


🧠 How This Repo Is Organized for Learning
This repository is built incrementally:
✅ Start simple (Git, folders, README)
✅ Add ingestion logic
✅ Add transformations
✅ Add SCD logic
✅ Add orchestration
✅ Add UI
✅ Move to production safely
You will never jump steps.


📌 Next Steps (Beginner Roadmap)
We will build this project in the same order real companies do:
1️⃣ ✅ Git & GitHub basics (DONE) 2️⃣ Docker & local runtime 3️⃣ Spark ingestion engine 4️⃣ BigQuery transformations 5️⃣ SCD framework 6️⃣ Airflow orchestration 7️⃣ Security & warehouse layer 8️⃣ BI dashboards 9️⃣ Production deployment


🤝 Contribution
This repo is designed for learning and enterprise readiness. Feel free to fork and experiment.


✅ Status
🚧 Under active development – step by step 🚧
