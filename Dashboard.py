import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from PIL import Image
from streamlit_option_menu import option_menu
from sklearn.ensemble import RandomForestRegressor


@st.cache_resource
def generate_model():
    data = pd.read_csv('clean_data.zip')
    X = data.drop(columns=['demand', 'month', 'holiday', 'weekday'])
    y = data[['demand']].copy()
    model = RandomForestRegressor()
    model.fit(X, y)
    return model, data


@st.cache_data
def get_stations():
    return pd.read_csv('stations.zip')


model, data = generate_model()
station = get_stations()


selected = option_menu(
    menu_title=None,
    options=["City Overview", "Day Summary", "Analysis"],
    icons=["app",  "graph-up", "bar-chart"],
    default_index=0,
    orientation="horizontal",
)


if selected != "Analysis":

    col1, col2, col3 = st.columns(3)
    with col1:
        isWorkday = 1 if st.checkbox("Working Day?") else 0
    with col2:
        weathers = {'Clear': 0, 'Cloudy': 0.25, 'Muggy': 0.4, 'Foggy': 0.55, 'Sprinkling': 0.7,
                    'Light Rain/Snow': 0.9, 'Moderate Rain/Snow': 0.95, 'Heavy Rain/Snow': 1,
                    'Stormy': 1}
        rain = weathers[st.select_slider(
            'Weather', options=weathers.keys(), value='Clear')]
    with col3:
        temp = st.slider('"Feels Like" Temperature (Fahrenheit)',
                         10.0, 104.0, 75.0) / 104.0

    if selected == "City Overview":

        hour = st.slider('Hour of Day', 0, 23, 12)/23.0

        demand_mult = model.predict([[hour, isWorkday, temp, rain]])

        station['demand'] = station['mean'] * demand_mult

        hour_total = int(station.demand.sum())

        station['col_height'] = station['demand'] / 10

        deck = pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=40.75,
                longitude=-111.88,
                zoom=11,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ColumnLayer',
                    data=station,
                    get_position='[lon,lat]',
                    get_elevation='col_height',
                    elevation_scale=1000,
                    radius=250,
                    get_fill_color=['col_height * 255', 0, 0, 255],
                    pickable=False,
                    auto_highlight=False,
                ),
            ],
        )

        st.pydeck_chart(deck)

        st.title("Hour Total: " + str(hour_total))

    elif selected == "Day Summary":
        mean = st.slider('Station Hourly Average', 0, 30, 10)

        arr = []
        for hour in range(24):
            arr.append([hour/23.0, isWorkday, temp, rain])
        day = pd.DataFrame(
            arr, columns=['hour', 'isWorkday', 'temp', 'weather'])

        demands = model.predict(day) * mean
        demands = [int(x) for x in demands]
        # st.bar_chart(demands)
        st.line_chart(demands)

        d_sum = 0
        for d in demands:
            d_sum += d
        st.title("Day Total: " + str(d_sum))
else:

    month_data = pd.DataFrame()
    month_data['Demand'] = data.groupby('month').demand.mean()
    month_data['Temperature'] = data.groupby('month').temp.mean()

    st.title("Average Demand by Month")
    st.bar_chart(data.groupby('month').demand.mean())
    st.title("Average Temperature by Month")
    st.bar_chart(data.groupby('month').temp.mean())

    weekdayTrends = Image.open("Images/WeekdayTrends.png")
    workdayTrends = Image.open("Images/WorkdayTrends.png")
    corr = Image.open("Images/Correlation.png")

    st.title("Hourly Demand Trends of Weekdays")
    st.image(weekdayTrends)
    st.title("Hourly Demand Trends for Workdays")
    st.image(workdayTrends)
    st.title("Data Feature Correlation Matrix")
    st.image(corr)
