# FMIS - Expense & Revenue Dashboard 📊

A premium, interactive web application built with **Streamlit** and **Plotly** to provide integrated monitoring of Government Expense and Revenue for the year 2025.

## Overview

The FMIS Expense & Revenue Dashboard serves as a high-end visualization tool for tracking government financial performance. It integrates both expenditure and revenue data to provide a holistic view of implementation progress against the Financial Law and Modified Law across National and Sub-national levels.

## Key Features

- **Integrated Summary KPIs:** Real-time visibility into Financial Law and Modified Law targets for both Expense and Revenue.
- **Execution Ratios:** Dynamic gauge charts showing the percentage of implementation relative to the Modified Law.
- **Implementation Progress:** Visual process bars tracking National and Sub-national levels side-by-side.
- **Top 5 Analytics:**
    - Implementation by **Economic Class** (Expense & Revenue).
    - implementation by **Organizations** (Expense & Revenue) using high-end donut charts.
- **Trend Analysis:**
    - **Monthly Trends:** Interactive multi-line charts comparing Revenue and Expense implementation over time.
    - **Quarterly Implementation:** Pyramid-style analysis for quarterly performance comparison.
- **Net Summary:** High-level bar chart comparing total Revenue vs Expense and the resulting Net position.
- **Premium UI/UX:**
    - Custom dark-themed interface with vibrant color palettes.
    - Responsive layout optimized for dashboard displays.
    - Interactive tooltips showing exact KHR values while maintaining clean "Million" scale visualizations on axes.

## Tech Stack

- **Python** (Core Logic & Data Processing)
- **Pandas** (Excel Data Handling)
- **Streamlit** (Web Framework & Layout)
- **Plotly** (Interactive Visualizations)
- **Custom CSS** (Advanced Styling & Animations)

## Installation & Setup

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

### 1. Clone the repository

```bash
git clone https://github.com/Sovatharothh/fmis_expenditure_dashboard.git
cd R20-dashboard
```

### 2. Set up a Virtual Environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```
## Running the Application

To start the dashboard locally, run the following command in your terminal:

```bash
streamlit run app.py
```

If you are using the virtual environment specifically on Windows, you can also run:
```powershell
.\venv\Scripts\streamlit run app.py
```

The application will typically be served at `http://localhost:8501`.

### 3. Install Dependencies

```bash
pip install streamlit plotly pandas openpyxl
```

## Running the Application

To start the dashboard locally, run:

```bash
streamlit run app.py
```

The application will typically be served at `http://localhost:8501`.

## Data Source

The dashboard automatically loads and processes data from Excel files located in the `data_set/` directory:
- `expense.xlsx`: Contains expenditure data across levels and classes.
- `revenue.xlsx`: Contains revenue collection data and targets.

## Project Structure

- `app.py`: Main application script with UI logic and visualizations.
- `data_set/`: Directory for input Excel data files.
- `venv/`: Local Python environment.
- `.streamlit/`: Streamlit configuration and themes.
