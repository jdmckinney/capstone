import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
#import joblib

from streamlit_option_menu import option_menu

from sklearn.ensemble import RandomForestRegressor

#model = joblib.load('capstone_model.sav')
@st.cache_resource
def gen_model():
    data= pd.read_csv('clean_data.zip')
    X = data.drop(columns=['demand'])
    y = data[['demand']].copy()
    model = RandomForestRegressor()
    model.fit(X, y)
    return model

model = gen_model()

def gen_cols(len):
    test = [[x/len,y/len] for x in range(len) for y in range(len)]
    df = pd.DataFrame((test + (0.15 * np.random.rand(len*len, 2))) / [25,25] + [40.75480, -111.888138] - [0.02,0.025], columns=['lat','lon'])
    df['mean'] = np.random.randint(10, high=100, size = len * len)
    return df

selected = option_menu(
    menu_title=None,
    options=["Predictions","Analytics","About"],
    icons=["graph-up","bar-chart","patch-question"],
    default_index=0,
    orientation="horizontal",
)

df = gen_cols(10)
if selected == "About":
    st.title("Hola")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        isWorkday = 1 if st.checkbox("Working Day?") else 0
    with col2:
        rain = st.slider('rain', 0.0, 1.0, 0.0)
    with col3:
        temp = st.slider('Temperature', 0.0, 104.0, 75.0) / 104.0

    if selected == "Predictions":

        hour = st.slider('hour', 0, 23, 12)/23.0
        
        demand_mult = model.predict([[isWorkday, hour, temp, rain]])
        
        df['demand'] =  df['mean'] * demand_mult

        df['demand'] = df['demand'] / 100
        
        deck = pdk.Deck(
            map_style=None,
            initial_view_state=pdk.ViewState(
                latitude=40.75,
                longitude=-111.8,
                zoom=11,
                pitch=50,
            ),
            layers=[
                pdk.Layer(
                    'ColumnLayer',
                    data=df,
                    get_position='[lon,lat]',
                    get_elevation='demand',
                    elevation_scale=1000,
                    radius=250,
                    get_fill_color=['demand * 255', 0, 0, 255],
                    pickable= False,
                    auto_highlight= False,
                ),
            ],
        )

        st.pydeck_chart(deck)


    elif selected == "Analytics":
        mean = 50

        arr = []
        for hour in range(24):
            arr.append([isWorkday, hour/23.0, temp, rain])
        df = pd.DataFrame(arr, columns=['isWorkday','time','temp','weather'])

        demands = model.predict(df) * mean

        st.bar_chart(demands)
