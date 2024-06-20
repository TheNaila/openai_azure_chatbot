from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from setup_variables import api_key_val, api_version_val, azure_endpoint_val, connection_string
from tenacity import retry, wait_random_exponential, stop_after_attempt
import json, time, os
from pymongo import UpdateOne
from langchain_community.vectorstores import AzureCosmosDBVectorSearch 
import asyncio


class CreateModels():
    def __init__(self):
        self.embedding_model = AzureOpenAIEmbeddings(
        openai_api_version = api_version_val,
        azure_endpoint = azure_endpoint_val,
        openai_api_key = api_key_val,   
        azure_deployment = "text-embedding-ada-002",
        chunk_size=10
        )
        self.openai_llm = AzureChatOpenAI(
        temperature = 0,
        openai_api_version = api_version_val,
        azure_endpoint =azure_endpoint_val,
        openai_api_key = api_key_val,   
        azure_deployment = "gpt-35-turbo-16k"
        )   

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def generate_embeddings(self, text: str):
        '''
        Generate embeddings from string of text using the deployed Azure OpenAI API embeddings model.
        This will be used to vectorize document data and incoming user messages for a similarity search with
        the vector index.
        '''
        response = self.embedding_model.embed_query(text)
        time.sleep(0.5) # rest period to avoid rate limiting on AOAI
        return response
    
    async def add_collection_content_vector_field(self, client, collection_name: str):
    
        documents_vector_dict = {}
        dict_obj = {}

        json_file_name = collection_name + "_collection_w_vectors.json"
        if os.path.exists(json_file_name):
            with open(json_file_name, 'r') as file:
                dict_obj = json.load(file)

        collection = client.db[collection_name]
        bulk_operations = []
        documents =  await collection.find({}).to_list(length = None)

        for doc in documents:

        # remove any previous contentVector embeddings
        #TODO: Explicitely handle updating docs and doc vectors

            if "contentVector" in doc:
                del doc["contentVector"]
                print("adding")

            if len(dict_obj) != 0:
                content_vector = dict_obj[doc["_id"]]
            else:
                content = json.dumps(doc)
                content_vector = self.generate_embeddings(content)     
                documents_vector_dict[doc["_id"]] = content_vector

            bulk_operations.append(UpdateOne(
                {"_id": doc["_id"]},
                {"$set": {"contentVector": content_vector}},
                upsert=True
            ))

        await collection.bulk_write(bulk_operations)
        if not os.path.exists(json_file_name):
            with open(json_file_name, 'w') as json_file:
                json.dump(documents_vector_dict, json_file, indent=4)
    
    async def create_vector_store_retriever(self, collection_name: str, top_k: int = 3):
        vector_store = AzureCosmosDBVectorSearch.from_connection_string(
            connection_string = connection_string,
            namespace = f"projects-development.{collection_name}",
            embedding = self.embedding_model,
            index_name = "VectorSearchIndex",    
            embedding_key = "contentVector",
            text_key = "_id"
        )
        vector_store.create_index() #use afrom_docs 
        return vector_store.as_retriever(search_kwargs={"score_threshold" : .76})