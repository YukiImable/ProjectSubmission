import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Menyiapkan dataframe
# create_daily_summary_df untuk mengelompokkan data berdasarkan hari
def create_daily_summary_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    daily_summary_df = df[['dteday', 'cnt_day']].drop_duplicates().reset_index(drop=True)
    daily_summary_df.rename(columns={"cnt_day": "total_rentals"}, inplace=True)
    return daily_summary_df

# create_hourly_rental_df untuk mengelompokkan data berdasarkan jam dan tipe hari
def create_hourly_rental_df(df):
    hourly_rental_df = df.groupby(["hr", "workingday_hour"]).agg({"cnt_hour": "mean"}).reset_index()
    hourly_rental_df.replace({"workingday_hour": {1: "Hari Kerja", 0: "Akhir Pekan"}}, inplace=True)
    return hourly_rental_df

# Load file main_data.csv
all_df = pd.read_csv("main_data.csv")

# Memastikan data dteday bertipe datetime
datetime_columns = ["dteday"]
all_df.sort_values(by="dteday", inplace=True)
all_df.reset_index(drop=True, inplace=True)
 
for column in datetime_columns:
  all_df[column] = pd.to_datetime(all_df[column])
  

# Membuat Filter
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    # Menambahkan logo
    st.image("https://raw.githubusercontent.com/YukiImable/assets/main/pngegg.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Pilih Range Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    

# Menyimpan data yang di filter dalam main_df
main_df = all_df[(all_df["dteday"] >= str(start_date)) & 
                (all_df["dteday"] <= str(end_date))]

# Memanggil helper function
daily_summary_df = create_daily_summary_df(main_df)
hourly_rental_df = create_hourly_rental_df(main_df)

# Dashboard Header
st.header('Dashboard Penyewaan Sepedah 🚲')

# Subheader 1: Visualisasi Sewa Harian
st.subheader('Sewa Harian')

# Inisialisasi kolom
col1, col2 = st.columns(2)

# Menampilkan metrik total dan rata-rata rental sepeda
with col1:
    total_rentals = daily_summary_df.total_rentals.sum()
    st.metric("Total Rentals", value=total_rentals)

with col2:
    avg_rentals = daily_summary_df.total_rentals.mean()
    st.metric("Average Daily Rentals", value=int(avg_rentals))
    
# Membuat grafik jumlah penyewaan harian
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_summary_df["dteday"],
    daily_summary_df["total_rentals"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)

# Menampilkan grafik jumlah penyewaan harian
ax.set_ylabel("[Total Rentals]", fontsize=15)
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=10)
st.pyplot(fig)

# Subheader 2: Visualisasi Dampak Cuaca Terhadap Penyewaan Sepeda
st.subheader('Pengaruh Kondisi Cuaca')

# Menghitung total penyewaan berdasarkan kondisi cuaca
rental_by_weather = main_df.groupby("weathersit_hour")["cnt_hour"].sum().sort_values(ascending=False)

# Filer kategori cuaca
rental_by_weather = rental_by_weather[rental_by_weather.index.isin([1, 2, 3])].sort_values(ascending=False)

# Memberi label untuk kondisi cuaca
weather_labels = {1: "Sunny", 2: "Cloudy", 3: "Rain"}
weather_categories = [weather_labels[i] for i in rental_by_weather.index]

# Membuat grafik jumlah penyewaan berdasarkan cuaca
fig, ax = plt.subplots(figsize=(8, 5))
rental_by_weather.plot(kind="bar", color=["skyblue", "lightgray", "lightgray"], ax=ax)

# Menampilkan grafik jumlah penyewaan berdasarkan cuaca
ax.set_title(f"Bike Rental Intensity Based on The Weather\n({start_date} s.d. {end_date})")
ax.set_xlabel("[Weather Conditions]")
ax.set_xticklabels(weather_categories, rotation=0)
ax.set_ylabel("[Total Rentals]")
ax.ticklabel_format(style='plain', axis='y')
st.pyplot(fig, clear_figure=True)

# Subheader 3: Visualisasi Puncak Penyewaan
st.subheader('Pola Penyewaan Sepeda Berdasarkan Jam')

# Filter data berdasarkan rentang waktu
main_df = all_df[(all_df["dteday"] >= str(start_date)) & (all_df["dteday"] <= str(end_date))]
hourly_rental_df = create_hourly_rental_df(main_df)

# Membuat visualisasi
fig, ax = plt.subplots(figsize=(10, 5))
for day_type in ["Hari Kerja", "Akhir Pekan"]:
    subset = hourly_rental_df[hourly_rental_df["workingday_hour"] == day_type]
    ax.plot(subset["hr"], subset["cnt_hour"], marker='o', linestyle='-', label=day_type, linewidth=2)
    
    # Menandai titik tertinggi
    max_point = subset.nlargest(1, "cnt_hour")
    ax.scatter(max_point["hr"], max_point["cnt_hour"], color='red', s=100, edgecolors='black', zorder=3)

# Menambahkan label dan judul
ax.set_xlabel("[Hour]")
ax.set_ylabel("[Average Bike Rental]")
ax.set_title(f"Bike Rental Patterns By Hour\n({start_date} s.d. {end_date})")
ax.legend()
ax.grid(True)

# Menampilkan plot di Streamlit
st.pyplot(fig)

# Caption
st.caption('Copyright © Dimas Adista Perdana 2025, ありがとうございます。')