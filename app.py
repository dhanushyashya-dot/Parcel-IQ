import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import run_analysis
from parcel_rules import run_rules

st.set_page_config(page_title="Parcel Intel", layout="wide")
st.title("📦 Parcel Intel Dashboard")
st.caption("Logistics cost optimization powered by domain expertise")

# Sidebar
st.sidebar.header("Data Source")
uploaded_file = st.sidebar.file_uploader("Upload Parcel CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv('/content/parcel_intel_sample.csv')
        st.sidebar.success("Demo data loaded")
    except:
        st.warning("Please upload a CSV file to get started.")
        st.stop()

# Run analysis
results = run_analysis(df)

# KPI Tiles
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Parcels", f"{results['total_parcels']:,}")
col2.metric("Total Spend", f"${results['total_spend']:,.2f}")
col3.metric("Avg Cost/Parcel", f"${results['avg_cost']:.2f}")
col4.metric("On-Time Rate", f"{results['ontime_rate']}%")

st.divider()

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Volume by Zone")
    fig = px.bar(results['zone_summary'], x='Zone', y='Volume', color='Volume',
                 color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Service Level Mix")
    fig = px.pie(results['service_summary'], names='Service Level', values='Volume',
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# Charts Row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Carrier On-Time Performance")
    carrier = results['carrier_summary']
    fig = px.bar(carrier, x='OnTime_Pct', y='Carrier', orientation='h',
                 color='OnTime_Pct', color_continuous_scale='RdYlGn',
                 range_color=[60, 100])
    fig.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="80% threshold")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Spend by Carrier")
    fig = px.pie(results['carrier_summary'], names='Carrier', values='Total_Spend',
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# Top States
st.subheader("Top Destination States")
fig = px.bar(results['top_states'], x='State', y='Volume', color='Volume',
             color_continuous_scale='Teal')
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Recommendations
st.subheader("🎯 AI Recommendations")
recommendations = run_rules(df)

if recommendations:
    total_savings = sum(r['estimated_savings'] for r in recommendations)
    st.success(f"**{len(recommendations)} recommendations found — Estimated savings: ${total_savings:,.2f}**")
    
    for rec in recommendations:
        with st.expander(f"💡 {rec['rule']} — {rec['parcels_affected']} parcels affected"):
            st.write(f"**Finding:** {rec['finding']}")
            st.write(f"**Recommendation:** {rec['recommendation']}")
            if rec['estimated_savings'] > 0:
                st.write(f"**Estimated Savings:** ${rec['estimated_savings']:,.2f}")
else:
    st.info("No recommendations generated.")
