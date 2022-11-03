#!/usr/bin/env python
# coding: utf-8

# # Visual Analytics Eindopdracht Crimes NY

# Studenten: Sophie Frerix en Merel van Zanten
# 
# Datum: 03-11-2022

# # Ophalen Data

# Dataset gevonden door zoeken naar ny in deze link: https://osf.io/zyaqn/wiki/1.%20Data%20sources/
# 
# Dataset van website: https://data.cityofnewyork.us/Public-Safety/NYPD-Complaint-Data-Historic/qgea-i56i

# In[59]:


# Importeren van packages die gebruikt kunnen worden
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import folium
import streamlit as st
from streamlit_folium import folium_static
#!pip list


# In[2]:


#!pip install streamlit


# In[60]:


# Dataset inladen als geojson
gdf_crime = pd.read_csv("https://data.cityofnewyork.us/resource/qgea-i56i.csv")
gdf_crime.head()


# ## Data cleaning

# Het verwijderen van onnodige kolommen en het bekijken van kolomwaardes

# In[61]:


gdf_crime.info()


# In[5]:


gdf_crime.isnull().sum()


# In[6]:


gdf_crime.isnull().head()


# In[7]:


gdf_crime.columns


# In[8]:


gdf_crime["parks_nm"].unique()


# In[9]:


gdf_crime["jurisdiction_code"].unique()


# In[10]:


gdf_crime["juris_desc"].unique()


# Enkele kolomnamen uitgeschreven
# 
# addr_pct-cd = The precinct in which the incident occurred
# 
# rpt_dt = date event was reported to police
# 
# pd_desc = Description of internal classification corresponding with PD code (more granular than Offense Description)
# 
# crm_atpt_cptd_cs = Indicator of whether crime was successfully completed or attempted, but failed or was interrupted prematurely
# 
# law_cat_cd = Level of offense: felony, misdemeanor, violation
# 
# boro_nm = the name of the borough (stadsdeel) in which the incident occured
# 
# loc_of_occur_desc = Specific location of occurrence in or around the premises; inside, opposite of, front of, rear of
# 
# perm_typ_desc = Specific description of premises; grocery store, residence, street, etc.
# 
# juris_desc = Description of the jurisdiction code
# 
# susp_age_group = suspect's age group

# In[11]:


gdf_crime["susp_age_group"].unique()


# In[12]:


gdf_crime["law_cat_cd"].unique()


# In[13]:


gdf_crime = gdf_crime.drop(["lat_lon_zip", "lat_lon_city", "lat_lon_address", "lat_lon_state", "housing_psa"], axis = 1)


# In[14]:


gdf_crime.head()


# In[15]:


# Toevoegen voor een jaar kolom van de datum van aangifte
gdf_crime["year"] = pd.to_datetime(gdf_crime["rpt_dt"]).dt.year


# # Maken visualisaties

# Voor het maken van de dashboard moet een histogram, boxplot en een scatterplot met trendlijn (regressiemodel) gemaakt worden.

# ## Histogrammen

# In[16]:


# Histogram van de codes van de misdaad per zwaarte van de misdaad
law_cat_cd_color_map = ["orange", "red", "purple"]

fig = px.histogram(gdf_crime, x = "pd_cd", color =  "law_cat_cd", 
                   color_discrete_sequence = law_cat_cd_color_map,
                   title = "Aantal keer dat een interne classificatie code voorkomt per 'level of offence'", labels = {
                       "pd_cd": "Three digit internal classification code",
                       "law_cat_cd": "Level of Offence"})

fig.update_layout({'yaxis': {'title':{'text': 'Aantal'}}})
fig.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig)


# In[17]:


#histogram level of offence per patrouille
fig1 = px.histogram(gdf_crime, x = "patrol_boro", color =  "law_cat_cd", 
                   color_discrete_sequence = law_cat_cd_color_map,
                   title = "Aantal keer een 'level of offence' voorkomt per patrouille ronde", labels = {
                       "patrol_boro": "Patrouille ronde", "law_cat_cd": "Level of Offence"})
fig1.update_layout({'yaxis': {'title':{'text': 'Aantal'}}})
fig1.show()


# Voor het weergeven in streamlit
st.plotly_chart(fig1)


# In[18]:


