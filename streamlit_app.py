import streamlit as st
import geopandas as gpd
import numpy as np
import shapestats_kc as shp
import matplotlib.pyplot as plt
from folium.plugins import Draw
from streamlit_folium import st_folium
from streamlit_folium import folium_static
import folium


st.set_page_config(page_title="streamlit-folium documentation")

form = st.form(key="inputs")
with form:
    uploaded_file = st.file_uploader("Upload Study Area Shapefile")
    submitted = st.form_submit_button(label="Submit")


    m = folium.Map(location=[40.70, -73.94], zoom_start=10, tiles='CartoDB positron')
    Draw(export=False).add_to(m)

    if uploaded_file is not None:
        dataframe = gpd.read_file(uploaded_file).to_crs(epsg=4326)
        geometry = dataframe['geometry']
        bbox = dataframe.total_bounds
        m.fit_bounds([[bbox[1],bbox[0]],[bbox[3],bbox[2]]], padding=[20,20])
        folium.GeoJson(data=geometry).add_to(m)


    # call to render Folium map in Streamlit
    folium_static(m)

