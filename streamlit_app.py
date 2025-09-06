import streamlit as st
import duckdb
import pandas as pd
import os

# Path relatif supaya bisa dibaca di Streamlit Cloud
DB_PATH = os.path.join(os.path.dirname(__file__), "revenue.duckdb")
conn = duckdb.connect(DB_PATH)

st.title("Dashboard Revenue Sekolah")

# Query data
df = conn.execute("SELECT * FROM revenue").df()

# Pastikan kolom 'date' bertipe datetime
df['date'] = pd.to_datetime(df['date'])

# Filter tanggal
st.subheader("Filter Data")
start_date = st.date_input("Start Date", value=df['date'].min())
end_date = st.date_input("End Date", value=df['date'].max())

if start_date > end_date:
    st.error("End date harus >= start date")
else:
    df_filtered_date = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

    # Filter sekolah
    schools = df_filtered_date['school'].unique()
    selected_schools = st.multiselect("Pilih Sekolah", options=schools, default=schools.tolist())

    filtered_df = df_filtered_date[df_filtered_date['school'].isin(selected_schools)]

    st.subheader("Data Revenue Filtered")
    st.dataframe(filtered_df)

    st.subheader("Grafik Revenue per Sekolah")
    revenue_chart = filtered_df.groupby('school')['revenue'].sum().reset_index()
    st.bar_chart(revenue_chart.set_index('school'))
