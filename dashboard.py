import streamlit as st
import pandas as pd
import plotly.graph_objects as go # type: ignore
from datetime import datetime, timedelta
from settings import (
    NUPL_THRESHOLDS,
    NUPL_MESSAGES,
    MVRV_LTH_THRESHOLDS,
    MVRV_LTH_MESSAGES,
    MVRV_STH_THRESHOLDS,
    MVRV_STH_MESSAGES,
    SOPR_STH_THRESHOLDS,
    SOPR_STH_MESSAGES
)

st.set_page_config(page_title="Metrics Dashboard", layout="wide")

def get_status(value, thresholds):
    for status, (min_val, max_val) in thresholds.items():
        if min_val <= value < max_val:
            return status
    return 'high' if value >= max_val else 'low'  # Handle values outside ranges

def create_metric_chart(df, metric_name, title, thresholds=None):
    # Get last 30 days of data instead of 7
    df_last_30d = df.tail(30).copy()
    
    fig = go.Figure()
    
    # Add threshold areas if thresholds exist
    if thresholds:
        for status, (min_val, max_val) in thresholds.items():
            fig.add_hrect(
                y0=min_val, 
                y1=max_val,
                fillcolor={"low": "red", "neutral": "yellow", "high": "green"}[status],
                opacity=0.1,
                line_width=0,
            )
    
    # Add the metric line
    fig.add_trace(go.Scatter(
        x=df_last_30d['date'],
        y=df_last_30d[metric_name],
        mode='lines+markers',
        name=metric_name,
        line=dict(width=2)
    ))
    
    fig.update_layout(
        title=title,
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Date",
        yaxis_title="Value",
        template="plotly_white"
    )
    
    return fig

def format_metrics_for_display(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Extract specific metrics and format them
    latest_data = df.iloc[-1]
    previous_data = df.iloc[-2]
    
    try:
        date = latest_data['date']
        nupl = latest_data['NUPL']
        mvrv_lth = latest_data['MVRV_LTH']
        mvrv_sth = latest_data['MVRV_STH']
        sopr_sth = latest_data['SOPR_STH']
        realized_cap = latest_data['RealizedCap']
    except KeyError as e:
        st.error(f"Column not found: {e}")
        return None, df
    
    # Determine current insights
    nupl_status = get_status(nupl, NUPL_THRESHOLDS)
    mvrv_lth_status = get_status(mvrv_lth, MVRV_LTH_THRESHOLDS)
    mvrv_sth_status = get_status(mvrv_sth, MVRV_STH_THRESHOLDS)
    sopr_sth_status = get_status(sopr_sth, SOPR_STH_THRESHOLDS)
    
    # Check for status changes
    alert_messages = []
    
    # Compare with previous values and add alerts for any changes
    prev_nupl_status = get_status(previous_data['NUPL'], NUPL_THRESHOLDS)
    prev_mvrv_lth_status = get_status(previous_data['MVRV_LTH'], MVRV_LTH_THRESHOLDS)
    prev_mvrv_sth_status = get_status(previous_data['MVRV_STH'], MVRV_STH_THRESHOLDS)
    prev_sopr_sth_status = get_status(previous_data['SOPR_STH'], SOPR_STH_THRESHOLDS)
    
    if nupl_status != prev_nupl_status:
        alert_messages.append(f"⚠️ NUPL status changed from {prev_nupl_status} to {nupl_status}")
    if mvrv_lth_status != prev_mvrv_lth_status:
        alert_messages.append(f"⚠️ LTH-MVRV status changed from {prev_mvrv_lth_status} to {mvrv_lth_status}")
    if mvrv_sth_status != prev_mvrv_sth_status:
        alert_messages.append(f"⚠️ STH-MVRV status changed from {prev_mvrv_sth_status} to {mvrv_sth_status}")
    if sopr_sth_status != prev_sopr_sth_status:
        alert_messages.append(f"⚠️ STH-SOPR status changed from {prev_sopr_sth_status} to {sopr_sth_status}")
    
    # Format the message with extra line breaks between metrics
    message = (
        f"📅 Date: {date}\n\n"
        f"🔹 NUPL: {nupl:.2f} ({nupl_status}) - {NUPL_MESSAGES[nupl_status]}\n\n"
        f"🔹 LTH-MVRV: {mvrv_lth:.2f} ({mvrv_lth_status}) - {MVRV_LTH_MESSAGES[mvrv_lth_status]}\n\n"
        f"🔹 STH-MVRV: {mvrv_sth:.2f} ({mvrv_sth_status}) - {MVRV_STH_MESSAGES[mvrv_sth_status]}\n\n"
        f"🔹 STH-SOPR: {sopr_sth:.2f} ({sopr_sth_status}) - {SOPR_STH_MESSAGES[sopr_sth_status]}\n\n"
        f"🔹 Realized Cap: ${realized_cap/1e9:,.2f}B\n\n"
    )
    
    if alert_messages:
        message += "ALERTS:\n" + "\n".join(alert_messages)
    
    return message, df

def main():
    st.title("📊 Crypto Metrics Dashboard")
    
    # Read and display the CSV data
    file_path = 'checkonchain.csv'
    
    try:
        # Format message and get dataframe
        message, df = format_metrics_for_display(file_path)
        
        if message:
            # Display the formatted message in a box
            st.subheader("Message Preview")
            st.info(message)
            
            # Display charts
            st.subheader("30-Day Metrics Charts")
            
            # Create charts for each metric
            col1, col2 = st.columns(2)
            
            with col1:
                # NUPL Chart
                fig_nupl = create_metric_chart(df, 'NUPL', 'NUPL', NUPL_THRESHOLDS)
                st.plotly_chart(fig_nupl, use_container_width=True)
                
                # MVRV STH Chart
                fig_mvrv_sth = create_metric_chart(df, 'MVRV_STH', 'MVRV Short Term Holders', MVRV_STH_THRESHOLDS)
                st.plotly_chart(fig_mvrv_sth, use_container_width=True)
            
            with col2:
                # MVRV LTH Chart
                fig_mvrv_lth = create_metric_chart(df, 'MVRV_LTH', 'MVRV Long Term Holders', MVRV_LTH_THRESHOLDS)
                st.plotly_chart(fig_mvrv_lth, use_container_width=True)
                
                # SOPR STH Chart
                fig_sopr_sth = create_metric_chart(df, 'SOPR_STH', 'SOPR Short Term Holders', SOPR_STH_THRESHOLDS)
                st.plotly_chart(fig_sopr_sth, use_container_width=True)
            
            # Realized Cap Chart (without thresholds)
            fig_realized_cap = create_metric_chart(df, 'RealizedCap', 'Realized Cap (in billions)', None)
            st.plotly_chart(fig_realized_cap, use_container_width=True)
            
            # Display raw data
            st.subheader("Raw Data")
            st.dataframe(df)
            
            # Add a refresh button
            if st.button("🔄 Refresh Data"):
                st.rerun()
                
    except Exception as e:
        st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 