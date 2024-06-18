import streamlit as st
import rasterio
import streamlit.components as components
import pandas as pd
from pyproj import Proj, Transformer

st.set_page_config(layout="wide")
# CSS to set the background color
css = """
<style>
body {
    background-color: #8B0000;
}
</style>
"""
'''
st.markdown(css, unsafe_allow_html=True)
# Customize the sidebar
markdown = """
This application uses www.floodmapviewer.com raster data to calculate potential flooding damage to properties.
"""
#st.markdown(markdown)
st.sidebar.title("About")
st.sidebar.info(markdown)
logo1 = "https://adersim.info.yorku.ca/files/2024/05/adersim.jpg"
st.sidebar.image(logo1)
logo2 = "https://www.yorku.ca/cifal/wp-content/uploads/sites/437/2021/12/team.jpg"
st.sidebar.image(logo2)
# Customize page title
st.title("Multi-Floor Flood Damage Assessment App- Golden Horseshoe (Ontario)")
'''
# Flood_rasters dictionary
flood_rasters = {
    "Flood 25": "https://drive.google.com/uc?export=download&id=1AbG8G1QfX17Htfl1DnfmlD3MsGa45GzE",
    "Flood 50": "https://drive.google.com/uc?export=download&id=1IcubfEqXA1aznGDEwuMJBPUMDtlMxXOy",
    "Flood 100": "https://drive.google.com/uc?export=download&id=16NWqHv-VOLwx38-b9TduWtWQ_cUFk_WK",
    "Flood 150": "https://drive.google.com/uc?export=download&id=1qK9xK5eCDR3lZR7hqEbZZwAgYec_bvWL",
    "Flood 200": "https://drive.google.com/uc?export=download&id=17WP20nHe0XVIQYjjDsnOyYS4nUnDJE0t",
    "Flood 300": "https://drive.google.com/uc?export=download&id=1Zojp4Sue2B84w9SFShoW5eCp7W9BOsQj",
    "Flood 500": "https://drive.google.com/uc?export=download&id=1-gz9WDvcFc5FrZpIdGr4VU3QOaGGP68G",
    "Slope": "https://drive.google.com/uc?export=download&id=1hj-r59TyGlKo2QXhIiRd84FZxVRQEaLz",
    "Height Above Nearest Drainage": "https://drive.google.com/uc?export=download&id=1si6bmzgPKD4W3utmZC3jBdagFJgSsle6",
    "Distance to Streams": "https://drive.google.com/uc?export=download&id=1RnMSW1_6qMhRcm192_UTQxqTnmPRF-Hj",
    "Curve Number": "https://drive.google.com/uc?export=download&id=1WAubdImsxJbv5BP16w0a0c6rjqZ7c8OT",
    "Total Precipitation": "https://drive.google.com/uc?export=download&id=1igKY0RniaXr9aAxpWGc8Ed8AHeIDEww2",
    "Effective Precipitation": "https://drive.google.com/uc?export=download&id=1ZCAicP9lvVLHu9PrWqaLauQg01Sp33ih"
    
}

def latlon_to_xy(lat, lon, dataset):
    transformer = Transformer.from_crs("epsg:4326", dataset.crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y

def get_raster_value(lat, lon, raster_path):
    try:
        with rasterio.open(raster_path) as dataset:
            x, y = latlon_to_xy(lat, lon, dataset)
            row, col = dataset.index(x, y)
            if 0 <= row < dataset.height and 0 <= col < dataset.width:
                return dataset.read(1)[row, col]
            else:
                return None  # Return None if out of bounds
    except Exception as e:
        return f"Error: {str(e)}"

def show_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], tooltip='Click me!', popup='Coordinates').add_to(m)
    return m


def show_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=13)
    folium.Marker([lat, lon], tooltip='Click me!', popup='Coordinates').add_to(m)
    return m