#histogram aantal delicten vs buurten vs sexes
# Veranderen van de onbekende geslachten (D en E) naar Divers
gdf_crime['vic_sex'] = gdf_crime['vic_sex'].replace(['D', 'E','F', 'M'], ['Divers', 'Divers', 'Female', 'Male'])


# Aanmaken plot (fig2)
fig2 = make_subplots(rows = 3, cols =1, shared_xaxes =True)
colors = ["00FFFF", "#0000EE", "#8A2BE2"]
row_num = 1
Vic_sex = ["Female", "Male", "Divers"]

#For loop om het geslacht apart te krijgen
for vic_sex in Vic_sex:
    df_crime = gdf_crime[gdf_crime["vic_sex"] == vic_sex]
    fig2.add_trace(go.Histogram(x = df_crime["boro_nm"], name = vic_sex),
                   row = row_num, col = 1)
    row_num += 1

# Updaten van de layout van fig8
fig2.update_layout(title = "Slachtofferaantal per buurt en per geslacht", legend_title_text = "Geslachten")
fig2.update_yaxes(title_text = "Aantal delicten")


fig2.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig2)


# ## Boxplot

# In[19]:


# Boxplot van geslacht per (interne) misdrijf classificatie code
fig3 = px.box(gdf_crime, x = "susp_sex", y = "pd_cd", title = "Leefdtijdsinformatie per geslacht verdachten", labels = {
             "susp_sex": "Geslacht van verdachten",
            "pd_cd": "(Interne) misdrijf classificatie code"})
fig3.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig3)


# In[20]:


# Het aanmaken van een kolom met de datum en tijd van het begin van de klacht
gdf_crime["date_time"] = pd.to_datetime(gdf_crime["cmplnt_fr_dt"].astype("str") + " " + gdf_crime["cmplnt_fr_tm"])


# In[21]:


# Voorbereiding voor het maken van een boxplot met datums
crime = gdf_crime.set_index("date_time")
crime.head()


# In[22]:


# Aanmaken van een boxplot over het geslacht en wanneer ze misdrijven hebben gepleegd.
color_map1 = ['mediumvioletred']

fig4 = px.box(crime, x = "susp_sex", y = "cmplnt_fr_dt",
              color_discrete_sequence=color_map1,
              title = "Tijd van gepleegde delicten per geslacht verdachten", 
              labels = {"susp_sex": "Geslacht van verdachten", "cmplnt_fr_dt": "Datum van gepleegde delict"})
fig4.show()


# In[23]:


# Het verwijderen van de outliers van de boxplot (fig3)
gdf_crime.drop(gdf_crime[gdf_crime["year"] < 2017].index, inplace = True)
gdf_crime["year"].unique()


# In[24]:


# Nog meer verwijder
gdf_crime["fr_year"] = gdf_crime["cmplnt_fr_dt"].dt.year
gdf_crime.drop(gdf_crime[gdf_crime["fr_year"] < 2018].index, inplace = True)
gdf_crime.drop(gdf_crime[gdf_crime['year'] < 2018].index, inplace = True)
gdf_crime["fr_year"].unique()


# In[25]:


# "date_time" kolom als index zetten voor het plotten van een boxplot met datum
gdf_crime = gdf_crime.reset_index()
gdf_crime = gdf_crime.set_index("date_time")
gdf_crime.sort_values("cmplnt_fr_dt")


# In[26]:


# Toevoegen van een maand colom
gdf_crime["fr_month"] = gdf_crime["cmplnt_fr_dt"].dt.month
gdf_crime.sort_values("fr_month")


# In[27]:


# Aanmaken van een boxplot over het geslacht en wanneer ze misdrijven hebben gepleegd.
fig5 = px.box(gdf_crime, x = "susp_sex", y = "cmplnt_fr_dt", notched=True,
              title = "Datum van gepleegde delicten per geslacht verdachten", 
              labels = {"susp_sex": "Geslacht van verdachten",
            "cmplnt_fr_dt": "Datum van gepleegde delict"})

fig5.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig5)


# ## Lijndiagram met tweepunt slider

# In[28]:


#aantal crimes per maand gesorteerd
gdf_crime["month"]= gdf_crime["rpt_dt"].dt.month
gdf_crime.head()

aantal_crimes_maand = gdf_crime.groupby(['month'])
aantal_crimes_maand = pd.DataFrame(aantal_crimes_maand['rpt_dt'].count())
print(aantal_crimes_maand)
aantal_crimes_maand = aantal_crimes_maand.reset_index()

