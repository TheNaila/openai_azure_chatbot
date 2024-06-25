import json
from pymongo import MongoClient, UpdateOne, DeleteMany
from pydantic import BaseModel, RootModel, create_model
import requests, uuid
from typing import Any, Dict, Type, List
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import httpx

#TODO: Can the keys not be strinf? is so use map to create a func that turns them to strings
def create_dynamic_model(name, data: Dict[str, Any]) -> Type[BaseModel]:
    return create_model(
        name,
        **{k: (type(v), ...) for k, v in data.items()}
    )

def get_model_name(index: int) -> str:
        return f"Type{index}Model"

def generate_models(collection_data):
    #find all unique objects
    unique_structures = {}
   

    if len(collection_data) > 1:
        for data in collection_data:
            set_of_keys = frozenset(data.keys())
            if set_of_keys not in unique_structures:
                unique_structures[set_of_keys] = data
    else:
        set_of_keys = frozenset(collection_data[0].keys())
        unique_structures[set_of_keys] = collection_data[0]
    models = {}
    for index, (keys, data) in enumerate(unique_structures.items()):
        model_name = get_model_name(index)
        model = create_dynamic_model(model_name, data)
        models[keys] = model
    
    return models
 
def callback_func(arg, model):
    return model(**arg)

def retrieve_model(data, models: dict):
    for keys, model in models.items():
        if keys == dict(data).keys():
            return model
        
def check_val_id(obj):
    try:
        obj.id
    except:
        # Generate a random UUID
        unique_id = uuid.uuid4()

        # Convert the UUID to a string
        unique_id_str = str(unique_id)

        obj.id = unique_id_str
    return obj

def isUrl(url):
    from urllib.parse import urlparse
    result = urlparse(url)
    if len(result.scheme) == 0:
        return False
    return True


class MongoDB_Connect():
    def __init__(self):
        self.load_env()
        self.client = None
        self.db = None

    def load_env(self):
        with open('env.json', 'r') as f:
            env_file = json.load(f)

        self.azure_endpoint_val = env_file["AOAI_ENDPOINT"]
        self.api_key_val = env_file["AOAI_KEY"]
        self.api_version_val = env_file["API_VERSION"]
        self.connection_string = env_file["CONNECTION_STRING"]
   
    async def connect_mongoDB(self, max_retries=0):
        if max_retries >= 3:
            raise ConnectionError("Max retries reached, could not connect to MongoDB")

        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client["projects-development"]
        except Exception as e:
            print(f"Connection failed: {e}")
            await asyncio.sleep(1)  # Adding a delay before retrying
            await self.connect_mongoDB(max_retries + 1)

    async def initialize(self):
        await self.connect_mongoDB()
    
    async def delete_collection(self, collection_name):
        self.db[collection_name].bulk_write([DeleteMany({})])
    
    async def create_collection(self, content_file, session_key: str):
        collection_data = None
        if isUrl(content_file):
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/proxy", params={"url": content_file})
                response.encoding = 'utf-8-sig'
                collection_data = json.loads(response.text)
        else:
            toJsonString = {
                "id" : str(uuid.uuid4()), 
                "text" : content_file
            }
            text_data = json.dumps(toJsonString)
            collection_data = json.loads(text_data)
            # #break document into smaller junks
            # line_by_line = content_file.split(".")
            # json_objs = []
            # for line in line_by_line:
            #     toJsonString = {
            #         "id" : str(uuid.uuid4()), 
            #         "text" : line
            #     }
            #     json_objs.append(toJsonString)
            # text_data = json.dumps(json_objs)
            # collection_data = json.loads(text_data)
        # collection_data = [collection_data]
        models = generate_models(collection_data)
        results = [callback_func(data, retrieve_model(data, models)) for data in collection_data]
        val_ids = [check_val_id(obj) for obj in results]
        await self.db[session_key].bulk_write([UpdateOne({"_id": obj.id}, {"$set": obj.model_dump(by_alias=True)}, upsert=True) for obj in val_ids])

    #TODO: Create function that handles if passed in files pdf or word
    
        

# obj = MongoDB_Connect()
# obj.delete_collection("products")
# obj.create_collection("https://cosmosdbcosmicworks.blob.core.windows.net/cosmic-works-small/product.json")