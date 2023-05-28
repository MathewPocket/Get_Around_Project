import streamlit as st
import pandas as pd
import plotly.express as px
from utils import *
import requests
import json


### CONFIG
st.set_page_config(
    page_title="Rental Price Predicter",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

### TITLE AND TEXT
st.title("📈 Rental Price Predicter")

st.divider()
st.markdown("""
### Bienvenue sur cet outil de prediction du prix de location d'une voiture
""")
            
st.divider()
st.text("Remplissez les champs et cliquez sur le bouton ADD_ROW pour ajouter la ligne")
st.text("Cliquer le bouton predict pour renseigner la derniere colonne avec les prédictions")

def predict():
    list_of_car = session_state.df.loc[ : , session_state.df.columns != 'rental_price_per_day'].to_json(orient="records")
    payload = {
    "inputs": json.loads(list_of_car)
    }
    r = requests.post("https://getaroundapiserver.herokuapp.com/predict", json=payload)
    session_state.df["rental_price_per_day"] = json.loads(json.loads(r.text))

#LoadDF
dt = pd.read_csv("https://full-stack-assets.s3.eu-west-3.amazonaws.com/Deployment/get_around_pricing_project.csv")
dt.drop(columns='Unnamed: 0',inplace=True)
dt['rental_price_per_day'] = ''
# Define column names for the empty dataframe
columns = dt.columns
# Create an empty dataframe with the defined columns
empty_df = pd.DataFrame(columns=columns)
# Create an empty session state variable
session_state = st.session_state
# Check if the session state variable is already defined
if "df" not in session_state:
    # Assign the initial data to the session state variable
    session_state.df = empty_df
    session_state.row = pd.Series(index=columns)

col1, col2, col3 = st.columns(3)
list_col = [col1, col2, col3]
i = 0
k = 0
# Create a selectbox for each column in the current row 
for col in columns[:-1]:

    with list_col[k]:
        # Get unique values from the corresponding column in the resource_data dataframe
        #We have 3 types of columns in the dataframe int64, object and boolean
        #object would become select, boolean checkbox and int64 textbox
        #Cas des objets
        if dt[col].dtype == 'O':
            #with col1:
                values = dt[col].unique().tolist()
                # Create a selectbox for the current column and add the selected value to the current row
                index = values.index(session_state.row[col]) if session_state.row[col] in values else 0
                session_state.row[col] = st.selectbox(col, values, key=col, index=index)
        elif dt[col].dtype == 'bool': 
            #with col2:
                session_state.row[col] = st.checkbox(col,key=col)
        elif dt[col].dtype == 'int64':
            #with col1:
                session_state.row[col] = st.number_input(col,key=col,min_value=0)
    
    i += 1
    if i == 3 and k < len(list_col)-1:
        k+=1
        i=0

# Add a button to add a new empty row to the dataframe and clear the values of the selectboxes for the current row
if st.button("Add Row"):
    session_state.df = pd.concat([session_state.df,session_state.row.to_frame().T],ignore_index=True)
    session_state.row = pd.Series(index=columns)

# Display the resulting dataframe
#st.dataframe(session_state.df)
session_state.df = st.experimental_data_editor(session_state.df)

#Permet de lancer la prédiction
st.button('Predict',on_click=predict)