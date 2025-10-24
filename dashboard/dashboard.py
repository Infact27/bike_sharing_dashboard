import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import calendar

# create_byday_df() digunakan untuk menyiapkan byday_df
def create_byday_df(df):
    byday_df = df.groupby(by="dteday").cnt.sum().reset_index()
    byday_df.rename(columns={
        "cnt": "rental_count"
    }, inplace=True)
    
    return byday_df

# create_byseason_df() digunakan untuk menyiapkan byseason_df
def create_byseason_df(df):
    season_backmapping = {'Winter': 1, 'Spring': 2, 'Summer': 3, 'Fall': 4}
    df['season'] = df['season'].map(season_backmapping)

    byseason_df = df.groupby(by="season").cnt.mean().reset_index()
    byseason_df.rename(columns={
        "cnt": "rental_count"
    }, inplace=True)
    byseason_df['season'] = byseason_df['season'].map({1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'})
    
    return byseason_df

# create_byweather_df() digunakan untuk menyiapkan byweather_df
def create_byweather_df(df):
    weathersit_backmapping = {'Clear': 1, 'Mist + Cloudy': 2, 'Light Snow/Rain': 3, 'Heavy Rain/Snow': 4}
    df['weathersit'] = df['weathersit'].map(weathersit_backmapping)
    byweather_df = df.groupby(by="weathersit").cnt.mean().reset_index()
    byweather_df.rename(columns={
        "cnt": "rental_count"
    }, inplace=True)
    byweather_df['weathersit'] = byweather_df['weathersit'].map({1: 'Clear', 2: 'Mist + Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'})
    return byweather_df

def create_bymonth_df(df):
    df['month'] = df['dteday'].dt.month
    bymonth_df = df.groupby(by="month").cnt.sum().reset_index()
    bymonth_df.rename(columns={
        "cnt": "rental_count"
    }, inplace=True)
    bymonth_df['month'] = bymonth_df['month'].apply(lambda x: calendar.month_name[x])
    return bymonth_df

st.title("Dashboard Bike Sharing Analysis")
df = pd.read_csv('dashboard/day.csv')

# mengubah tipe data kolom dteday menjadi datetime
df['dteday'] = pd.to_datetime(df['dteday'])

# Menyiapkan filter di sidebar
min_date = df['dteday'].min()
max_date = df['dteday'].max()

season_mapping = {1: 'Winter', 2: 'Spring', 3: 'Summer', 4: 'Fall'}
df['season'] = df['season'].map(season_mapping)

weathersit_mapping = {1: 'Clear', 2: 'Mist + Cloudy', 3: 'Light Snow/Rain', 4: 'Heavy Rain/Snow'}
df['weathersit'] = df['weathersit'].map(weathersit_mapping)

# memasang filter di sidebar
with st.sidebar:
    st.header("Filter Data")
    date_range = st.date_input(
    "Pilih rentang tanggal",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
    )
    
    st.multiselect(
        label="Pilih musim",
        options=df['season'].unique(),
        default=df['season'].unique(),
        key='season_filter'
    )

    st.multiselect(
        label="Pilih cuaca",
        options=df['weathersit'].unique(),
        default=df['weathersit'].unique(),
        key='weather_filter'
    )




# Memfilter DataFrame berdasarkan filter yang dipilih
filtered_df = df[
    (df['dteday'] >= pd.to_datetime(date_range[0])) &
    (df['dteday'] <= pd.to_datetime(date_range[1])) &
    (df['season'].isin(st.session_state.season_filter)) &
    (df['weathersit'].isin(st.session_state.weather_filter))
]

# Membuat DataFrame untuk setiap visualisasi
day_df = create_byday_df(filtered_df)
season_df = create_byseason_df(filtered_df)
weather_df = create_byweather_df(filtered_df)
monthly_df = create_bymonth_df(filtered_df)

# memvisualisasikan day_df, season_df, dan weather_df sesuai kebutuhan dashboard

# visualisasi data berdasarkan filter yang diterapkan
st.header("Bike Sharing Analysis Dashboard :bike:")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Total And Average Rentals")
    total = filtered_df['cnt'].sum()
    st.metric(label="Total Rentals", value=total)
    avg = filtered_df['cnt'].mean()
    st.metric(label="Average Daily Rentals", value=f"{avg:.2f}")
with col2:
    st.subheader("Max and Min Daily Rentals")
    max_rentals = filtered_df['cnt'].max()
    st.metric(label="Maximum Daily Rentals", value=max_rentals)
    min_rentals = filtered_df['cnt'].min()
    st.metric(label="Minimum Daily Rentals", value=min_rentals)
st.subheader("Daily Rentals Over Time")
st.line_chart(day_df.set_index('dteday')['rental_count'])

# visualisasi total rentals per month
st.subheader("Total Rentals per Month")
fig, ax = plt.subplots(figsize=(10, 6))
colors = "skyblue"
sns.barplot(x="month", y="rental_count", data=monthly_df, ax=ax)
ax.set_ylabel("Total Rentals")
ax.set_xlabel("Month")
ax.set_title("Total Rentals by Month")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(rotation=45)
st.pyplot(fig)

st.markdown("#### Insight")
st.write("August has the highest total rentals, possibly due to favorable weather conditions and vacation periods, while February has the lowest rentals, likely influenced by colder weather.")
st.write("January has the lowest total rentals, possibly due to post-holiday season and colder weather conditions.")

# visualisasi average rentals by season
st.subheader("Average Rentals by Season")
fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette("pastel")
sns.barplot(x="season", y="rental_count", data=season_df, palette=colors, ax=ax)
ax.set_ylabel("Average Rentals")
ax.set_xlabel("Season")
ax.set_title("Average Rentals by Season")
st.pyplot(fig)
st.markdown("#### Insight")
st.write("Summer has the highest average rentals, likely due to favorable weather conditions and vacation periods, while Winter has the lowest rentals, likely influenced by colder weather.")
st.write("Winter has the lowest average rentals, possibly due to colder weather conditions and shorter daylight hours.")

# visualisasi average rentals by weather situation
st.subheader("Average Rentals by Weather Situation")
fig, ax = plt.subplots(figsize=(10, 6))
colors = sns.color_palette("muted")
sns.barplot(x="weathersit", y="rental_count", data=weather_df, palette=colors, ax=ax)
ax.set_ylabel("Average Rentals")
ax.set_xlabel("Weather Situation")
ax.set_title("Average Rentals by Weather Situation")
st.pyplot(fig)
st.markdown("#### Insight")
st.write("Clear weather conditions lead to the highest average rentals, while heavy rain/snow conditions result in the lowest rentals, indicating that weather significantly impacts bike rental behavior.")
st.write("Light rain/snow conditions lead to the lowest average rentals, while clear weather results in the highest rentals, indicating that weather significantly impacts bike rental behavior.")
