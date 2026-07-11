# 🎵 Music Streaming Analytics Platform

> An end-to-end cloud-native Analytics Engineering and Data Engineering platform built using modern industry best practices.

---

## 📖 Project Overview

The Music Streaming Analytics Platform simulates a production-grade analytics ecosystem for a modern music streaming company.

The platform ingests user listening events, stores raw data in the cloud, transforms data into trusted analytical models, validates data quality, orchestrates automated pipelines, powers executive dashboards, and enables machine learning workflows.

Rather than focusing on a single technology, this project demonstrates how modern data platforms are designed from the ground up to support analytics, business intelligence, and predictive modeling.

---

## 🎯 Objectives

- Build a scalable cloud analytics platform
- Model event-driven streaming data
- Design a modern dimensional warehouse
- Implement Analytics Engineering best practices using dbt
- Automate workflows using orchestration
- Validate data quality throughout the pipeline
- Develop executive dashboards
- Create ML-ready feature datasets
- Demonstrate production-grade engineering principles

---

# 🏗️ Architecture

```
                  Public Music Metadata
                           +
                 Generated Streaming Events
                           │
                           ▼
                    Python Ingestion
                           │
                           ▼
                      AWS S3 (Bronze)
                           │
                           ▼
                      Snowflake
                           │
                           ▼
                    dbt Transformations
                 (Staging → Intermediate → Marts)
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        Business Marts         Feature Tables
                │                     │
                ▼                     ▼
          Streamlit Dashboard    Jupyter ML
                │
                ▼
         Executive Analytics
```

---

# 🛠️ Technology Stack

| Category | Technology |
|-----------|------------|
| Programming | Python |
| Cloud Storage | AWS S3 |
| Data Warehouse | Snowflake |
| Transformations | dbt Core |
| Orchestration | Apache Airflow |
| Data Validation | Great Expectations + dbt Tests |
| Machine Learning | Scikit-Learn |
| Notebooks | Jupyter |
| Dashboard | Streamlit |
| Containers | Docker |
| CI/CD | GitHub Actions |
| Version Control | Git |

---

# 📂 Project Structure

```
music-streaming-analytics-platform/

├── configs/
├── dashboard/
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── dbt_project/
├── docs/
├── ingestion/
├── notebooks/
├── orchestration/
├── scripts/
├── tests/
├── .github/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# 🧠 Business Domain

The platform models a fictional music streaming company inspired by real-world products such as Spotify, Apple Music, Amazon Music, and YouTube Music.

The project combines:

- Public music metadata
- Synthetic user behavior
- Streaming events
- Subscription activity
- Recommendation interactions
- Product analytics
- Revenue analytics

This hybrid approach creates realistic analytical scenarios while respecting proprietary platform data.

---

# 📊 Business Questions

The platform is designed to answer questions such as:

- How many Daily Active Users (DAU) do we have?
- Which artists are trending?
- Which tracks have the highest completion rates?
- What is our Premium conversion rate?
- Which recommendations drive engagement?
- What factors contribute to churn?
- Which devices generate the highest listening time?
- What is customer lifetime value?
- How do listening habits differ by geography?

---

# 🧱 Data Architecture

The project follows a Medallion Architecture.

### Bronze

Raw immutable source data.

### Silver

Cleaned, standardized, validated datasets.

### Gold

Business-ready dimensional models and analytical marts.

### Feature Layer

Curated datasets for machine learning workflows.

---

# 📈 Analytics Engineering

The warehouse follows dimensional modeling principles.

Dimension tables include:

- Users
- Artists
- Albums
- Tracks
- Devices
- Subscriptions
- Date

Fact tables include:

- Listening Events
- Search Events
- Playlist Events
- Recommendation Events
- Payment Events

Business marts provide curated datasets for reporting and analytics.

---

# 🤖 Machine Learning

The project includes notebooks for:

- Exploratory Data Analysis
- Customer Segmentation
- Churn Prediction
- Recommendation Features
- Revenue Forecasting

Machine learning models consume curated feature tables generated from the analytics platform rather than raw source data.

---

# ✅ Data Quality

Data quality is enforced using:

- dbt Tests
- Great Expectations
- Schema validation
- Referential integrity checks
- Null validation
- Duplicate detection

---

# ⚙️ CI/CD

GitHub Actions automatically:

- Run Python checks
- Execute dbt tests
- Validate data quality
- Lint SQL
- Lint Python
- Build project documentation

---

# 📚 Documentation

Project documentation includes:

- Business Requirements
- Domain Model
- Warehouse Architecture
- Star Schema
- Data Dictionary
- Metric Definitions
- Architecture Decisions
- Deployment Guide

---

# 🚀 Future Enhancements

Potential future enhancements include:

- Kafka event streaming
- Real-time dashboards
- Feature Store
- ML model deployment
- A/B testing framework
- Recommendation engine
- Data observability platform

---

# 👨‍💻 Author

Built as a production-inspired Analytics Engineering, Data Engineering, and Applied Data Science portfolio project demonstrating modern cloud-native data platform design and implementation.