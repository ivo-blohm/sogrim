import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import json

st.set_page_config(
    page_title="Sogrim",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache
def load_data():
  with open('data.json') as f:
    json_data = json.load(f)
    gpd_data = gpd.GeoDataFrame.from_features(json_data.features)
    return gpd_data


@st.cache
def get_data_unit(feature):
  data_unit = {
      "BEVDICHTE_SQKM_2019": "p/sqkm",
      "AUSLAENDER_ANTEIL_2019": "%",
      "ALTERSVERTEILUNG_ANTEIL_0_19_2019": "%",
      "ALTERSVERTEILUNG_ANTEIL_20_64_2019": "%",
      "ALTERSVERTEILUNG_ANTEIL_65PLUS_2019": "%",
      "PRIVATHAUSHALTE_2019": "Hshlt.",
      "GESAMTFLAECHE_SQKM_2016": "sqkm",
      "LANDWIRTSCHAFTSFLAECHE_ANTEIL_2004": "%",
      "WALD_GEHOELZE_ANTEIL_2004": "%",
      "UNPRODUKTIVE_FLAECHE_ANTEIL_2004": "%",
      "BESCHAEFTIGTE_ERSTERSEKTOR_2018": "p.",
      "BESCHAEFTIGTE_ZWEITERSEKTOR_2018": "p.",
      "BESCHAEFTIGTE_DRITTERSEKTOR_2018": "p.",
      "NEUWOHNUNGEN_PRO_1000_2018": "Wo./1,000p",
      "SOZAILHILFEQUOTE_2019": "%",
      "WAEHLERANTEIL_SP_2019": "%",
      "WAEHLERANTEIL_SVP_2019": "%",
      "AVG_INCOME_PRO_STEUERPFLPERSON": "Chf/p.",
      "ANZAHL_FAHRZEUGE": "Fhrz.",
      "ANZAHL_HALTESTELLEN_OV": "Hltst.",
      "ANZAHL_FILIALEN_MIGROS": "Fil."
  }
  return data_unit[feature]


st.sidebar.title("Sogrim")
nav = st.sidebar.radio(
    "Navigation", ("TEST", "Data Exploration", "Location Optimizer"))
st.sidebar.header("About")
st.sidebar.write("""The purpose of SOGRIM is to help Migros optimize their store locations.
For this purpose, we leverage a wide range of data points from various pubic data sources such as the Federal Bureau of Statistics.""")

data = load_data()

if nav == "Data Exploration":
  st.write("This is Data Exploration")
  choice_data_exp = st.selectbox("Select a Feature", list(data.columns))
  col1, col2, col3, col4, col5, col6 = st.columns(6)
  col1.metric("Min", str(data[choice_data_exp].min().round(
      2))+" "+get_data_unit(choice_data_exp))
  col2.metric("q1", str(data[choice_data_exp].quantile(
      q=0.25).round(2))+" "+get_data_unit(choice_data_exp))
  col3.metric("Average", str(data[choice_data_exp].mean().round(
      2))+" "+get_data_unit(choice_data_exp))
  col4.metric("q3", str(data[choice_data_exp].quantile(
      q=0.75).round(2))+" "+get_data_unit(choice_data_exp))
  col5.metric("Max", str(data[choice_data_exp].max().round(
      2))+" "+get_data_unit(choice_data_exp))
  col6.metric("SD", str(data[choice_data_exp].std().round(
      2))+" "+get_data_unit(choice_data_exp))
  fig = px.histogram(data[choice_data_exp], nbins=int(
      len(data[choice_data_exp])**0.5))
  st.plotly_chart(fig, use_container_width=True)
  st.dataframe(data)

elif nav == "Location Optimizer":
  col1, col2 = st.columns(2)
  choice_model = col1.selectbox("Select a Model", ["linregModel","knnModel","rfModel","xgbrModel","ensemble"])
  choice_option = col2.selectbox(
      "Select a Group", ("Consolidation", "Perfect", "Opportunities"))

  if choice_option == "Consolidation":
    location_data = data[data[choice_model]
                                < data.ANZAHL_FILIALEN_MIGROS]
  elif choice_option == "Perfect":
    location_data = data[data[choice_model]
                                == data.ANZAHL_FILIALEN_MIGROS]
  elif choice_option == "Opportunities":
    location_data = data[data[choice_model]
                                > data.ANZAHL_FILIALEN_MIGROS]

  col1, col2, col3 = st.columns(3)

  col1.metric("# Consolidations", len(
      data[data[choice_model] < data.ANZAHL_FILIALEN_MIGROS]))
  col2.metric("# Same", len(
      data[data[choice_model] == data.ANZAHL_FILIALEN_MIGROS]))
  col3.metric("# Opportunities", len(
      data[data[choice_model] > data.ANZAHL_FILIALEN_MIGROS]))

  st.map(location_data[[choice_model, "lat", "lon"]])

  st.dataframe(location_data.drop(["lat", "lon"], axis=1))

  # fig = px.choropleth_mapbox(geo_df,
  #                          geojson=geo_df.geometry,
  #                          locations=geo_df.index,
  #                          color="ANZAHL_FILIALEN_MIGROS",
  #                          center={"lat": 45.5517, "lon": -73.7073},
  #                          mapbox_style="open-street-map",
  #                          zoom=8.5)

  # st.map(fig)

elif nav == "TEST":
  fig = px.choropleth_mapbox(data,
                           geojson=data.geometry,
                           locations=data.index,
                           color="ANZAHL_FILIALEN_MIGROS",
                           center={"lat": 46.9, "lon": 8.2275},
                           mapbox_style="open-street-map",
                           zoom=7,
                           color_continuous_scale="Viridis",
                           opacity=0.5)

  st.map(fig)