#veranderen van nummerieke getallen van maand naar letters
aantal_crimes_maand["month_alpha"] = aantal_crimes_maand["month"]
aantal_crimes_maand['month_alpha'] = aantal_crimes_maand['month_alpha'].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ], 
                                                      ['januari', 'februari', 'maart', 'april', 'mei', 
                                                       'juni', 'juli', 'augustus', 'september', 'oktober', 
                                                       'november', 'december'])

aantal_crimes_maandA = aantal_crimes_maand
aantal_crimes_maandA


# In[29]:


# Aanmaken van een lijndiagram van aantal crimes per maand met een "twee slider"
fig6 = px.line(aantal_crimes_maandA, x = "month_alpha", y = "rpt_dt",
              title= "Aantal delicten in New York per maand", labels = {"month_alpha": "maand", "rpt_dt": "Aantal delicten"})

fig6.update_xaxes(rangeslider_visible=True)
fig6.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig6)


# In[30]:


##aantal crimes per dag gesorteerd
gdf_crime["month"]= gdf_crime["rpt_dt"].dt.month
gdf_crime["day"]= gdf_crime["rpt_dt"].dt.day
gdf_crime.head()

# Nieuw dataframe aanmaken voor dag en maand
aantal_crimes_dag = gdf_crime.groupby(["month", "day"])
aantal_crimes_dag = pd.DataFrame(aantal_crimes_dag["rpt_dt"].count())

aantal_crimes_dag = aantal_crimes_dag.reset_index()

#Toevoegen benamingen maand
aantal_crimes_dag["month_alpha"] = aantal_crimes_dag["month"]
aantal_crimes_dag["month_alpha"] = aantal_crimes_dag["month_alpha"].replace([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 ], 
                                                      ['januari', 'februari', 'maart', 'april', 'mei', 
                                                       'juni', 'juli', 'augustus', 'september', 'oktober', 
                                                       'november', 'december'])
aantal_crimes_dag.head()


# In[31]:


# Plotten aantal crimes per maand
fig7 = px.line(aantal_crimes_dag, x= "day", y = "rpt_dt", color = "month_alpha",
              title= "Aantal delicten in New York per dag van de maand")
fig7.update_xaxes(rangeslider_visible=True)
fig7.update_layout({'xaxis': {'title': {'text': 'Dagen'}},
                   'yaxis': {'title':{'text': 'Aantal delicten'}},
                   'legend': {'title':{'text': 'Maanden'}}})
fig7.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig7)


# ## Staafdiagram

# In[32]:


#barplot crimes per dag van de week
gdf_crime['Delict'] = pd.to_datetime(gdf_crime['rpt_dt'])
gdf_crime['day_of_week'] = gdf_crime['Delict'].dt.day_of_week
gdf_crime.head()


aantal_crimes_weekdag = gdf_crime.groupby(['day_of_week'])
aantal_crimes_weekdag = pd.DataFrame(aantal_crimes_weekdag['Delict'].count())
aantal_crimes_weekdag = aantal_crimes_weekdag.reset_index('day_of_week')
print(aantal_crimes_weekdag)


aantal_crimes_weekdag["day_of_week_alpha"] = aantal_crimes_weekdag['day_of_week']
aantal_crimes_weekdag['day_of_week_alpha'] = aantal_crimes_weekdag['day_of_week_alpha'].replace([0, 1, 2, 3, 4, 5, 6],['maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag'])
print(aantal_crimes_weekdag)

color_map=["mediumvioletred"]

fig8 = px.histogram(aantal_crimes_weekdag, x = "day_of_week_alpha", y = "Delict",
             title='Aantal delicten per dag van de week',  color_discrete_sequence=color_map)
fig8.update_layout({'xaxis': {'title': {'text': 'Dag van de week'}},
                   'yaxis': {'title':{'text': 'Aantal delicten'}}}, showlegend=False)   


fig8.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig8)


# In[33]:


color_map2 = ['mediumturquoise']
fig9 = px.histogram(gdf_crime, x = "boro_nm",
             title='Aantal delicten per buurt in New York',  color_discrete_sequence=color_map2)
