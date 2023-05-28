import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI#, File, UploadFile
from sklearn.compose import ColumnTransformer


description = """
Welcome to our new GetAround APP
This api help you to get best price for rent your car.

Check out documentation below 👇 for more information on each endpoint. 
"""

app = FastAPI(
    title="GETAROUND PRICE API",
    description=description,
    version="0.1",
    contact={
        "name": "GET AROUND APP",
        "url": "http://localhost:4000",
    }
)

# Type avec un objet voiture et les infos nécessaires
class carInfos(BaseModel):
    model_key : str
    mileage : int
    engine_power : int
    fuel : str
    paint_color : str
    car_type : str
    private_parking_available : bool
    has_gps : bool
    has_air_conditioning : bool
    automatic_car : bool
    has_getaround_connect : bool
    has_speed_regulator : bool
    winter_tires : bool

# Type Liste d'objet voiture
class carList(BaseModel):
    inputs : List[carInfos]

#Fonction de prédiction
def predict_rent_price(car_infos : carInfos):
    #
    return 100

@app.get("/")
async def index():
    message = "Hello world! This `/` is the most simple and default endpoint. If you want to learn more, check out documentation of the api at `/docs`"
    return message

@app.post("/predict")
async def predict_price(carListsInput: carList):
    """
    EndPoint de Prédiction du prix de location d'une voiture
    """
    # Set tracking URI to your Heroku application
    mlflow.set_tracking_uri("https://getaroundmlflowserver.herokuapp.com")

    columns_list = ['model_key','mileage', 'engine_power', 'fuel', 'paint_color',
       'car_type', 'private_parking_available', 'has_gps',
       'has_air_conditioning', 'automatic_car', 'has_getaround_connect',
       'has_speed_regulator', 'winter_tires']
    dataset = pd.DataFrame(columns=columns_list)
    for car in carListsInput.inputs:
        series = pd.Series(car.dict())
        dataset = pd.concat([dataset,series.to_frame().T],ignore_index=True)
    
    #Transformation des marques en Autre
    marque_to_keep = ['Audi','BMW','Citroën','Mercedes','Mitsubishi','Nissan','Peugeot','Renault','Volkswagen']
    dataset['marque'] = dataset["model_key"].apply(lambda x : 'Autre' if x not in marque_to_keep else x)

    #Chargement du model MLFLOW
    logged_model = 'runs:/3f65d16674cd41fe96cb5ebed6729216/model'
    loaded_model = mlflow.pyfunc.load_model(logged_model)
    Y_pred = loaded_model.predict(dataset)
    return json.dumps(Y_pred.astype(int).tolist())