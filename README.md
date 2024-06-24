# Chat.AI 👋

Welcome to Chat.AI! A conversational AI chatbot built using Azure OpenAI API `text-embedding-ada-002` and `gpt-35-turbo-16k` for chat completions

## AI Techniques 

### Natural Language Processing (NLP)

**Text Embeddings** : Utilizing OpenAI's text-embedding-ada-002 model to transform text into high-dimensional vectors that represent semantic meaning

**Conversational AI**: Implementing dialogue management using OpenAI's gpt-35-turbo-16k model for generating human-like responses based on the context of the conversation

### Retrieval-Augmented Generation (RAG)

**Vector Search Index**: Using Azure Cosmos DB for MongoDB with a Vector Search Index to enhance the chatbot's ability to retrieve relevant information efficiently

## Frontend 

### Frameworks and Libraries

#### HTML/CSS, JavaScript, DOM Manipulation


`Fetch API` : Used to make HTTP POST requests to a server

`Date API` : Used to generate a unique timestamp for unique session key

`Crypto API` : Used to generate random values for creating a unique session key

`URL API` : Used to validate URL strings


## Backend 

### Frameworks and Libraries

`FastAPI`: Used for building the API endpoints, providing features like data validation and automatic API documentation in `Swagger`

`langchain` : Used to manage the interaction with the Azure OpenAI API

`pydantic`: Utilized to deserealize data including JSON data with multiple object structures
![image](https://github.com/TheNaila/openai_azure_chatbot/assets/63077056/20f39bba-7fbd-477c-92c3-070614b70f4a)
![image](https://github.com/TheNaila/openai_azure_chatbot/assets/63077056/02b84504-4d9d-485b-95d8-3476bbbd5e98)

`asyncio` and `httpx` : To leverage async, await and lock for performing non-blocking operations

`httpx` : Used to create a proxy server for server-to-server requests for smooth communication between frontend and backend

`pytest` : For writing unit tests to ensure code quality 

`Uvicorn`: An ASGI server used to run the FastAPI application



https://github.com/TheNaila/azure_openai/assets/63077056/ebb1439e-aba8-4efc-9da8-2727cba992fa


https://github.com/TheNaila/azure_openai/assets/63077056/b89b88e9-46aa-481b-8b60-7ea116fba424







