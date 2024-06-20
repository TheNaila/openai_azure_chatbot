import pytest, requests, os, json
import numpy as np
from ai_client import CreateModels
from create_db import MongoDB_Connect
from uvicorn import Config, Server
from app import app
from multiprocessing import Process
'''
Create an a class that will compute embeddings (database will be connected in app file,  will need langchain openai emebedding ), add vectors to db , and create vectorsearch with langchain class
'''
test_string = "test string for models"


def test_embeddings_success():
    ai_client = CreateModels()
    embedding = ai_client.generate_embeddings(test_string)
    # Assert that the embedding is not None
    assert embedding is not None, "Embedding is None"

    # Assert that the embedding is of type list or numpy array
    assert isinstance(embedding, (list, np.ndarray)), "Embedding is not a list or numpy array"

    # Optionally, you can check if all elements are numbers (floats or ints)
    assert all(isinstance(x, (float, int)) for x in embedding), "Embedding contains non-numeric values"

def run_server():
    config = Config(app, host="127.0.0.1", port=8000, log_level="info")
    server = Server(config)
    server.run()

@pytest.mark.asyncio
@pytest.fixture(scope="module", autouse=True)
def start_server():
    proc = Process(target=run_server)
    proc.start()
    yield  # Yield control to allow the tests to run
    proc.terminate()  # This will be executed after the tests complete
    proc.join()

def test_add_collection_to_db(start_server):

    db_client = MongoDB_Connect()
    content_file = "https://cosmosdbcosmicworks.blob.core.windows.net/cosmic-works-small/product.json"
    session_key = "1234567"
    db_client.create_collection(content_file, session_key)
    condition = session_key in db_client.db.list_collection_names()
    assert condition
    db_client.db.drop_collection(session_key)
    condition = session_key in db_client.db.list_collection_names()
    assert not condition

@pytest.mark.asyncio
async def test_generate_all_embeddings_for_collection(start_server):

    db_client = MongoDB_Connect()
    await db_client.initialize()
    session_key = "test"
    await db_client.db.drop_collection(session_key)
    test_docs = [{

        "id": "123", 
        "field1" : "test1"
    }, 
    {

        "id": "456", 
        "field1" : "test2"
    },   
    { 
        "id": "478", 
        "field1" : "test2"
    }
    ]

    for doc in test_docs:
        await db_client.db[session_key].insert_one({"_id": doc["id"]}, doc)

    ai_client = CreateModels()
    await ai_client.add_collection_content_vector_field(db_client, session_key)

    res = await db_client.db[session_key].find_one({"_id": "123"})

    assert res is not None
    await db_client.db.drop_collection(session_key)
    condition = session_key in await db_client.db.list_collection_names()
    assert not condition

    file_name = session_key + "_collection_w_vectors.json"
    if os.path.exists(file_name):
    # Delete the file
        os.remove(file_name)
    assert not os.path.exists(file_name)

def test_creating_vector_search_index(start_server):
    import json
    from langchain.schema.document import Document
    from typing import List 


    def format_docs(docs:List[Document]) -> str:
        str_docs = []
        for doc in docs:
            # Build the product document without the contentVector
            doc_dict = {"_id": doc.page_content}
            doc_dict.update(doc.metadata)
            if "contentVector" in doc_dict:  
                del doc_dict["contentVector"]
            str_docs.append(json.dumps(doc_dict, default=str))                  
        # Return a single string containing each product JSON representation
        # separated by two newlines
        return "\n\n".join(str_docs)
    db_client = MongoDB_Connect()
    session_key = "test"

    db_client.db.drop_collection(session_key)

    sample_docs = [
    {
        "_id": "123",
        "field1": "The quick brown fox jumps over the lazy dog."
    },
    {
        "_id": "456",
        "field1": "Never gonna give you up, never gonna let you down."
    }, 
     {
        "_id": "789",
        "field1": "To be or not to be, that is the question."
    }
]

    for doc in sample_docs:
        db_client.db[session_key].insert_one(doc)

    ai_client = CreateModels()
    ai_client.add_collection_content_vector_field(db_client, session_key)
    vector_store = ai_client.create_vector_store_retriever(session_key)

    query = "never gonna what?"
    results = vector_store.invoke(query)
   
    struct_res = format_docs(results)

    assert struct_res is not None
    db_client.db.drop_collection(session_key)

    file_name = session_key + "_collection_w_vectors.json"
    if os.path.exists(file_name):
    # Delete the file
        os.remove(file_name)
    assert not os.path.exists(file_name)


def test_content_file_added(start_server):

    test_request = {
        "sessionKey": "lxlvs8ye-5j2ly1u",
        "contentFile": "https://cosmosdbcosmicworks.blob.core.windows.net/cosmic-works-small/product.json",
    }
    
    response = requests.post('http://localhost:8000', json= test_request)

    print(response.content)

def test_prompt_added(start_server):
    system_prompt = """
        You are a helpful, fun and friendly sales assistant for Cosmic Works, a bicycle and bicycle accessories store.

        Your name is Cosmo.

        You are designed to answer questions about the products that Cosmic Works sells, the customers that buy them, and the sales orders that are placed by customers.

        If you don't know the answer to a question, respond with "I don't know."
        
        Only answer questions related to Cosmic Works products, customers, and sales orders.
        
        If a question is not related to Cosmic Works products, customers, or sales orders,
        respond with "I only answer questions about Cosmic Works"
    """    
    test_request = {
        "sessionKey": "lxlvs8ye-5j2ly1u",
        "systemPrompt": system_prompt, 
    }
    
    response = requests.post('http://localhost:8000', json= test_request)

    print(response.content)

def test_query_added():
    test_request = {
        "sessionKey": "lxlvs8ye-5j2ly1u",
        "query": "what bikes do you have?"
    }

    response = requests.post('http://localhost:8000', json= test_request)

    print(response.content)
    '''
    Create tools 
    Retrieve similar docs and format 
    Format prompt
    Retrieve query
    '''


'''
import pytest in file 
pytest <file_path> to run 
pytest <file_path>::<function_name> to run specific function
pytest -s <file_name> to see the output 
pytest -s <file_path>::<function_name>
pytest -vv to see the full error message 
pytest -s -vv <file_path>::<function_name>
'''