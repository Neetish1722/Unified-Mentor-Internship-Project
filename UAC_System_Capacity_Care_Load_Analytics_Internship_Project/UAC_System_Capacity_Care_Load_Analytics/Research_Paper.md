# Research Paper: System Capacity & Care Load Analytics for Unaccompanied Children

## Abstract
This project develops a transparent analytical framework for monitoring the UAC care pipeline from CBP custody through HHS care and discharge. The supplied dataset contains 720 populated reporting dates between 2023-01-12 and 2025-12-21. Raw counts are transformed into total system load, net intake pressure, growth, backlog, volatility, discharge offset and stress indicators.

## 1. Background and Problem
The UAC care pipeline can be understood as a dynamic flow: CBP intake → CBP custody → transfer to HHS → HHS care → discharge. A centralized analytical layer is needed to understand system-wide load, inflow/outflow balance, sustained pressure and relief periods.

## 2. Objectives
- Quantify daily and cumulative care load across CBP and HHS.
- Identify periods of capacity strain and relief.
- Analyze transfers into HHS versus HHS discharges.
- Support staffing and shelter planning.
- Improve situational awareness for policymakers.
- Enable data-driven humanitarian response evaluation.

## 3. Dataset
The supplied dataset contains Date, CBP apprehensions, CBP custody, transfers out of CBP, HHS care and HHS discharges. It contains 1,170 source rows, 450 blank rows, and 720 populated reporting dates. The full calendar span contains 1,075 days.

## 4. Data Ingestion and Quality
Dates are parsed and ordered chronologically. Numeric fields are converted from comma-formatted text where necessary. Blank records and duplicate populated dates are handled. A complete daily calendar is created so missing reporting days remain visible rather than being silently invented.

Validation checks include missing core measures, transfer-versus-CBP constraints, and discharge-versus-HHS constraints. Flags are presented as investigation signals, not automatically treated as operational errors.

## 5. Derived Healthcare Capacity Metrics
**Total System Load** = CBP custody + HHS care.

**Net Daily Intake Pressure** = transfers into HHS − HHS discharges.

**Care Load Growth Rate** = day-over-day percentage change in total system load.

**Backlog Indicator** = sustained positive 14-day average net intake pressure.

**Care Load Volatility Index** = rolling 14-day standard deviation of net pressure divided by rolling 14-day average system load × 100.

**Discharge Offset Ratio** = HHS discharges divided by transfers into HHS × 100.

**Stress Score** = normalized recent load combined with positive rolling pressure as a screening signal.

## 6. Trend and Temporal Analysis
The application supports daily, weekly and monthly views, rolling 7/14-day averages, monthly comparisons, pressure trends and high-stress windows.

## 7. KPI Framework
| KPI | Purpose |
|---|---|
| Total Children Under Care | System-wide care responsibility |
| Net Intake Pressure | Inflow/outflow imbalance |
| Care Load Volatility Index | Stability of pressure |
| Backlog Accumulation Rate | Sustained positive pressure |
| Discharge Offset Ratio | Ability to relieve transfer pressure |
| Peak System Load | Highest combined load |
| Stress Score | Capacity-pressure screening signal |

## 8. Streamlit Application
The dashboard includes:
- System Load Overview Pane
- CBP vs HHS Load Comparison
- Net Intake & Backlog Trends
- KPI Summary Cards
- Date range selector
- Metric selector
- Daily/weekly/monthly granularity
- Pressure and stress analysis
- Data-quality transparency
- Optional 14-day trend projection
- Methodology and limitations

The interface uses a dark executive theme, animated hero section, gradient/glass-style KPI cards, responsive layout and interactive Plotly visualizations.

## 9. Recommendations
1. Establish recurring KPI reviews.
2. Combine load analytics with facility capacity and staffing information.
3. Investigate sustained positive rolling pressure early.
4. Use rolling indicators rather than isolated daily spikes.
5. Maintain a data-quality exception log.
6. Add facility-level occupancy, staffing and length-of-stay data in future versions.
7. Validate future forecasting models with back-testing before operational adoption.

## 10. Limitations
The dataset does not contain staffing, bed capacity, clinical acuity, length-of-stay, facility-level occupancy or individual-level outcomes. Therefore, this project measures **care-load pressure**, not actual facility capacity, clinical risk or individual child risk.

## 11. Conclusion
The project converts raw UAC pipeline counts into a transparent capacity-intelligence framework. It gives stakeholders a common view of load, pressure, volatility and discharge balance while clearly separating analytical signals from official operational, clinical, legal and safeguarding decisions.
