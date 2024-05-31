
from confluent_kafka import Consumer, KafkaError, KafkaException
import json
import logging
from logging.handlers import RotatingFileHandler
import jq
import os
from pprint import pprint
import time
from configparser import ConfigParser
from pymongo import MongoClient, errors

logging.basicConfig(
    format="%(asctime)s - %(levelname)s => %(message)s",
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            filename=os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "consumer.log"),
            mode="a",
            maxBytes=100000000,
            backupCount=5,
        )
    ],
)

# Setting up the config object
config = ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), ".config.ini"))
conn = config['mongo']

#Setting up a mongo connection object.
mongo = MongoClient(f"mongodb://{conn['user']}:{conn['passwd']}@{conn['host']}:{conn['port']}")
db = mongo["userDetails"]
collection = db["users"]

# Setup consumer object
consumer = Consumer({
    "bootstrap.servers": "broker:29092, broker-1:29092",
    "group.id": "user_consumer_0003",
    "auto.offset.reset": "earliest"
})


consumer.subscribe(["users"])
while True:
    msg = consumer.poll(1.0)

    if not msg:
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            logging.error('%% %s [%d] reached end at offset %d\n' %(msg.topic(), msg.partition(), msg.offset()))
        elif msg.error():
            logging.error(KafkaException(msg.error()))
    else:    
        value = eval(msg.value().decode("utf8"))
            
        # jq specification to transform consumed value.
        jolt = '''
            {
                "_id": .id,
                "name": (.name.first + " " + .name.last),
                "title": .name.title,
                "gender": (if .gender == "female" then "F" else "M" end),
                "age": .dob.age,
                "dob": .dob.date,
                "email": .email,
                "phone": .phone,
                "country": .location.country,
                "country_code": .location.country_code,
                "image": .picture.thumbnail,
                "location": {
                    "region": .location.state,
                    "city": .location.city,
                    "district": .location.county,
                    "town": .location.town,
                    "suburb": .location.suburb,
                    "street": .location.street,
                    "postcode": .location.postcode,
                    "housenumber": .location.housenumber,
                    "coordinates": {
                        "longitude": .location.lon,
                        "latitude": .location.lat
                    },
                },
                "timezone": {
                    "name": .location.timezone.name,
                    "abbreviation_DST": .location.timezone.abbreviation_DST,
                    "offset_DST": .location.timezone.offset_DST
                },
                "created_at": now | strftime("%B %d, %Y %H:%M:%S")
            }
            '''
        # Transform incoming json
        obj = jq.compile(jolt).input_value(value).first()
        
        # Get address from the location details while ignoring null values.
        address_ = [obj["location"][value] for value in ["housenumber", "street", "suburb", "town", "city", "district", "region"] if obj["location"][value] is not None]
        
        # Handle cases where there are a lot of nulls.
        if len(address_) >= 3:
            address = "{} {}, {}".format(address_[0], address_[1], ", ".join(address_[2:]))
        address = ", ".join(address_)
        obj["address"] = address

        
        try:
            collection.insert_one(obj)
            logging.info(f"Successfully inserted into DB: {obj}")
        except Exception as e:
            logging.error(f"DB insert failed with error: {e}")        
        