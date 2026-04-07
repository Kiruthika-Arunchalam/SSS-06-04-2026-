import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="SSS Dashboard", layout="wide")

# ---------------------------
# THEME
# ---------------------------
theme = st.toggle("Dark Mode")

bg_color = "#0e1117" if theme else "white"
text_color = "white" if theme else "black"

# ---------------------------
# CSS
# ---------------------------
st.markdown(f"""
<style>
body {{
    background-color: {bg_color};
    color: {text_color};
}}
.title {{
    background: linear-gradient(90deg, #ff9a9e, #a18cd1, #84fab0);
    padding: 18px;
    text-align: center;
    font-size: 30px;
    font-weight: bold;
    color: white;
    border-radius: 12px;
    margin-bottom: 20px;
}}
.section {{
    background: linear-gradient(90deg, #36d1dc, #5b86e5);
    padding: 10px;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    margin-top: 25px;
}}
.card {{
    padding: 25px;
    border-radius: 14px;
    color: white;
    text-align: center;
    font-weight: bold;
}}
.card1 {{ background: linear-gradient(135deg, #ff9a9e, #fad0c4); }}
.card2 {{ background: linear-gradient(135deg, #a18cd1, #fbc2eb); }}
.card3 {{ background: linear-gradient(135deg, #f6d365, #fda085); }}
.card4 {{ background: linear-gradient(135deg, #84fab0, #8fd3f4); }}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# CHART STYLE
# ---------------------------
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font_color=text_color,
        xaxis=dict(tickfont=dict(color=text_color)),
        yaxis=dict(tickfont=dict(color=text_color))
    )
    return fig

# ---------------------------
# TITLE
# ---------------------------
st.markdown('<div class="title">SSS DATA ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)

# ---------------------------
# LOAD DATA (NO CACHE ISSUE)
# ---------------------------
def load_data():
    df = pd.read_csv("SSS(06-04-2026).csv", encoding="cp1252")
    return df

df = load_data()

# ---------------------------
# CLEAN DATA
# ---------------------------
df["Operator_Code"] = df["Operator_Code"].astype(str).str.strip()
df["Service"] = df["Service"].astype(str).str.strip()
df["From_Port"] = df["From_Port"].astype(str).str.strip().str.upper()
df["To_Port"] = df["To_Port"].astype(str).str.strip().str.upper()

df["Inserted_At"] = pd.to_datetime(df["Inserted_At"], errors="coerce", dayfirst=True)
df["Inserted_Date"] = df["Inserted_At"].dt.normalize()

# ---------------------------
# FILTERS
# ---------------------------
st.markdown("### Filters")

col1, col2, col3, col4 = st.columns(4)

operator = col1.multiselect("Operator", sorted(df["Operator_Code"].unique()))
service = col2.multiselect("Service", sorted(df["Service"].unique()))
from_port = col3.multiselect("From Port", sorted(df["From_Port"].unique()))
to_port = col4.multiselect("To Port", sorted(df["To_Port"].unique()))

filtered_df = df.copy()

if operator:
    filtered_df = filtered_df[filtered_df["Operator_Code"].isin(operator)]
if service:
    filtered_df = filtered_df[filtered_df["Service"].isin(service)]
if from_port:
    filtered_df = filtered_df[filtered_df["From_Port"].isin(from_port)]
if to_port:
    filtered_df = filtered_df[filtered_df["To_Port"].isin(to_port)]

# ---------------------------
# KPI METRICS
# ---------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Records", len(filtered_df))
k2.metric("Operators", filtered_df["Operator_Code"].nunique())
k3.metric("Routes", filtered_df["From_Port"].nunique())
k4.metric("Services", filtered_df["Service"].nunique())

# ---------------------------
# CARDS
# ---------------------------
c1, c2, c3, c4 = st.columns(4)

c1.markdown(f'<div class="card card1">OPERATORS<br><h1>{filtered_df["Operator_Code"].nunique()}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="card card2">PORTS<br><h1>{filtered_df["From_Port"].nunique()}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="card card3">TERMINALS<br><h1>{filtered_df["From_Port_Terminal"].nunique()}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="card card4">VESSELS<br><h1>{filtered_df["Vessel_Name"].nunique()}</h1></div>', unsafe_allow_html=True)

# ---------------------------
# DOWNLOAD
# ---------------------------
#st.download_button("📥 Download Data", filtered_df.to_csv(index=False), "data.csv")

# ---------------------------
# MARKET SHARE
# ---------------------------
# st.markdown('<div class="section">Market Share</div>', unsafe_allow_html=True)

# market_df = filtered_df["Operator_Code"].value_counts().reset_index()
# market_df.columns = ["Operator", "Count"]

# fig_pie = px.pie(market_df, names="Operator", values="Count", hole=0.4)
# st.plotly_chart(style_chart(fig_pie), use_container_width=True)

# ---------------------------
# SUMMARY TABLE
# ---------------------------
st.markdown('<div class="section">Date vs Operator Summary</div>', unsafe_allow_html=True)

summary_df = (
    filtered_df.groupby(["Inserted_Date", "Operator_Code"])
    .size()
    .reset_index(name="Count")
)

summary_df["Inserted_Date"] = summary_df["Inserted_Date"].dt.strftime("%d-%m-%Y")

total = pd.DataFrame({
    "Inserted_Date": ["TOTAL"],
    "Operator_Code": [""],
    "Count": [summary_df["Count"].sum()]
})

final_df = pd.concat([summary_df, total])

st.dataframe(final_df, use_container_width=True)

# ---------------------------
# OPERATOR TREND
# ---------------------------
st.markdown('<div class="section">Operator Count</div>', unsafe_allow_html=True)

trend = filtered_df["Operator_Code"].value_counts().reset_index()
trend.columns = ["Operator", "Count"]

fig = px.bar(
    trend,
    x="Operator",
    y="Count",
    color="Operator",
    text="Count",
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig.update_traces(textposition="outside", textfont=dict(color=text_color))
fig.update_layout(showlegend=False)

st.plotly_chart(style_chart(fig), use_container_width=True)

# ---------------------------
# TOP ROUTES
# ---------------------------
st.markdown('<div class="section">Top Routes</div>', unsafe_allow_html=True)

route_df = (
    filtered_df.groupby(["From_Port", "To_Port"])
    .size()
    .reset_index(name="Count")
)

route_df["Route"] = route_df["From_Port"] + " → " + route_df["To_Port"]
route_df = route_df.sort_values(by="Count", ascending=False).head(10)

fig_route = px.bar(
    route_df,
    x="Count",
    y="Route",
    orientation="h",
    color="Route",
    text="Count",
    color_discrete_sequence=px.colors.qualitative.Set3
)

st.plotly_chart(style_chart(fig_route), use_container_width=True)

# ---------------------------
# SERVICE DISTRIBUTION
# ---------------------------
st.markdown('<div class="section">Service Distribution</div>', unsafe_allow_html=True)

service_df = filtered_df["Service"].value_counts().reset_index()
service_df.columns = ["Service", "Count"]

fig_service = px.bar(
    service_df.head(10),
    x="Count",
    y="Service",
    orientation="h",
    color="Service",
    text="Count",
    color_discrete_sequence=px.colors.qualitative.Dark24
)

st.plotly_chart(style_chart(fig_service), use_container_width=True)

# ---------------------------
# ANOMALY DETECTION
# ---------------------------
# st.markdown('<div class="section">Anomaly Detection</div>', unsafe_allow_html=True)

# anomaly = filtered_df["Operator_Code"].value_counts().reset_index()
# anomaly.columns = ["Operator", "Count"]

# avg = anomaly["Count"].mean()
# anomaly["Anomaly"] = anomaly["Count"] < (avg * 0.5)

# st.dataframe(anomaly[anomaly["Anomaly"] == True])

# ---------------------------
# COMPARISON
# ---------------------------
st.markdown('<div class="section">Operator Comparison</div>', unsafe_allow_html=True)

op_list = filtered_df["Operator_Code"].unique()

op1 = st.selectbox("Operator 1", op_list)
op2 = st.selectbox("Operator 2", op_list)

st.write(f"{op1}: {len(filtered_df[filtered_df['Operator_Code']==op1])} records")
st.write(f"{op2}: {len(filtered_df[filtered_df['Operator_Code']==op2])} records")
