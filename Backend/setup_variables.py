import json

env_file = []

with open('env.json', 'r') as f:
    env_file = json.load(f)

azure_endpoint_val = env_file["AOAI_ENDPOINT"]
api_key_val = env_file["AOAI_KEY"]
api_version_val = env_file["API_VERSION"]
connection_string = env_file["CONNECTION_STRING"]