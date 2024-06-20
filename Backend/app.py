"""
API entrypoint for backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from create_db import MongoDB_Connect
from fastapi.responses import JSONResponse
from ai_client import CreateModels
import httpx

import json 
from langchain.schema.document import Document
from typing import List
from langchain.agents import Tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain_core.messages import SystemMessage
import threading
import asyncio

lock = asyncio.Lock()
app = FastAPI()

origins = [
    "*"
]
class RequestModel(BaseModel):
    session_key: str = Field(None, alias="sessionKey")
    system_prompt: Optional[str] = Field(None, alias="systemPrompt")
    content_file: Optional[str] = Field(None, alias="contentFile")
    query: Optional[str] = None
    #TODO: think about the neccessity of queries

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_docs(docs:List[Document]) -> str:
    """
    Prepares the product list for the system prompt.
    """
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


# Agent pool keyed by session_id to retain memories/history in-memory.
# Note: the context is lost every time the service is restarted.
agent_pool = {}

@app.get("/")
def root():
    """
    Health probe endpoint.
    """
    return {"status": "ready"}

@app.post("/")
async def root(request: RequestModel):
    response_string = []

    async with lock:
        if request.session_key not in agent_pool:
            agent_pool[request.session_key] = {}
        
        agent_obj = agent_pool[request.session_key]
        response_string.append("added session key")

    async with lock:
        retriever = None
        if request.content_file != None:
            db_obj = MongoDB_Connect()
            await db_obj.initialize()
            await db_obj.delete_collection(request.session_key) #TODO: REMOVE TO DO RAG
            await db_obj.create_collection(request.content_file, request.session_key)
               #
            ai_client = CreateModels()
            await ai_client.add_collection_content_vector_field(db_obj, request.session_key)
            agent_obj["ai_client"] = ai_client 
            retriever = await ai_client.create_vector_store_retriever(request.session_key)
            retriever_chain = retriever | format_docs

            tools = [
                Tool(
                    name = "vector_search", 
                    func = retriever_chain.invoke,
                    description = "Searches Cosmic Works product information for similar products based on the question. Returns the product information in JSON format."
                )
            ]
            agent_obj["tools"] = tools
            agent_obj["content_file_added"] = "true"
            response_string.append("exiting lock")
            # return response_string

    async with lock:
        if request.system_prompt !=None:
            prompt =  SystemMessage(content = agent_obj["system_prompt_added"])
            agent_obj["system_prompt_added"] = prompt
            response_string.append("recieved prompt")
            # return response_string
        
    async with lock:
        if request.query != None:
            agent_obj["query"] = request.query
    async with lock:
        if "content_file_added" in agent_obj and "query" in agent_obj and "ai_client" in agent_obj:
            ai_client = agent_obj["ai_client"]
            tools = agent_obj["tools"]
            query = agent_obj["query"]
            prompt = None
            if "system_prompt_added" in agent_obj:
                prompt = agent_obj["system_prompt_added"]
            agent_executor = create_conversational_retrieval_agent(ai_client.openai_llm, tools, system_message = prompt, verbose=True)
            result = agent_executor({"input": query})
            return result
       
    async with lock:
        if request.query != None and not "content_file_added" in agent_obj:
            return {"status": "Please provide a file for content"}

@app.get("/proxy")
async def proxy_get(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            return JSONResponse(content=response.json(), status_code=response.status_code)
        except httpx.RequestError as exc:
            return JSONResponse(content={"error": str(exc)}, status_code=400)
