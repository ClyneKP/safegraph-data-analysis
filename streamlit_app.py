import streamlit as st
from folium.plugins import Draw
from streamlit_folium import folium_static
import geemap.eefolium as geemap
import ipywidgets as widgets
from ipyleaflet import WidgetControl
from geemap import geojson_to_ee
from mycomponent import mycomponent
import ee

# os.environ["EARTHENGINE_TOKEN"] == st.secrets["EARTHENGINE_TOKEN"]
service_account = "admin-815@earth-engine-342417.iam.gserviceaccount.com"
credentials = ee.ServiceAccountCredentials(service_account, 'earth-engine-342417-f19485aba489.json')
ee.Initialize(credentials)
"# streamlit geemap demo"

import streamlit as st
from streamlit_folium import folium_static
import geemap.eefolium as geemap
import ee

m = geemap.Map(center=[40.70, -73.94], zoom=4)
Draw(export=False).add_to(m)
dem = ee.Image('USGS/SRTMGL1_003')

vis_params = {
'min': 0,
'max': 4000,
'palette': ['006633', 'E5FFCC', '662A00', 'D8D8D8', 'F5F5F5']}

m.addLayer(dem, vis_params, 'SRTM DEM', True, 1)
m.addLayerControl()

# call to render Folium map in Streamlit
folium_static(m)

value = mycomponent(my_input_value="hello there")
st.write("Received", value)