fig9.update_layout({'xaxis': {'title': {'text': 'Buurt'}},
                   'yaxis': {'title':{'text': 'Aantal delicten'}}}, showlegend=False) 

# Voor het weergeven in streamlit
st.plotly_chart(fig9)


# In[34]:


fig10 = go.Figure()


for boro_nm in ['MANHATTAN', 'BRONX', 'BROOKLYN', 'QUEENS', 'STATEN ISLAND']:    
    GDF_Boro = gdf_crime[gdf_crime.boro_nm == boro_nm]    
    fig10.add_trace(go.Histogram(x = GDF_Boro["law_cat_cd"], name=boro_nm))

dropdown_buttons = [
    {'label': 'TOTAL', 'method':'update', 'args': [{'visible': [True, True, True, True,True]},{'title': 'All'}]},
    {'label': 'MANHATTAN', 'method':'update', 'args': [{'visible': [True, False, False, False, False]},{'title': 'MANHATTAN'}]},
    {'label': 'BRONX', 'method':'update', 'args': [{'visible': [False, True, False, False, False]},{'title': 'BRONX'}]},
    {'label': 'BROOKLYN', 'method':'update', 'args': [{'visible': [False, False, True, False, False]},{'title': 'BROOKLYN'}]},
    {'label': 'QUEENS', 'method':'update', 'args': [{'visible': [False, False, False, True, False]},{'title': 'QUEENS'}]},
    {'label': 'STATEN ISLAND', 'method':'update', 'args': [{'visible': [False, False, False, False, True]},{'title': 'STATEN ISLAND'}]},
]



# Update the figure to add dropdown menu
fig10.update_layout(
    {'updatemenus': [
    {'active': 0, 'buttons': dropdown_buttons}
    ]})

fig10.update_layout(bargap = 0.2)
fig10.update_layout({'xaxis': {'title': {'text': 'Soort delict'}},
                  'title': {'text': 'Soort delict per buurt in New York City'}})

# Voor het weergeven in streamlit
#st.plotly_chart(fig10)


# ## Cirkeldiagram

# In[35]:


#nieuwe tabel aantal slachtoffers per ras voor piechart
Table= {
    'ras' :["White","Unknown", "White Hispanic", "Black", "Asian/Pacific Islander", "Black Hispanic", "American Indian"],
    'aantal_ras':[165, 310, 171, 237, 66, 32, 7],
  
          }
test = pd.DataFrame(Table)
print(test)


# In[36]:


#piechart slachtoffers per ras
fig11 = px.pie(test, values='aantal_ras', names='ras', title="Circkeldiagram met rassen van slachtoffers", 
             color_discrete_sequence=px.colors.qualitative.Safe)
fig11.update_layout({'xaxis': {'title': {'text': 'Maand'}}, 
                   'yaxis': {'title':{'text': 'Aantal vliegtuigongelukken'}},
                   'legend': {'title':{'text': 'Rassen'}}})

fig11.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig11) 


# # Hulpbron opschoning dataset

# In[37]:


# Ophalen en eerste 5 rijen weergeven van de hulpbron dataset
df_residents = pd.read_csv("https://data.cityofnewyork.us/resource/5r5y-pvs3.csv")
df_residents.head()


# In[38]:


df_residents.columns


# In[39]:


# Droppen van onnodige kolommen uit de hulpbron dataset
df_residents = df_residents.drop(["statecity_section8_flag", "all_average_gross_rent", 
                                  "total_female_headed_hoh_62_years_and_over", "total_male_headed_hoh_62_years_and_over",
                                  "total_hoh_62_years_and_over", "total_hoh_62_years_and_over_as_percent_of_families",
                                  "total_single_parent_grandparent_families_with_minors",
                                  "total_families_on_welfare_and_hoh_elderly", 
                                  "total_male_headed_single_parent_grandparent_with_minors",
                                  "total_single_parent_grandparent_families_on_welfare",
                                  "total_female_headed_single_parent_grandparent_with_minors", 
                                  "total_single_parent_grandparent_with_minors_as_of_families"], axis = 1)
df_residents.head()


# In[40]:


df_residents.columns


# ## Werken met hulpdataset

# In[41]:


# Totaal aantal families van new york berekenen
total_families_ny = df_residents["total_families"].sum()
print(total_families_ny)


# In[42]:


df_residents["program"].unique()


# In[43]:


