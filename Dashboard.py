import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from streamlit_option_menu import option_menu

from sklearn.ensemble import RandomForestRegressor


@st.cache_resource
def generate_model():
    data = pd.read_csv('clean_data.zip')
    X = data.drop(columns=['demand'])
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
    options=["City Overview", "Day Summary", "Analytics"],
    icons=["app",  "graph-up", "bar-chart"],
    default_index=0,
    orientation="horizontal",
)


if selected != "Analytics":

    col1, col2, col3 = st.columns(3)
    with col1:
        isWorkday = 1 if st.checkbox("Working Day?") else 0
    with col2:
        rain = st.slider('rain', 0.0, 1.0, 0.0)
    with col3:
        temp = st.slider('Temperature', 0.0, 104.0, 75.0) / 104.0

    if selected == "City Overview":

        hour = st.slider('hour', 0, 23, 12)/23.0

        demand_mult = model.predict([[isWorkday, hour, temp, rain]])

        station['demand'] = station['mean'] * demand_mult

        station['demand'] = station['demand'] / 100

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
                    get_elevation='demand',
                    elevation_scale=1000,
                    radius=250,
                    get_fill_color=['demand * 255', 0, 0, 255],
                    pickable=False,
                    auto_highlight=False,
                ),
            ],
        )

        st.pydeck_chart(deck)

    elif selected == "Day Summary":
        mean = 50

        arr = []
        for hour in range(24):
            arr.append([isWorkday, hour/23.0, temp, rain])
        day = pd.DataFrame(
            arr, columns=['isWorkday', 'time', 'temp', 'weather'])

        demands = model.predict(day) * mean
        demands = [int(x) for x in demands]
        # st.bar_chart(demands)
        st.line_chart(demands)
else:
    st.title("Hola")
