import streamlit as st
import geopandas as gpd

st.set_page_config(page_title="streamlit-folium documentation")

"# streamlit-folium"

data = gpd.read_file("Lower Manhattan2.geojson").to_crs(epsg=26914)

with st.echo():

    import streamlit as st
    from streamlit_folium import folium_static
    import folium
    import branca

    page = st.radio(
        "Select map type", ["Single map", "Dual map", "Branca figure"], index=0
    )

    uploaded_file = st.file_uploader("Upload Study Area Shapefile")

    if uploaded_file is None:
        dataframe = gpd.read_file(uploaded_file).to_crs(epsg=26914)
        m = folium.Map(location=[40.70, -73.94], zoom_start=10, tiles='CartoDB positron')
        folium.GeoJson(data=dataframe['geometry']).add_to(m)
    else:
        m = folium.Map(location=[40.70, -73.94], zoom_start=10, tiles='CartoDB positron')
        folium.GeoJson(data=data['geometry']).add_to(m)


    # call to render Folium map in Streamlit
    folium_static(m)

