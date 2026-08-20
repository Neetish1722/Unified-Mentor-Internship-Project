import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parent))
from src.engine import load_data,filter_data,aggregate,quality_report,trend_projection

PLOT_BACKGROUND = "rgba(0,0,0,0)"
NET_INTAKE_PRESSURE = "Net Intake Pressure"
HHS_CARE = "HHS Care"
STRESS_SCORE = "Stress Score"

st.set_page_config(page_title="UAC Care Load Intelligence",page_icon="🧭",layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:Inter,sans-serif}
.stApp{background:radial-gradient(circle at 5% 5%,rgba(99,102,241,.16),transparent 27%),radial-gradient(circle at 95% 10%,rgba(20,184,166,.14),transparent 28%),linear-gradient(135deg,#07111f,#0b1730 48%,#111827);color:#f8fafc}
.block-container{max-width:1500px;padding-top:1.1rem}
.hero{padding:32px;border-radius:28px;background:linear-gradient(135deg,rgba(15,23,42,.97),rgba(30,41,59,.85));border:1px solid rgba(148,163,184,.18);box-shadow:0 20px 60px #0005;animation:in .8s ease-out;position:relative;overflow:hidden}
.hero:after{content:"";position:absolute;width:380px;height:380px;right:-150px;top:-180px;background:radial-gradient(circle,rgba(45,212,191,.30),transparent 68%)}
.hero h1{margin:0;font-size:2.5rem;letter-spacing:-1.5px}.hero p{color:#cbd5e1;font-size:1.03rem}
.pill{display:inline-block;margin-top:14px;padding:7px 12px;border-radius:999px;background:#6366f126;border:1px solid #818cf852;color:#c7d2fe;font-size:.82rem;font-weight:700}
@keyframes in{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.kpi{padding:19px;border-radius:20px;min-height:125px;background:linear-gradient(145deg,#1e293bed,#0f172ae8);border:1px solid #94a3b829;box-shadow:0 10px 35px #0003;transition:.25s}
.kpi:hover{transform:translateY(-5px);border-color:#2dd4bf88}.label{color:#94a3b8;font-size:.74rem;font-weight:700;text-transform:uppercase;letter-spacing:.7px}.value{font-size:1.65rem;font-weight:800;margin-top:8px}.hint{color:#64748b;font-size:.73rem;margin-top:5px}
.section{margin:24px 0 12px;padding:12px 16px;border-left:4px solid #2dd4bf;background:#0f172a73;border-radius:8px}.section h3{margin:0}
div[data-testid="stSidebar"]{background:linear-gradient(180deg,#08101f,#0b162a);border-right:1px solid #94a3b81f}
</style>
""",unsafe_allow_html=True)

df = load_data()
valid = df.dropna(subset=["Date"]).copy()
source_file = Path(__file__).resolve().parent / "HHS_Unaccompanied_Alien_Children_Program.csv"

try:
    raw_source = pd.read_csv(source_file)
    blank = int(raw_source["Date"].isna().sum())
except Exception:
    blank = 0
st.sidebar.markdown("## 🧭 UAC Intelligence")
st.sidebar.caption("System Capacity & Care Load Analytics")
mind,maxd=valid.Date.min().date(),valid.Date.max().date()
dr=st.sidebar.date_input("Reporting window",(mind,maxd),min_value=mind,max_value=maxd)
gran=st.sidebar.selectbox("Time granularity",["Daily","Weekly","Monthly"])
metric=st.sidebar.selectbox("Primary metric",["Total System Load","CBP Care",HHS_CARE,NET_INTAKE_PRESSURE,STRESS_SCORE])
projection=st.sidebar.toggle("Show 14-day trend projection",False)
if isinstance(dr,tuple) and len(dr)==2:start,end=dr
else:start,end=mind,maxd
f=filter_data(valid,start,end); view=aggregate(f,gran)

st.markdown('<div class="hero"><h1>🧭 UAC Care Load Intelligence</h1><p>System Capacity & Care Load Analytics for the Unaccompanied Children Care Pipeline</p><span class="pill">CBP → HHS → Care → Discharge • Decision-support analytics</span></div>',unsafe_allow_html=True)

latest=f.dropna(subset=["total_system_load"]).iloc[-1]; peak=f.loc[f.total_system_load.idxmax()]
cards=[
("👧 Total Children Under Care",f"{latest.total_system_load:,.0f}","Latest reported system load"),
("📈 Peak System Load",f"{peak.total_system_load:,.0f}",peak.Date.strftime("%d %b %Y")),
(f"⚖️ {NET_INTAKE_PRESSURE}",f"{f.net_intake_pressure.mean():+,.1f}","Average transfers − discharges"),
("🌊 Load Volatility",f"{f.load_volatility_index.mean():,.1f}%","14-day normalized volatility"),
("🧱 Backlog Pressure",f"{(f.rolling_14_pressure>0).mean()*100:.1f}%","Days with positive 14-day pressure"),
("🩺 Discharge Offset",f"{f.discharge_offset_ratio.replace([float('inf'),-float('inf')],pd.NA).mean():.1f}%","Mean discharges / transfers")]
for c,card in zip(st.columns(6),cards):
    c.markdown(f'<div class="kpi"><div class="label">{card[0]}</div><div class="value">{card[1]}</div><div class="hint">{card[2]}</div></div>',unsafe_allow_html=True)

st.markdown('<div class="section"><h3>📊 System Load & Flow Observatory</h3></div>',unsafe_allow_html=True)
mm={"Total System Load":("total_system_load","Total Children Under Care"),"CBP Care":("cbp_care","Children in CBP Custody"),HHS_CARE:("hhs_care","Children in HHS Care"),NET_INTAKE_PRESSURE:("net_intake_pressure",NET_INTAKE_PRESSURE),STRESS_SCORE:("stress_score","Stress Score (0–100)")}
col,title=mm[metric]
fig=px.area(view,x="Date",y=col,title=title);fig.update_layout(template="plotly_dark",height=430,margin={"l":10,"r":10,"t":55,"b":10},paper_bgcolor=PLOT_BACKGROUND,plot_bgcolor=PLOT_BACKGROUND,hovermode="x unified")
st.plotly_chart(fig,use_container_width=True)

if projection:
    pr=trend_projection(f,14)
    if not pr.empty:
        fp=go.Figure()
        fp.add_trace(go.Scatter(x=f.Date.tail(60),y=f.total_system_load.tail(60),mode="lines",name="Observed Load"))
        fp.add_trace(go.Scatter(x=pr.Date,y=pr["Projected Load"],mode="lines+markers",name="14-day trend projection", line={"dash": "dash"}))
        fp.update_layout(template="plotly_dark",height=350,title="Transparent Trend Projection — not an operational forecast",paper_bgcolor=PLOT_BACKGROUND,plot_bgcolor=PLOT_BACKGROUND)
        st.plotly_chart(fp,use_container_width=True)

t1,t2,t3,t4,t5=st.tabs(["🏥 CBP vs HHS","⚠️ Pressure & Stress","📅 Temporal Analysis","🔎 Data Quality","📘 Methodology"])
with t1:
    x=view[["Date","cbp_care","hhs_care"]].melt("Date",var_name="Stage",value_name="Children")
    x.Stage=x.Stage.map({"cbp_care":"CBP Custody","hhs_care":"HHS Care"})
    st.plotly_chart(px.line(x,x="Date",y="Children",color="Stage",title="Care Load by Pipeline Stage").update_layout(template="plotly_dark",height=400),use_container_width=True)
    x=view[["Date","transfers_to_hhs","hhs_discharges"]].melt("Date",var_name="Flow",value_name="Children")
    x.Flow=x.Flow.map({"transfers_to_hhs":"Transfers into HHS","hhs_discharges":"HHS Discharges"})
    st.plotly_chart(px.bar(x,x="Date",y="Children",color="Flow",barmode="group",title="Inflow vs Outflow").update_layout(template="plotly_dark",height=390),use_container_width=True)
with t2:
    a,b=st.columns(2)
    with a:
        st.plotly_chart(px.line(f,x="Date",y=["rolling_7_pressure","rolling_14_pressure"],title="Rolling Net Intake Pressure").update_layout(template="plotly_dark",height=380),use_container_width=True)
    with b:
        st.plotly_chart(px.area(f,x="Date",y="stress_score",title="Capacity Stress Score").update_layout(template="plotly_dark",height=380),use_container_width=True)
    high=f.sort_values("stress_score",ascending=False).head(10)[["Date","total_system_load","net_intake_pressure","stress_score","rolling_14_pressure"]]
    st.dataframe(high.rename(columns={"total_system_load":"System Load","net_intake_pressure":"Net Intake","stress_score":"Stress Score","rolling_14_pressure":"14-Day Pressure"}),use_container_width=True,hide_index=True)
with t3:
    mo=aggregate(f,"Monthly")
    st.plotly_chart(px.bar(mo,x="Date",y="total_system_load",title="Monthly Average Total System Load").update_layout(template="plotly_dark",height=380),use_container_width=True)
    we=aggregate(f,"Weekly")
    st.plotly_chart(px.line(we,x="Date",y="net_intake_pressure",title="Weekly Net Intake Pressure").update_layout(template="plotly_dark",height=380),use_container_width=True)
with t4:
    q=quality_report(df)
    st.warning(f"Transparency: the source contains {blank} blank rows and {valid.Date.nunique()} populated reporting dates. The full calendar spans {len(df)} days; missing reporting days remain explicit gaps rather than being silently imputed.")
    st.dataframe(pd.DataFrame({"Validation Check":list(q.keys()),"Count":list(q.values())}),use_container_width=True,hide_index=True)
    st.caption("Logical flags are investigation signals, not proof of operational error; timing and reporting definitions can create apparent same-day inconsistencies.")
with t5:
    st.markdown("""
### Analytical pipeline
**Data ingestion → cleaning → complete calendar → validation → feature engineering → temporal analysis → pressure detection → KPI monitoring → dashboard**

**Total System Load** = CBP custody + HHS care

**Net Daily Intake Pressure** = transfers into HHS − HHS discharges

**Care Load Growth Rate** = day-over-day percentage change

**Backlog Indicator** = sustained positive 14-day average net intake pressure

**Care Load Volatility Index** = 14-day SD of net pressure ÷ 14-day average system load × 100

**Discharge Offset Ratio** = HHS discharges ÷ transfers × 100

**Stress Score** = normalized recent load + positive pressure screening signal.

### Limitation
The source has no staffing, bed capacity, acuity, length-of-stay, facility-level occupancy or outcome fields. This dashboard therefore measures **care-load pressure**, not actual facility capacity or individual risk.
""")
st.markdown("---")
st.caption("UAC System Capacity & Care Load Analytics • Internship Decision-Support Prototype")
