# Technical Documentation

## Architecture
```text
UAC CSV
  ↓
Data Cleaning / Parsing
  ↓
Complete Daily Calendar
  ↓
Data Quality Validation
  ↓
Feature Engineering
  ├─ Total System Load
  ├─ Net Intake Pressure
  ├─ Growth Rate
  ├─ Rolling 7/14-day measures
  ├─ Volatility
  ├─ Backlog Indicator
  ├─ Discharge Offset Ratio
  └─ Stress Score
  ↓
Daily / Weekly / Monthly Aggregation
  ↓
Streamlit + Plotly Dashboard
```

## Visual Enhancements
- Animated hero section
- Gradient dark executive theme
- Glass-style KPI cards
- Hover effects
- Responsive six-card KPI layout
- Interactive Plotly charts
- Sidebar filters
- Five analytical tabs
- Data-quality transparency
- Optional 14-day trend projection
- Methodology and limitation panel

## Reproducibility
All analytical values are calculated programmatically from the supplied dataset. No chart values are manually hard-coded.
