
from pathlib import Path
import pandas as pd, numpy as np
DATA_PATH=Path(__file__).resolve().parents[1]/"data"/"uac_care_load_cleaned.csv"
def load_data():
    return pd.read_csv(DATA_PATH,parse_dates=["Date"]).sort_values("Date").reset_index(drop=True)
def filter_data(df,start_date=None,end_date=None):
    x=df.copy()
    if start_date is not None: x=x[x.Date>=pd.Timestamp(start_date)]
    if end_date is not None: x=x[x.Date<=pd.Timestamp(end_date)]
    return x
def aggregate(df,granularity):
    if granularity=="Daily": return df.copy()
    key="Week" if granularity=="Weekly" else "Month"
    x=df.groupby(key,as_index=False).agg(
        cbp_care=("cbp_care","mean"),hhs_care=("hhs_care","mean"),
        total_system_load=("total_system_load","mean"),net_intake_pressure=("net_intake_pressure","sum"),
        hhs_discharges=("hhs_discharges","sum"),transfers_to_hhs=("transfers_to_hhs","sum"),
        stress_score=("stress_score","mean"),rolling_14_pressure=("rolling_14_pressure","mean"),
        discharge_offset_ratio=("discharge_offset_ratio","mean"))
    x["Date"]=x[key]; return x
def quality_report(df):
    return {
      "Missing core reporting days":int(df[["cbp_care","hhs_care","transfers_to_hhs","hhs_discharges"]].isna().any(axis=1).sum()),
      "Transfers > CBP custody":int((df.transfers_to_hhs>df.cbp_care).fillna(False).sum()),
      "Discharges > HHS care":int((df.hhs_discharges>df.hhs_care).fillna(False).sum())}
def trend_projection(df,horizon=14):
    x=df.dropna(subset=["Date","total_system_load"]).tail(60)
    if len(x)<10:return pd.DataFrame()
    t=np.arange(len(x)); slope,intercept=np.polyfit(t,x.total_system_load,1)
    ft=np.arange(len(x),len(x)+horizon)
    return pd.DataFrame({"Date":pd.date_range(x.Date.max()+pd.Timedelta(days=1),periods=horizon),
                         "Projected Load":intercept+slope*ft})
