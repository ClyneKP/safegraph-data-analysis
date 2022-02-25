import streamlit as st
import geopandas as gpd
import numpy as np
import shapestats_kc as shp
import matplotlib.pyplot as plt

st.set_page_config(page_title="streamlit-folium documentation")

"# streamlit-folium"

data = gpd.read_file("Lower Manhattan2.geojson").to_crs(epsg=26914)

with st.echo():

    import streamlit as st
    from streamlit_folium import folium_static
    import folium

    uploaded_file = st.file_uploader("Upload Study Area Shapefile")

    if uploaded_file is None:
        m = folium.Map(location=[40.70, -73.94], zoom_start=10, tiles='CartoDB positron')
        folium.GeoJson(data=data['geometry']).add_to(m)
    else:
        dataframe = gpd.read_file(uploaded_file).to_crs(epsg=4326)
        geometry = dataframe['geometry']
        bbox = dataframe.total_bounds
        st.write(bbox)
        m = folium.Map(location=[40.70, -73.94], tiles='CartoDB positron')
        m.fit_bounds([[bbox[0],bbox[3]],[bbox[2],bbox[1]]])
        folium.GeoJson(data=geometry).add_to(m)


    # call to render Folium map in Streamlit
    folium_static(m)

