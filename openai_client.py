import os
import json
from openai import AzureOpenAI

env_file = []
with open('env.json', 'r') as f:
    env_file = json.load(f)

azure_endpoint_val = env_file["AOAI_ENDPOINT"], 
api_key_val = env_file["AOAI_KEY"],  
api_version_val = env_file["API_VERSION"]
connection_string = env_file["CONNECTION_STRING"]

ai_client = AzureOpenAI(
  azure_endpoint = azure_endpoint_val, 
  api_key = api_key_val,  
  api_version = api_version_val
)

'''
#Test with chatCompletion endpoint 

chatResponse = ai_client.chat.completions.create(
    model="gpt-35-turbo-16k",
    messages=[
        {"role": "system", "content": "You are a helpful, fun and friendly sales assistant for Cosmic Works, a bicycle and bicycle accessories store."},
        {"role": "user", "content": "Do you sell bicycles?"},
        {"role": "assistant", "content": "Yes, we do sell bicycles. What kind of bicycle are you looking for?"},
        {"role": "user", "content": "I'm not sure what I'm looking for. Could you help me decide?"}
    ]
)

print(chatResponse.choices[0].message.content)

'''


