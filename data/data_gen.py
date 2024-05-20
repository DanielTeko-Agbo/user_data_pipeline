import requests
from pprint import pprint
import random
import polars as pl
import os
from configparser import ConfigParser
import uuid
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    format="%(asctime)s - %(levelname)s => %(message)s",
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "datagen.log"),
            mode="a",
            maxBytes=100000000,
            backupCount=5,
        )
    ],
)


config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), ".config.ini"))

# Get the url and apiKey of the reverse geocoding API
url = config["ReverseGeo"]["url"]
apiKey = config["ReverseGeo"]["apiKey"]

def get_user():
    try:
        req = requests.get("https://randomuser.me/api/")
        result = req.json()["results"][0]
    except Exception as err: 
        logging.error(f"Unable to generate randomUser: {err}")
    else:
        logging.info("Random user generated")
        return result

phonegen = lambda: f"233{random.choice(['20', '50', '24', '54', '59', '53', '27', '57'])}{random.randint(1000000, 9999999)}"

def get_location():
    file = os.path.join(os.path.dirname(__file__), "coords.csv")
    df = pl.read_csv(file)

    val = df[random.randint(0, df.shape[0])].to_dicts()[0]
    long = val.get("Longitude")
    lat = val.get("Latitude")

    params = {
        "lat": lat, 
        "lon": long,
        "apiKey": apiKey
    }

    try:
        req = requests.get(url, params=params)
        res = req.json()["features"][0]["properties"]
    except Exception as err:
        logging.error(f"Reverse Geocoding for ({lat}, {long}) failed: {err}")
    else:
        logging.info(f"Reverse Geocoding for ({lat}, {long}) passed")
        return res


try:
    user = get_user()
    phone = phonegen()
    location = get_location()

    user["phone"] = phone
    user["location"] = location
    user["id"] = str(uuid.uuid1())
except Exception as err:
    logging.error(f"User generation failed: {err}")
else: 
    logging.info(f"User details generated : {user}")
