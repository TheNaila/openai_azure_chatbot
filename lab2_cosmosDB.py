from pymongo import MongoClient
import json, os
import requests
from pymongo import UpdateOne
from models import Product, Customer, SalesOrder
from tenacity import retry, wait_random_exponential, stop_after_attempt
from openai_client import ai_client, connection_string
from time import sleep


def connect_mongoDB(max_retries = 0):
    if max_retries == 3:
        return 
    try:
        client = MongoClient(connection_string)
    except: 
        print("couldn't connect")
        max_retries = max_retries + 1
        return connect_mongoDB(max_retries)
    return client

def create_product_collection(_client):
    db = _client["projects-development"]
    product_raw_data = "https://cosmosdbcosmicworks.blob.core.windows.net/cosmic-works-small/product.json"
    '''
    #(**var) syntax unwraps the attributes of a dictionary
    data is a dictionary with keys that match the names of the parameters in the __init__ method of the Product class that decodes the JSON object or a Pydantic model (decoder)
    '''
    product_data = [Product(**data) for data in requests.get(product_raw_data).json()]
    
    '''
    UpdateOne({"_id": prod.id}, {"$set": prod.model_dump(by_alias=True)}, upsert=True):

    UpdateOne: The UpdateOne method is used to update a single document that matches the specified filter criteria.
    {"_id": prod.id}: This is the filter criteria for the update operation
    {"$set": prod.model_dump(by_alias=True)}: It uses the $set operator to update the document with the fields provided by prod.model_dump(by_alias=True). This assumes that each prod object has a model_dump method that returns a dictionary representation of the object
    upsert=True: This option specifies that if no document matches the filter criteria (i.e., a document with the specified _id doesn't exist), a new document should be created using the filter criteria and the update document
    The bulk_write method takes a list of write operations, which can include InsertOne, UpdateOne, DeleteOne, and others
    The bulk_write method sends all the update operations to MongoDB in a single request
    
    When using Pydantic models, you can define aliases for fields. These aliases can be used, for example, to match field names with external data formats (like JSON keys) that use different naming conventions than your Python code
    

    class Product(BaseModel):
        id: int
        name: str
        price: float
        description: str = Field(alias="productDescription") ---> the alias is how the attribute is named in the data source outside of your model "productDescription" but in your code you want it names as "description"

    # Creating an instance of the Product model
    product = Product(id=1, name="Product 1", price=100.0, productDescription="First product")

    # Default behavior (by_alias=False)
    print(product.dict())
    # Output:
    # {'id': 1, 'name': 'Product 1', 'price': 100.0, 'description': 'First product'}

    # Using aliases (by_alias=True)
    print(product.dict(by_alias=True))
    # Output:
    # {'id': 1, 'name': 'Product 1', 'price': 100.0, 'productDescription': 'First product'}

    '''
    db["products"].bulk_write([UpdateOne({"_id": prod.id}, {"$set": prod.model_dump(by_alias=True)}, upsert=True) for prod in product_data])
        
    customer_sales_raw_data = "https://cosmosdbcosmicworks.blob.core.windows.net/cosmic-works-small/customer.json"
    response = requests.get(customer_sales_raw_data)
    # override decoding
    response.encoding = 'utf-8-sig'
    response_json = response.json()
    # filter where type is customer
    customers = [cust for cust in response_json if cust["type"] == "customer"]
    # filter where type is salesOrder
    sales_orders = [sales for sales in response_json if sales["type"] == "salesOrder"]
    
    customer_data = [Customer(**data) for data in customers]
    db["customers"].bulk_write([ UpdateOne({"_id": cust.id}, {"$set": cust.model_dump(by_alias=True)}, upsert=True) for cust in customer_data])
   
    sales_data = [SalesOrder(**data) for data in sales_orders]
    db["sales"].bulk_write([ UpdateOne({"_id": sale.id}, {"$set": sale.model_dump(by_alias=True)}, upsert=True) for sale in sales_data])

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def generate_embeddings(text: str):
    '''
    Generate embeddings from string of text using the deployed Azure OpenAI API embeddings model.
    This will be used to vectorize document data and incoming user messages for a similarity search with
    the vector index.
    '''
    response = ai_client.embeddings.create(input=text, model="text-embedding-ada-002")
    embeddings = response.data[0].embedding
    sleep(0.5) # rest period to avoid rate limiting on AOAI
    return embeddings

