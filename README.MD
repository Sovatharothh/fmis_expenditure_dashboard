# Government Budget Expense Dashboard 📊

A comprehensive and interactive web application built with **Streamlit** and **Plotly** to visualize and analyze government budget expenses across different levels (National, Sub-National, and APE) for the years 2026.

## Overview

The Government Budget Expense Dashboard provides a clear, high-level summary and detailed breakdown of budget allocations, movements, and implementations. It allows stakeholders to monitor financial metrics, identify trends, and ensure budget availability across multiple administrative levels and classifications (Class A, Class B, Class C, and Total).

## Features

- **Overall Summary:** High-level metrics for Financial Law, Budget Movement, Modified Law, Implementation, and Available Budget.
- **Budget Classification Breakdown:** Detailed views for "Class A", "Class B", and "Class C" budgets showing individual contributions and metrics.
- **Level Analysis:** Specific breakdown of National, Sub-National, and APE Levels side by side for comparison.
- **Visual Analytics:** Multiple interactive Plotly charts, including:
  - Budget Utilization Rate by Category
  - Monthly Expense Trend (2026)
  - Top 5 Departments by Budget Allocation
  - Budget Allocated vs. Implementation by Quarter
  - Available Budget Distribution Pie Chart
- **Dynamic CSS Styling:** Custom dark-theme user interface with clean typography, progress bars, and premium color palettes designed for maximum readability and visual appeal.

## Tech Stack

- **Python** (Core Logic)
- **Streamlit** (Web Framework and UI)
- **Plotly.Graph_Objects** (Interactive Data Visualization)

## Installation & Setup

### Prerequisites

Ensure you have Python 3.8+ installed on your system.

### 1. Clone the repository

```bash
# If using git
git clone https://github.com/Sovatharothh/fmis_expenditure_dashboard.git
cd R20-dashboard
```

### 2. Set up a Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

You will need to install `streamlit` and `plotly` to run this application. If you have a `requirements.txt`, run:
```bash
pip install -r requirements.txt
```
*(Otherwise, simply install the required packages manually: `pip install streamlit plotly`)*

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

## Project Structure

- `app.py`: The main entry point of the application containing the Streamlit layout, style definitions (CSS injected via markdown), mock data structures, and Plotly visualization logic.
- `venv/`: Your local Python virtual environment.