#main
#latitude = 43.55
#longitude = -79.58
st.markdown("""
<style>
.title-font {
    font-size:20px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Create two columns for the inputs
col1, col2 = st.columns(2)
# Use the first column for latitude input
latitude = col1.number_input("Enter latitude:", value=43.550243681701424)
# Use the second column for longitude input
longitude = col2.number_input("Enter longitude:", value=-79.58122729155784)

####
data = {}

floors = ['Basement', 'First Floor', 'Second Floor', 'Third Floor', 'Fourth Floor']


#print(flood_rasters.items())
flood_types = []
flood_values = []
damage_percentages = []
content_damages = []

for flood_type, path in flood_rasters.items():
    flood_types.append(flood_type)
    raster_value = get_raster_value(latitude, longitude, path)
    #content_damage = calculate_content_damage(raster_value)
    ####
    data[flood_type] = raster_value

st.write("Prompt is:\n", data)
####************************
df = pd.DataFrame(data, [1])

df['Slope'] = df['Slope']*100

#print(df)

#DS

df.loc[df['Distance to Streams']<=100, ['DS_C']] = 5
df.loc[(df['Distance to Streams']>100) & (df['Distance to Streams']<=300), ['DS_C']] = 4
df.loc[(df['Distance to Streams']>300) & (df['Distance to Streams']<=500), ['DS_C']] = 3
df.loc[(df['Distance to Streams']>500) & (df['Distance to Streams']<=1000), ['DS_C']] = 2
df.loc[df['Distance to Streams']>1000, ['DS_C']] = 1

df.loc[df['Distance to Streams']<=100, ['Distance to Streams Level']] = 'Very low'
df.loc[(df['Distance to Streams']>100) & (df['Distance to Streams']<=300), ['Distance to Streams Level']] = 'Low'
df.loc[(df['Distance to Streams']>300) & (df['Distance to Streams']<=500), ['Distance to Streams Level']] = 'Medium'
df.loc[(df['Distance to Streams']>500) & (df['Distance to Streams']<=1000), ['Distance to Streams Level']] = 'High'
df.loc[df['Distance to Streams']>1000, ['Distance to Streams Level']] = 'Very high'

df.loc[df['Distance to Streams']<=100, ['Distance to Streams Flodd Risk Level']] = 'Very high'
df.loc[(df['Distance to Streams']>100) & (df['Distance to Streams']<=300), ['Distance to Streams Flodd Risk Level']] = 'High'
df.loc[(df['Distance to Streams']>300) & (df['Distance to Streams']<=500), ['Distance to Streams Flodd Risk Level']] = 'Medium'
df.loc[(df['Distance to Streams']>500) & (df['Distance to Streams']<=1000), ['Distance to Streams Flodd Risk Level']] = 'Low'
df.loc[df['Distance to Streams']>1000, ['Distance to Streams Flood Risk Level']] = 'Very low'

#CN
'''
df.loc[df['Curve Number']==94, ['CN_C']] = 5
df.loc[(df['Curve Number']==90) | (df['Curve Number']==91), ['CN_C']] = 4
df.loc[df['Curve Number']==86, ['CN_C']] = 3
df.loc[df['Curve Number']==79, ['CN_C']] = 2
df.loc[df['Curve Number']==74, ['CN_C']] = 1

df.loc[df['Curve Number']==94, ['Curve Number Level']] = 'Very high'
df.loc[(df['Curve Number']==90) | (df['Curve Number']==91), ['Curve Number Level']] = 'High'
df.loc[df['Curve Number']==86, ['Curve Number Level']] = 'Medium'
df.loc[df['Curve Number']==79, ['Curve Number Level']] = 'Low'
df.loc[df['Curve Number']==74, ['Curve Number Level']] = 'Very low'

df.loc[df['Curve Number']==94, ['Curve Number Flodd Risk Level']] = 'Very high'
df.loc[(df['Curve Number']==90) | (df['Curve Number']==91), ['Curve Number Flood Risk Level']] = 'High'
df.loc[df['Curve Number']==86, ['Curve Number Flood Risk Level']] = 'Medium'
df.loc[df['Curve Number']==79, ['Curve Number Flood Risk Level']] = 'Low'
df.loc[df['Curve Number']==74, ['Curve Number Flood Risk Level']] = 'Very low'
'''

#TP
df.loc[df['Total Precipitation']<=79.9, ['TP_C']] = 1
df.loc[(df['Total Precipitation']>79.9) & (df['Total Precipitation']<=81.2), ['TP_C']] = 2
df.loc[(df['Total Precipitation']>81.2) & (df['Total Precipitation']<=82.3), ['TP_C']] = 3
df.loc[(df['Total Precipitation']>82.3) & (df['Total Precipitation']<=83.2), ['TP_C']] = 4
df.loc[df['Total Precipitation']>83.2, ['TP_C']] = 5

df.loc[df['Total Precipitation']<=79.9, ['Total Precipitation Level']] = 'Very low'
df.loc[(df['Total Precipitation']>79.9) & (df['Total Precipitation']<=81.2), ['Total Precipitation Level']] = 'Low'
df.loc[(df['Total Precipitation']>81.2) & (df['Total Precipitation']<=82.3), ['Total Precipitation Level']] = 'Medium'
df.loc[(df['Total Precipitation']>82.3) & (df['Total Precipitation']<=83.2), ['Total Precipitation Level']] = 'High'
df.loc[df['Total Precipitation']>83.2, ['Total Precipitation Level']] = 'Very high'

df.loc[df['Total Precipitation']<=79.9, ['Total Precipitation Flodd Risk Level']] = 'Very low'
df.loc[(df['Total Precipitation']>79.9) & (df['Total Precipitation']<=81.2), ['Total Precipitation Flood Risk Level']] = 'Low'
df.loc[(df['Total Precipitation']>81.2) & (df['Total Precipitation']<=82.3), ['Total Precipitation Flood Risk Level']] = 'Medium'
df.loc[(df['Total Precipitation']>82.3) & (df['Total Precipitation']<=83.2), ['Total Precipitation Flodd Risk Level']] = 'High'
df.loc[df['Total Precipitation']>83.2, ['Total Precipitation Flood Risk Level']] = 'Very high'

#EP
df.loc[df['Effective Precipitation']<=36.2, ['EP_C']] = 1
df.loc[(df['Effective Precipitation']>36.2) & (df['Effective Precipitation']<=49.2), ['EP_C']] = 2
df.loc[(df['Effective Precipitation']>49.2) & (df['Effective Precipitation']<=58), ['EP_C']] = 3
df.loc[(df['Effective Precipitation']>58) & (df['Effective Precipitation']<=65.1), ['EP_C']] = 4
df.loc[df['Effective Precipitation']>65.1, ['EP_C']] = 5

df.loc[df['Effective Precipitation']<=36.2, ['Effective Precipitation Level']] = 'Very low'
df.loc[(df['Effective Precipitation']>36.2) & (df['Effective Precipitation']<=49.2), ['Effective Precipitation Level']] = 'Low'
df.loc[(df['Effective Precipitation']>49.2) & (df['Effective Precipitation']<=58), ['Effective Precipitation Level']] = 'Medium'
df.loc[(df['Effective Precipitation']>58) & (df['Effective Precipitation']<=65.1), ['Effective Precipitation Level']] = 'High'
df.loc[df['Effective Precipitation']>65.1, ['Effective Precipitation Level']] = 'Very high'

df.loc[df['Effective Precipitation']<=36.2, ['Effective Precipitation Flodd Risk Level']] = 'Very low'
df.loc[(df['Effective Precipitation']>36.2) & (df['Effective Precipitation']<=49.2), ['Effective Precipitation Flood Risk Level']] = 'Low'
df.loc[(df['Effective Precipitation']>49.2) & (df['Effective Precipitation']<=58), ['Effective Precipitation Flood Risk Level']] = 'Medium'
df.loc[(df['Effective Precipitation']>58) & (df['Effective Precipitation']<=65.1), ['Effective Precipitation Flood Risk Level']] = 'High'
df.loc[df['Effective Precipitation']>65.1, ['Effective Precipitation Flood Risk Level']] = 'Very high'

#Slope
df.loc[df['Slope']<=10, ['S_C']] = 5
df.loc[(df['Slope']>10) & (df['Slope']<=20), ['S_C']] = 4
df.loc[(df['Slope']>20) & (df['Slope']<=30), ['S_C']] = 3
df.loc[(df['Slope']>30) & (df['Slope']<=50), ['S_C']] = 2
df.loc[df['Slope']>50, ['S_C']] = 1

df.loc[df['Slope']<=10, ['Slope Level']] = 'Very low'
df.loc[(df['Slope']>10) & (df['Slope']<=20), ['Slope Level']] = 'Low'
df.loc[(df['Slope']>20) & (df['Slope']<=30), ['Slope Level']] = 'Medium'
df.loc[(df['Slope']>30) & (df['Slope']<=50), ['Slope Level']] = 'High'
df.loc[df['Slope']>50, ['Slope Level']] = 'Very high'

df.loc[df['Slope']<=10, ['Slope Flodd Risk Level']] = 'Very high'
df.loc[(df['Slope']>10) & (df['Slope']<=20), ['Slope Flodd Risk Level']] = 'High'
df.loc[(df['Slope']>20) & (df['Slope']<=30), ['Slope Flodd Risk Level']] = 'Medium'
df.loc[(df['Slope']>30) & (df['Slope']<=50), ['Slope Flodd Risk Level']] = 'Low'
df.loc[df['Slope']>50, ['Slope Flood Risk Level']] = 'Very low'


#HAND
df.loc[df['Height Above Nearest Drainage']<=2, ['HAND_C']] = 5
df.loc[(df['Height Above Nearest Drainage']>2) & (df['Height Above Nearest Drainage']<=4), ['HAND_C']] = 4
df.loc[(df['Height Above Nearest Drainage']>4) & (df['Height Above Nearest Drainage']<=6), ['HAND_C']] = 3
df.loc[(df['Height Above Nearest Drainage']>6) & (df['Height Above Nearest Drainage']<=8), ['HAND_C']] = 2
df.loc[df['Height Above Nearest Drainage']>8, ['HAND_C']] = 1

df.loc[df['Height Above Nearest Drainage']<=2, ['Height Above Nearest Drainage Level']] = 'Very low'
df.loc[(df['Height Above Nearest Drainage']>2) & (df['Height Above Nearest Drainage']<=4), ['Height Above Nearest Drainage Level']] = 'Low'
df.loc[(df['Height Above Nearest Drainage']>4) & (df['Height Above Nearest Drainage']<=6), ['Height Above Nearest Drainage Level']] = 'Medium'
df.loc[(df['Height Above Nearest Drainage']>6) & (df['Height Above Nearest Drainage']<=8), ['Height Above Nearest Drainage Level']] = 'High'
df.loc[df['Height Above Nearest Drainage']>8, ['Height Above Nearest Drainage Level']] = 'Very high'

df.loc[df['Height Above Nearest Drainage']<=2, ['Height Above Nearest Drainage Flodd Risk Level']] = 'Very high'
df.loc[(df['Height Above Nearest Drainage']>2) & (df['Height Above Nearest Drainage']<=4), ['Height Above Nearest Drainage Flodd Risk Level']] = 'High'
df.loc[(df['Height Above Nearest Drainage']>4) & (df['Height Above Nearest Drainage']<=6), ['Height Above Nearest Drainage Flodd Risk Level']] = 'Medium'
df.loc[(df['Height Above Nearest Drainage']>6) & (df['Height Above Nearest Drainage']<=8), ['Height Above Nearest Drainage Flodd Risk Level']] = 'Low'
df.loc[df['Height Above Nearest Drainage']>8, ['Height Above Nearest Drainage Flood Risk Level']] = 'Very low'

#FP
#df.loc[df['Floodplain']=='In', ['FP_C']] = 5
#df.loc[df['Floodplain']=='Out', ['FP_C']] = 2

#df.loc[df['Floodplain']=='In', ['Floodplain Flood Risk Level']] = 'Very high'
#df.loc[df['Floodplain']=='Out', ['Floodplain Flood Risk Level']] = 'Low'

#Class
df['Class'] = ((df['S_C']+df['HAND_C']+df['DS_C']+df['TP_C']+df['EP_C'])//5)+1

#Level
df.loc[df['Class']==5, ['Level']] = 'Very high'
df.loc[df['Class']==4, ['Level']] = 'High'
df.loc[df['Class']==3, ['Level']] = 'Medium'
df.loc[df['Class']==2, ['Level']] = 'Low'
df.loc[df['Class']==1, ['Level']] = 'Very low'

#print(df)
def generate_on_user_info(row):
    # Prompt template generates the texts
    prompt_template = """<s>[INST]
    You are a risk team member for an insurance company evaluating a
    homeowner insurance policy for a property in a flood plain. Develop a detailed
    vulnerability assessment of the property, considering factors like building
    elevation, foundation type, floodproofing measures, and proximity to water
    sources.

    Property Details:

    Slope Level = {Slope_Level}
    Slope Flood Risk Level = {Slope_Flood_Risk_Level}
    Height Above Nearest Drainage Level = {HAND_L}
    Height Above Nearest Drainage Flood Risk Level = {HAND_FRL}
    Distance to Streams Level = {DS_L}
    Distance to Streams Flood Risk Level = {DS_FRL}

    Total Precipitation Level = {TP_L}
    Total Precipitation Flood Risk Level = {TP_FRL}
    Effective Precipitation Level = {EP_L}
    Effective Precipitation Flood Risk Level = {EP_FRL}

    total flood risk level = {total_flood_risk_level}
    You need to write a short essay that includes all the given information somewhere in the essay.
    Do not miss out any.[/INST]"""

    #user_id = row['ID Number']
    Slope_Level = row['Slope Level']
    Slope_Flood_Risk_Level = row['Slope Flood Risk Level']
    HAND_L = row['Height Above Nearest Drainage Level']
    HAND_FRL = row['Height Above Nearest Drainage Flood Risk Level']
    DS_L = row['Distance to Streams Level']
    DS_FRL = row['Distance to Streams Flood Risk Level']
    #CN_L = row['Curve Number Level']
    #CN_FRL = row['Curve Number Flood Risk Level']
    TP_L = row['Total Precipitation Level']
    TP_FRL = row['Total Precipitation Flood Risk Level']
    EP_L = row['Effective Precipitation Level']
    EP_FRL = row['Effective Precipitation Flood Risk Level']
    #Floodplain = row['Floodplain']
    #FP_FRL = row['Floodplain Flood Risk Level']
    total_flood_risk_level = row['Level']

    # Fill in prompt with PII
    prompt = prompt_template.format(Slope_Level=Slope_Level,
                                    Slope_Flood_Risk_Level=Slope_Flood_Risk_Level,
                                    HAND_L=HAND_L,
                                    HAND_FRL=HAND_FRL,
                                    DS_L=DS_L,
                                    DS_FRL=DS_FRL,
                                    TP_L=TP_L,
                                    TP_FRL=TP_FRL,
                                    EP_L=EP_L,
                                    EP_FRL=EP_FRL,
                                    total_flood_risk_level=total_flood_risk_level
                                   )
    return prompt

prompt = generate_on_user_info(row=df.loc[1])

st.write("Prompt is:\n", prompt)
