import streamlit as st 
import pandas as pd
import requests
import altair as alt

# ==================== Streamlit Page Config ====================
st.set_page_config(
    page_title="Revenue Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💰"
)

# ==================== Ambil Data dari API ====================
API_URL = "https://script.google.com/macros/s/AKfycbzRHUpJT9nC02eiZldUJeUuQreWf__yDOj8ojC5TboFaGc107VAOLtZ9xjX4AgBl3iM/exec"
response = requests.get(API_URL)
data = response.json()

df = pd.DataFrame(data)
df['tanggal'] = pd.to_datetime(df['tanggal'])
df['saldo'] = df['saldo'].astype(int)

# ==================== Sidebar Filter ====================
st.sidebar.header("Filter Data")
start_date = st.sidebar.date_input("Start Date", value=df['tanggal'].min())
end_date = st.sidebar.date_input("End Date", value=df['tanggal'].max())

# Checkbox list untuk kategori
st.sidebar.subheader("Pilih Kategori")
categories = df['kategori'].unique()
selected_categories = []
for cat in categories:
    if st.sidebar.checkbox(cat, value=True):  # default dicentang semua
        selected_categories.append(cat)

# ==================== Filter Data ====================
if start_date > end_date:
    st.sidebar.error("❌ End date harus >= start date")
else:
    df_filtered = df[
        (df['tanggal'] >= pd.to_datetime(start_date)) &
        (df['tanggal'] <= pd.to_datetime(end_date)) &
        (df['kategori'].isin(selected_categories))
    ]

    # ==================== Grafik Line Revenue per Tanggal ====================
    st.subheader("📈 Trend Revenue per Tanggal")
    if not df_filtered.empty:
        # Group by tanggal
        saldo_per_tanggal = df_filtered.groupby('tanggal')['saldo'].sum().reset_index()
        saldo_per_tanggal['saldo_str'] = saldo_per_tanggal['saldo'].apply(lambda x: f"{int(x):,}".replace(",", "."))

        line_chart_tanggal = alt.Chart(saldo_per_tanggal).mark_line(point=True, color='#2ca02c').encode(
            x=alt.X('tanggal:T', title='Tanggal'),
            y=alt.Y('saldo:Q', title='Total Saldo'),
            tooltip=[alt.Tooltip('tanggal:T', title='Tanggal'), alt.Tooltip('saldo_str', title='Total Saldo')]
        )

        text = line_chart_tanggal.mark_text(
            dy=-10,
            color='white',
            fontSize=12
        ).encode(
            text='saldo_str'
        )

        st.altair_chart(line_chart_tanggal + text, use_container_width=True)
    else:
        st.info("Tidak ada data untuk grafik per tanggal.")


    # ==================== Grafik Total Saldo per Bulan ====================
    st.subheader("📈 Trend Revenue per Bulan")
    if not df_filtered.empty:
        df_filtered['bulan'] = df_filtered['tanggal'].dt.to_period('M')
        saldo_per_bulan = df_filtered.groupby('bulan')['saldo'].sum().reset_index()
        
        # Konversi ke string format "Bulan-Tahun"
        saldo_per_bulan['bulan_str'] = saldo_per_bulan['bulan'].dt.strftime('%B-%Y')
        
        # Pastikan diurutkan berdasarkan bulan
        saldo_per_bulan = saldo_per_bulan.sort_values('bulan')
        
        saldo_per_bulan['saldo_str'] = saldo_per_bulan['saldo'].apply(lambda x: f"{int(x):,}".replace(",", "."))
        
        line_chart = alt.Chart(saldo_per_bulan).mark_line(point=True, color='#ff7f0e').encode(
            x=alt.X('bulan_str:N', title='Bulan', sort=saldo_per_bulan['bulan_str'].tolist()),
            y=alt.Y('saldo:Q', title='Total Saldo'),
            tooltip=['bulan_str', alt.Tooltip('saldo_str', title='Total Saldo')]
        )
        
        text = line_chart.mark_text(
            dy=-10,
            color='white',
            fontSize=12
        ).encode(
            text='saldo_str'
        )
        
        st.altair_chart(line_chart + text, use_container_width=True)


    # ==================== Bar Chart Total Saldo per Kategori ====================
    st.subheader("💹 Revenue per Kategori")
    saldo_per_kategori = df_filtered.groupby('kategori')['saldo'].sum().reset_index()
    saldo_per_kategori['saldo_str'] = saldo_per_kategori['saldo'].apply(lambda x: f"{int(x):,}".replace(",", "."))

    bar_chart = alt.Chart(saldo_per_kategori).mark_bar(color='#1f77b4').encode(
        x=alt.X('kategori:N', sort='-y', title='Kategori'),
        y=alt.Y('saldo:Q', title='Total Saldo'),
        tooltip=['kategori', alt.Tooltip('saldo_str', title='Total Saldo')]
    )

    text = bar_chart.mark_text(
        dy=-5,
        color='white',
        fontSize=12
    ).encode(
        text='saldo_str'
    )

    st.altair_chart(bar_chart + text, use_container_width=True)

    # ==================== Tabel Saldo per Tanggal per Kategori ====================
    st.subheader("📊 Revenue per Tanggal per Kategori")
    if df_filtered.empty:
        st.info("Tidak ada data untuk filter yang dipilih.")
    else:
        pivot_df = df_filtered.pivot_table(
            index='tanggal',
            columns='kategori',
            values='saldo',
            aggfunc='sum'
        ).fillna(0).sort_index()

        pivot_df.index = pivot_df.index.strftime("%d/%m/%Y")
        pivot_df_formatted = pivot_df.applymap(lambda x: f"{int(x):,}".replace(",", "."))

        st.dataframe(pivot_df_formatted, use_container_width=True)
