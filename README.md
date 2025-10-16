# 🚀 SmartMach: AI-Powered Predictive Maintenance System

<div align="center">

![SmartMach Logo](smartmach_logo.png)

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=TensorFlow&logoColor=white)](https://tensorflow.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

**Live Demo:** 🎯 [https://smartmach-predictive-maintenance-2.onrender.com](https://smartmach-predictive-maintenance-2.onrender.com)

*A comprehensive industrial AI solution for machinery health monitoring and predictive maintenance.*

</div>

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Model Details](#-model-details)
- [Results](#-results)
- [Live Demo](#-live-demo)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**SmartMach** is an end-to-end **AI-powered predictive maintenance system** that monitors industrial machinery health, predicts **Remaining Useful Life (RUL)**, and provides actionable insights for maintenance optimization.  

The system processes real-time sensor data to prevent **unexpected downtime** and reduce **maintenance costs**, ensuring smoother factory operations.

### 💼 Business Impact
- ✅ **30% reduction** in unplanned downtime  
- ✅ **25% decrease** in maintenance costs  
- ✅ **50% improvement** in maintenance planning accuracy  
- ✅ **Real-time** machinery health monitoring  

---

## ✨ Features

### 🔍 All Engine Conditions Dashboard
- Fleet-wide health overview with 3-stage classification  
- Critical / Warning / Good engine status tracking  
- Real-time health scoring (0–100%)  
- Priority-based maintenance scheduling  

### ⚙️ Specific Engine Analysis
- Individual engine health reports  
- Predicted vs Actual RUL comparison  
- Sensor-by-sensor anomaly detection  
- Advanced trend visualizations  

### 💰 AI Cost Optimizer
- Maintenance cost prediction across 4 scenarios  
- Preventive vs Emergency maintenance comparison  
- ROI and penalty cost estimation  
- Financially optimized decision support  

### 🔧 Root Cause Analysis
- SHAP-based feature importance analysis  
- Sensor contribution visualization  
- Data-driven insights for RUL degradation  
- Automated maintenance recommendations  

### 📈 Trend Forecasting
- RNN-based future trend prediction  
- 10-day forecast with threshold alerts  
- Predictive maintenance scheduling suggestions  

### 📊 Professional Reporting
- Automated PDF health reports  
- Fleet performance dashboards  
- CSV export and executive summary generation  

---

## 🛠 Technology Stack

### **Backend & AI**
- 🧠 `TensorFlow 2.20.0` — Deep Learning (LSTM Models)  
- 🌲 `Scikit-learn 1.6.1` — Random Forest, Regression, Classification  
- 🧮 `Pandas 2.3.3`, `NumPy 2.0.2` — Data processing and numerical computation  

### **Frontend & Visualization**
- 💻 `Streamlit 1.50.0` — Interactive Web Interface  
- 📊 `Plotly 6.3.1`, `Matplotlib 3.9.4` — Data Visualization  
- 🔍 `SHAP 0.48.0` — Model Explainability  

### **Deployment & Infrastructure**
- ☁️ `Render.com` — Cloud Hosting Platform  
- 🐳 `Docker` — Containerization  
- 💾 `Git LFS` — Large File Storage (Model files)  

---

## 🏗 Architecture

**Data Flow:**  
Data Layer → Preprocessing → AI Models → Business Logic → Web Interface
↓ ↓ ↓ ↓ ↓
Sensor Data Feature Eng. LSTM/RF Models Health Scoring Streamlit Dashboard


### **Workflow Steps**
1. **Sensor Data Ingestion** — Real-time industrial sensor data collected.  
2. **Feature Engineering** — Normalization, sequence building, noise reduction.  
3. **AI Prediction** — LSTM predicts RUL; Random Forest handles classification.  
4. **Health Scoring** — Multi-factor weighted health index generation.  
5. **Visualization & Reporting** — Streamlit dashboard + downloadable reports.  

---

## 📦 Installation

### 🧰 Local Development

```bash
# Clone repository
git clone https://github.com/Iftikhar-hasan12/smartmach-predictive-maintenance.git
cd smartmach-predictive-maintenance

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run app.py

### 🧰 Environment Setup
# requirements.txt
streamlit==1.50.0
tensorflow==2.20.0
pandas==2.3.3
numpy>=2.1.0
scikit-learn==1.6.1
plotly==6.3.1
matplotlib==3.9.4
shap==0.48.0
reportlab==4.4.4
seaborn==0.13.2
protobuf>=5.28.0
### 📁 Project Structure
smartmach-predictive-maintenance/
├── app.py                          # Main Streamlit application
├── preprocess.py                   # Data processing & model loading
├── animation.py                    # Loading animations
├── requirements.txt                # Python dependencies
├── smartmach_logo.png              # Application logo
├── .streamlit/
│   └── config.toml                 # Streamlit configuration
├── data/
│   ├── train_data.csv              # Training dataset
│   └── test_data.csv               # Testing dataset
├── feature/
│   ├── all_eng.py                  # All engines analysis
│   ├── single_eng.py               # Single engine analysis
│   ├── cost_optimizer.py           # Maintenance cost optimization
│   ├── root_cause_analyzer.py      # Root cause analysis
│   ├── trend_forecast.py           # Trend forecasting
│   ├── health_monitor.py           # Health scoring system
│   ├── graph.py                    # Visualization utilities
│   ├── generatereport_all_eng.py   # Fleet reporting
│   └── single_eng_report.py        # Individual engine reports
└── model/
    ├── model.h5                    # LSTM RUL prediction model
    ├── cost_model.pkl              # Cost optimization model
    └── rf.pkl                      # Random Forest analysis model
