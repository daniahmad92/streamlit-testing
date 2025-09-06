import streamlit as st
import duckdb
import pandas as pd
import os

# Path relatif supaya bisa dibaca di Streamlit Cloud
DB_PATH = os.path.join(os.path.dirname(__file__), "revenue.duckdb")
conn = duckdb.connect(DB_PATH)

# Query data
df = conn.execute("SELECT * FROM revenue").df()
df['date'] = pd.to_datetime(df['date'])

# Sidebar filter
st.sidebar.title("Filter Data")
start_date = st.sidebar.date_input("Start Date", value=df['date'].min())
end_date = st.sidebar.date_input("End Date", value=df['date'].max())

schools = df['school'].unique()
selected_schools = st.sidebar.multiselect("Pilih Sekolah", options=schools, default=schools.tolist())

if start_date > end_date:
    st.error("End date harus >= start date")
else:
    df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) &
                     (df['date'] <= pd.to_datetime(end_date)) &
                     (df['school'].isin(selected_schools))]

    # ==================== KPI Cards per Sekolah ====================
    st.subheader("Total Revenue per Sekolah")
    kpi_cols = st.columns(len(selected_schools))
    for i, school in enumerate(selected_schools):
        total_rev = df_filtered[df_filtered['school'] == school]['revenue'].sum()
        kpi_cols[i].metric(label=school, value=f"Rp {total_rev:,.0f}")

    # ==================== Tabel Resume per Sekolah ====================
    st.subheader("Resume Revenue per Sekolah")
    for school in selected_schools:
        st.markdown(f"### {school}")
        school_df = df_filtered[df_filtered['school'] == school]
        resume_df = school_df.groupby('date')['revenue'].sum().reset_index()
        resume_df['Cumulative Revenue'] = resume_df['revenue'].cumsum()
        st.dataframe(resume_df)

    # ==================== Grafik Perbandingan Revenue ====================
    st.subheader("Grafik Perbandingan Revenue Sekolah")
    comparison_df = df_filtered.groupby('school')['revenue'].sum().reset_index()
    st.bar_chart(comparison_df.set_index('school'))
