# UAC System Capacity & Care Load Analytics

## Internship requirement coverage
This project implements the supplied specification end-to-end:
- Daily/cumulative CBP + HHS care load
- Intake/transfer/discharge balance
- Capacity strain and relief signals
- Data quality and logical validation
- Complete daily index
- Total System Load
- Net Daily Intake Pressure
- Care Load Growth Rate
- Backlog Indicator
- Rolling 7/14-day averages
- Volatility analysis
- Prolonged strain windows
- Required KPI framework
- Streamlit overview dashboard
- CBP vs HHS comparison
- Net intake/backlog trends
- KPI cards
- Date range, metric and time-granularity filters
- Research paper
- Executive summary
- Technical documentation
- Enhanced animated visual design
- Optional transparent trend projection

## Run
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Important limitation
The source does not contain facility capacity, staffing, acuity, length-of-stay or individual-level outcomes. This prototype measures care-load pressure and is not an individual-risk or clinical decision system.
