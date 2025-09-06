import streamlit as st
import duckdb
import pandas as pd
import os

# ==================== Streamlit Page Config ====================
st.set_page_config(
    page_title="Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💰"
)
st.markdown(
    """
    <style>
    /* Dark Mode Styling */
    body {background-color: #0E1117; color: #FFF;}
    .stSidebar {background-color: #111; color: #FFF;}
    .stDataFrame div.row_widget.stDataFrame {background-color: #111;}

    /* Ubah teks date_input menjadi putih */
    .stDateInput input, .stDateInput label {
        color: #FFF;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================== Koneksi Database ====================
DB_PATH = os.path.join(os.path.dirname(__file__), "revenue.duckdb")
conn = duckdb.connect(DB_PATH)

# Query data
df = conn.execute("SELECT * FROM revenue").df()
df['date'] = pd.to_datetime(df['date'])

# ==================== Sidebar Filter ====================
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", value=df['date'].min())
end_date = st.sidebar.date_input("End Date", value=df['date'].max())
schools = df['school'].unique()
selected_schools = st.sidebar.multiselect(
    "Pilih Sekolah", options=schools, default=schools.tolist()
)

# ==================== Filter Data ====================
if start_date > end_date:
    st.sidebar.error("❌ End date harus >= start date")
else:
    df_filtered = df[
        (df['date'] >= pd.to_datetime(start_date)) &
        (df['date'] <= pd.to_datetime(end_date)) &
        (df['school'].isin(selected_schools))
    ]

    # ==================== KPI Cards per Sekolah ====================
    st.subheader("💹 Total Revenue per Sekolah")
    kpi_cols = st.columns(len(selected_schools))
    for i, school in enumerate(selected_schools):
        total_rev = df_filtered[df_filtered['school'] == school]['revenue'].sum()
        total_rev_str = f"Rp {int(total_rev):,}".replace(",", ".")
        kpi_cols[i].metric(label=school, value=total_rev_str)

    # ==================== Tabel Revenue per Tanggal ====================
    st.subheader("📊 Revenue per Tanggal per Sekolah")
    pivot_df = df_filtered.pivot_table(
        index='date',
        columns='school',
        values='revenue',
        aggfunc='sum'
    ).fillna(0).sort_index()

    # Format tanggal dd/mm/yyyy
    pivot_df.index = pivot_df.index.strftime("%d/%m/%Y")

    # Format semua angka menjadi Rupiah (tanpa kumulatif)
    pivot_df_formatted = pivot_df.applymap(lambda x: f"{int(x):,}".replace(",", "."))

    st.dataframe(pivot_df_formatted, use_container_width=True)