def add_collection_content_vector_field(collection_name: str, db):
    '''
    Add a new field to the collection to hold the vectorized content of each document.
    '''
    documents_vector_dict = {}
    dict_obj = {}

    json_file_name = collection_name + "_collection_w_vectors.json"
    if os.path.exists(json_file_name):
        with open(json_file_name, 'r') as file:
            dict_obj = json.load(file)

    collection = db[collection_name]
    bulk_operations = []
    documents = list(collection.find({}))

    for doc in documents:

    # remove any previous contentVector embeddings
    #TODO: Explicitely handle updating docs and doc vectors

        if "contentVector" in doc:
            del doc["contentVector"]

        if len(dict_obj) != 0:
            content_vector = dict_obj[doc["_id"]]
        else:
            content = json.dumps(doc)
            content_vector = generate_embeddings(content)     
            documents_vector_dict[doc["_id"]] = content_vector

        bulk_operations.append(UpdateOne(
            {"_id": doc["_id"]},
            {"$set": {"contentVector": content_vector}},
            upsert=True
        ))

    collection.bulk_write(bulk_operations)
    if not os.path.exists(json_file_name):
        with open(json_file_name, 'w') as json_file:
            json.dump(documents_vector_dict, json_file, indent=4)

def vector_search(collection_name, query, num_results=3):
    """
    Perform a vector search on the specified collection by vectorizing
    the query and searching the vector index for the most similar documents.

    returns a list of the top num_results most similar documents
    """
    collection = db[collection_name]
    query_embedding = generate_embeddings(query)    
    pipeline = [
        {
            '$search': {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "path": "contentVector",
                    "k": num_results
                },
                "returnStoredSource": True }},
        {'$project': { 'similarityScore': { '$meta': 'searchScore' }, 'document' : '$$ROOT' } }
    ]
    results = collection.aggregate(pipeline)
    return results

def print_product_search_result(result):
    '''
    Print the search result document in a readable format
    '''
    print(f"Similarity Score: {result['similarityScore']}")  
    print(f"Name: {result['document']['name']}")   
    print(f"Category: {result['document']['categoryName']}")
    print(f"SKU: {result['document']['categoryName']}")
    print(f"_id: {result['document']['_id']}\n")


# A system prompt describes the responsibilities, instructions, and persona of the AI.
system_prompt = """
You are a helpful, fun and friendly sales assistant for Cosmic Works, a bicycle and bicycle accessories store. 
Your name is Cosmo.
You are designed to answer questions about the products that Cosmic Works sells.

Only answer questions related to the information provided in the list of products below that are represented
in JSON format.

If you are asked a question that is not in the list, respond with "I don't know."

List of products:
"""


def rag_with_vector_search(question: str, num_results: int = 3):
    """
    Use the RAG model to generate a prompt using vector search results based on the
    incoming question.  
    """
    # perform the vector search and build product list
    results = vector_search("products", question, num_results=num_results)
    product_list = ""
    for result in results:
        if "contentVector" in result["document"]:
            del result["document"]["contentVector"]
        product_list += json.dumps(result["document"], indent=4, default=str) + "\n\n"

    # generate prompt for the LLM with vector results
    formatted_prompt = system_prompt + product_list

    # prepare the LLM request
    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": question}
    ]

    completion = ai_client.chat.completions.create(messages=messages, model="gpt-35-turbo-16k")
    return completion.choices[0].message.content


client = connect_mongoDB()
create_product_collection(client)
db = client["projects-development"]
add_collection_content_vector_field("products", db)
add_collection_content_vector_field("customers", db)
add_collection_content_vector_field("sales", db)


# Create the products vector index
#TODO: Better understand
db.command({
  'createIndexes': 'products',
  'indexes': [
    {
      'name': 'VectorSearchIndex',
      'key': {
        "contentVector": "cosmosSearch"
      },
      'cosmosSearchOptions': {
        'kind': 'vector-ivf',
        'numLists': 1,
        'similarity': 'COS',
        'dimensions': 1536
      }
    }
  ]
})

# Create the customers vector index
db.command({
  'createIndexes': 'customers',
  'indexes': [
    {
      'name': 'VectorSearchIndex',
      'key': {
        "contentVector": "cosmosSearch"
      },
      'cosmosSearchOptions': {
        'kind': 'vector-ivf',
        'numLists': 1,
        'similarity': 'COS',
        'dimensions': 1536
      }
    }
  ]
})

# Create the sales vector index
db.command({
  'createIndexes': 'sales',
  'indexes': [
    {
      'name': 'VectorSearchIndex',
      'key': {
        "contentVector": "cosmosSearch"
      },
      'cosmosSearchOptions': {
        'kind': 'vector-ivf',
        'numLists': 1,
        'similarity': 'COS',
        'dimensions': 1536
      }
    }
  ]
})

query = "What bikes do you have?"
results = vector_search("products", query, num_results=4)
for result in results:
    print_product_search_result(result)   

print(rag_with_vector_search("What bikes do you have?", 5))

