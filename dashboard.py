import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

# Menyiapkan dataframe
# create_daily_summary_df untuk mengelompokkan data per hari
def create_daily_summary_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    daily_summary_df = df[['dteday', 'cnt_day']].drop_duplicates().reset_index(drop=True)
    daily_summary_df.rename(columns={"cnt_day": "total_rentals"}, inplace=True)
    return daily_summary_df

# create_hourly_summary_df untuk mengelompokkan data per jam
def create_hourly_summary_df(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    hourly_summary_df = df.groupby(['dteday', 'hr']).agg({"cnt_hour": "sum"}).reset_index()
    hourly_summary_df.rename(columns={"cnt_hour": "hourly_rentals"}, inplace=True)
    return hourly_summary_df

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
hourly_summary_df = create_hourly_summary_df(main_df)

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
ax.set_title(f"Bike Rental Intensity Based on The Weather \n ({start_date} s.d. {end_date})")
ax.set_xlabel("[Weather Conditions]")
ax.set_xticklabels(weather_categories, rotation=0)
ax.set_ylabel("[Total Rentals]")
ax.ticklabel_format(style='plain', axis='y')
st.pyplot(fig, clear_figure=True)

# Subheader 3: Visualisasi Puncak Penyewaan
st.subheader('Puncak Penyewaan')

# Mengelompokkan data berdasarkan tanggal dan jam kerja, lalu mencari jam dengan jumlah penyewaan tertinggi
peak_rental_df = main_df.groupby(["dteday", "workingday_hour"]).agg({"hr": lambda x: x.loc[main_df.loc[x.index, "cnt_hour"].idxmax()]})
peak_rental_df = peak_rental_df.reset_index()

# Membuat grafik dengan warna garis berbeda untuk hari kerja dan akhir pekan
fig, ax = plt.subplots(figsize=(16, 8))

# Menyiapkan variabel untuk menggambar garis
prev_day_type = peak_rental_df["workingday_hour"].iloc[0]
x_vals = [peak_rental_df["dteday"].iloc[0]]
y_vals = [peak_rental_df["hr"].iloc[0]]
colors = {1: "skyblue", 0: "orange"}

# Menggambar garis berdasarkan perubahan jenis hari
for i in range(1, len(peak_rental_df)):
    current_day_type = peak_rental_df["workingday_hour"].iloc[i]
    x_vals.append(peak_rental_df["dteday"].iloc[i])
    y_vals.append(peak_rental_df["hr"].iloc[i])
    
    # Jika jenis hari berubah, gambar garis dan mulai segmen baru
    if current_day_type != prev_day_type or i == len(peak_rental_df) - 1:
        ax.plot(x_vals, y_vals, marker='o', linewidth=2, color=colors[prev_day_type])
        x_vals = [peak_rental_df["dteday"].iloc[i]]
        y_vals = [peak_rental_df["hr"].iloc[i]]
        prev_day_type = current_day_type
        
# Menambahkan legenda di pojok kiri atas untuk tiap jenis warna garis
legend_labels = [plt.Line2D([0], [0], color="skyblue", marker='o', linestyle='', markersize=8, label="Hari Kerja"),
                plt.Line2D([0], [0], color="orange", marker='o', linestyle='', markersize=8, label="Akhir Pekan")]
ax.legend(handles=legend_labels, loc="upper left")

# Menampilkan grafik puncak penyewaan
ax.set_ylabel("[Rental Peak Hours]", fontsize=15)
ax.set_yticks([0, 4, 8, 12, 16, 20, 24])
ax.tick_params(axis='y', labelsize=12)
ax.tick_params(axis='x', labelsize=10)
st.pyplot(fig)

# Caption
st.caption('Copyright © Dimas Adista Perdana 2025, ありがとうございます。')