residents = df_residents.groupby("program").sum("total_families")
residents = residents.reset_index()
#residents = residents.drop(residents[residents["program"] == "ALL PROGRAMS"])
residents = residents[~ residents["program"].str.contains("ALL PROGRAMS")]
residents


# In[44]:


fig12 = go.Figure()

fig12.add_trace(go.Box(name = "Totale populatie", y= residents["total_population"]))
fig12.add_trace(go.Box(name = "Totaal aantal families", y= residents["total_families"]))
fig12.update_layout(title = "Totaal aantal mensen in New York")
fig12.update_yaxes(title_text = "Aantal mensen")
fig12.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig12)


# In[45]:


# Totale populatie van new york berekenen
total_population_ny = df_residents["total_population"].sum()
print(total_population_ny)


# In[46]:


#Berekenen percentage verdachten van totale bevolking
tot_bev = gdf_crime.groupby("susp_sex")
tot_bev = pd.DataFrame(tot_bev['rpt_dt'].count())

tot_bev["%_susp"] = tot_bev["rpt_dt"]/total_population_ny*100
tot_bev = tot_bev.reset_index()
tot_bev


# In[47]:


#piechart slachtoffers per ras
fig13 = px.pie(tot_bev, values='rpt_dt', names='susp_sex', title="Cirkeldiagram met het aantal delicten gepleegd per geslacht")

# Update hoverdata

fig13.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig13) 


# ## Scatterplot

# In[48]:


# Aanmaken van de plot (fig8)
fig14 = make_subplots(rows = 3, cols =1, shared_xaxes =True, shared_yaxes=True)
row_num = 1
law_cat_cd = ["MISDEMEANOR", "FELONY", "VIOLATION"]

for misdrijf in law_cat_cd:
    df_crime = gdf_crime[gdf_crime["law_cat_cd"] == misdrijf]
    fig14.add_trace(go.Scatter(x = df_crime["rpt_dt"], y = gdf_crime["pd_cd"], mode = "markers",name = misdrijf),
                   row = row_num, col = 1)
    row_num += 1

fig14.update_layout(title = "Internal classification code per datum van aangifte weergegeven permisdrijf(zwaarte)", 
                   legend_title_text = "Misdrijven")
fig14.update_xaxes(title_text = "Datum van aangifte")
fig14.update_yaxes(title_text = "Internal calssification code")  
fig14.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig14)


# In[49]:


# Aanmaken scatterplot over complained datum en geraporteerde datum
fig15 = px.scatter(gdf_crime, x = "rpt_dt", y = "cmplnt_fr_dt")

fig15.update_layout(title = "Datum van klacht tegen de daten van aangifte")
fig15.update_xaxes(title_text = "Datum van aangifte")
fig15.update_yaxes(title_text = "Datum van klacht")  

fig15.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig15)


# # Toevoegen van een kaart

# In[50]:


# Functie door docent gevonden op het internet voor het toevoegen van een categorische legenda (Visual Analytic opdarcht 3):
# (bron: https://stackoverflow.com/questions/65042654/how-to-add-categorical-legend-to-python-folium-map)

def add_categorical_legend(folium_map, title, colors, labels):
    if len(colors) != len(labels):
        raise ValueError("colors and labels must have the same length.")

    color_by_label = dict(zip(labels, colors))
    
    legend_categories = ""     
    for label, color in color_by_label.items():
        legend_categories += f"<li><span style='background:{color}'></span>{label}</li>"
        
    legend_html = f"""
    <div id='maplegend' class='maplegend'>
      <div class='legend-title'>{title}</div>
      <div class='legend-scale'>
        <ul class='legend-labels'>
        {legend_categories}
        </ul>
      </div>
    </div>
    """
    script = f"""
        <script type="text/javascript">
        var oneTimeExecution = (function() {{
                    var executed = false;
                    return function() {{
                        if (!executed) {{
                             var checkExist = setInterval(function() {{
                                       if ((document.getElementsByClassName('leaflet-top leaflet-right').length) || (!executed)) {{
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.display = "flex"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].style.flexDirection = "column"
                                          document.getElementsByClassName('leaflet-top leaflet-right')[0].innerHTML += `{legend_html}`;
                                          clearInterval(checkExist);
                                          executed = true;
                                       }}
                                    }}, 100);
                        }}
                    }};
                }})();
        oneTimeExecution()
        </script>
      """
   

    css = """

    <style type='text/css'>
      .maplegend {
        z-index:9999;
        float:right;
        background-color: rgba(255, 255, 255, 1);
        border-radius: 5px;
        border: 2px solid #bbb;
        padding: 10px;
        font-size:12px;
        positon: relative;
      }
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 0px solid #ccc;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    """

    folium_map.get_root().header.add_child(folium.Element(script + css))

    return folium_map


