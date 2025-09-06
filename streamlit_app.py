import streamlit as st
import duckdb
import pandas as pd
import os

# ==================== Koneksi Database ====================
DB_PATH = os.path.join(os.path.dirname(__file__), "revenue.duckdb")
conn = duckdb.connect(DB_PATH)

# Query data
df = conn.execute("SELECT * FROM revenue").df()
df['date'] = pd.to_datetime(df['date'])

# ==================== Sidebar Filter ====================
st.sidebar.title("Filter Data")
start_date = st.sidebar.date_input("Start Date", value=df['date'].min())
end_date = st.sidebar.date_input("End Date", value=df['date'].max())
schools = df['school'].unique()
selected_schools = st.sidebar.multiselect("Pilih Sekolah", options=schools, default=schools.tolist())

# ==================== Filter Data ====================
if start_date > end_date:
    st.error("End date harus >= start date")
else:
    df_filtered = df[
        (df['date'] >= pd.to_datetime(start_date)) &
        (df['date'] <= pd.to_datetime(end_date)) &
        (df['school'].isin(selected_schools))
    ]

    # ==================== KPI Cards per Sekolah ====================
    st.subheader("Total Revenue per Sekolah")
    card_template = """
    <div style="
        background-color: #4CAF50;
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        ">
        <p>{revenue}</p>
        <p>{school}</p>
    </div>
    """
    kpi_cols = st.columns(len(selected_schools))
    for i, school in enumerate(selected_schools):
        total_rev = df_filtered[df_filtered['school'] == school]['revenue'].sum()
        total_rev_str = f"{int(total_rev):,}".replace(",", ".")
        kpi_cols[i].markdown(card_template.format(school=school, revenue=total_rev_str), unsafe_allow_html=True)

    # ==================== Tabel Gabungan per Tanggal ====================
    st.subheader("Resume Revenue Gabungan per Tanggal")
    pivot_df = df_filtered.pivot_table(
        index='date',
        columns='school',
        values='revenue',
        aggfunc='sum'
    ).fillna(0).sort_index()

    # Format tanggal dd/mm/yyyy
    pivot_df.index = pivot_df.index.strftime("%d/%m/%Y")

    # Cumulative revenue per sekolah
    cum_df = pivot_df.cumsum()
    pivot_df_cum = cum_df.copy()  # cumulative revenue

    # Format semua angka menjadi Rupiah dengan titik sebagai pemisah ribuan
    pivot_df_cum = pivot_df_cum.applymap(lambda x: f"{int(x):,}".replace(",", "."))

    st.dataframe(pivot_df_cum)


    # ==================== Grafik Perbandingan Revenue ====================
    st.subheader("Grafik Perbandingan Revenue Sekolah")
    comparison_df = df_filtered.groupby('school')['revenue'].sum().reset_index()
    st.bar_chart(comparison_df.set_index('school'))