# In[57]:


# New York: latitude = 40.730610 , longitude = -73.935242, van https://www.latlong.net/place/new-york-city-ny-usa-1848.html
m1 = folium.Map(location = [40.730610, -73.935242], zoom_start = 12, tiles = "openstreetmap")
folium.TileLayer("cartodbpositron").add_to(m1)

# Definieren kleur
def color_producer(law_cat_cd):
   if law_cat_cd == "MISDEMEANOR": 
    return "yellow"
   elif law_cat_cd == "FELONY": 
    return "red"
   elif law_cat_cd == "VIOLATION": 
    return "navy"


# Aanmaken van circkelmarkers in de folium kaart
for x in range(0, len(gdf_crime)):
     folium.CircleMarker(
         fill = True,
         fill_color = color_producer(gdf_crime.iloc[x]["law_cat_cd"]),
         #radius = gdf_crime.iloc[x]["law_cat_cd"],
         color = color_producer(gdf_crime.iloc[x]["law_cat_cd"]),
         location= [gdf_crime.iloc[x]["latitude"], gdf_crime.iloc[x]["longitude"]],
         popup= gdf_crime.iloc[x][["juris_desc", "susp_race"]],
    ).add_to(m1)



folium.LayerControl(position='bottomleft', collapsed=False).add_to(m1)

# Toevoegen legenda
m1 = add_categorical_legend(m1, "Legenda",
                             colors = ["red", "yellow", "navy"],
                           labels = ["Zware misdaad", "Misdrijf", "Overtreding"])
folium_static(m1)


# Map van verdachte sexuele oriëntatie

# In[58]:


# New York: latitude = 40.730610 , longitude = -73.935242, van https://www.latlong.net/place/new-york-city-ny-usa-1848.html
m2 = folium.Map(location = [40.730610, -73.935242], zoom_start = 10.5, tiles = "openstreetmap")

folium.TileLayer("cartodbpositron").add_to(m2)

# Definieren kleur
def color_producers(susp_sex):
    if susp_sex == "F": 
        return "deeppink"
    elif susp_sex == "M": 
        return "deepskyblue"
    elif susp_sex == "U": 
        return "darkviolet"
    elif susp_sex == "None": 
        return "darkslategray"


# Aanmaken van circkelmarkers in de folium kaart
for x in range(0, len(gdf_crime)):
    folium.CircleMarker(
        fill = True,
        fill_color = color_producers(gdf_crime.iloc[x]["susp_sex"]),
        color = color_producers(gdf_crime.iloc[x]["susp_sex"]),
        location= [gdf_crime.iloc[x]["latitude"], gdf_crime.iloc[x]["longitude"]],
        popup= gdf_crime.iloc[x][["susp_race", "susp_age_group"]],
    ).add_to(m2)

folium.LayerControl(position='bottomleft').add_to(m2)

# Toevoegen legenda
m2 = add_categorical_legend(m2, "Legenda",
                            colors = ["deeppink", "deepskyblue", "darkviolet", "darkslategray"],
                            labels = ["Vrouw", "Man", "Overig", "None"])
folium_static(m2)


# # Regressie model

# In[53]:


#!pip install statsmodels


# In[54]:


# Outliers verwijderen voor een duidelijkere scatterplot
resident = df_residents.drop(df_residents[df_residents["total_population"] >= 200000].index)
resident = resident.reset_index()


# In[55]:


fig16 = px.scatter(resident, x = "total_population", y = "total_minors_under_18", trendline = "ols")

fig16.update_layout(title = "Totale populatie tegen over de totale aantal minderjarige (<18) met trendlijn")
fig16.update_xaxes(title_text = "Totale populatie van NYC")
fig16.update_yaxes(title_text = "Totaal aanta minderjarige (<18) van NYC") 

fig16.show()

# Voor het weergeven in streamlit
st.plotly_chart(fig16)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




