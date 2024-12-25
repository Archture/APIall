import os
import asyncio
import aiohttp
import google.generativeai as genai
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
CORSMiddleware,
allow_origins=[""], # Allows all origins. For more security, specify the origins you need.
allow_credentials=True,
allow_methods=[""], # Allows all methods (GET, POST, etc.)
allow_headers=["*"], # Allows all headers
)


class Message(BaseModel):
    messageOpenAi: str
    messageGemini: str
    messageX: str
    messageGrok: str
    messageMistral: str
    
    modelOpenAi: str  # New 'model' field to be sent in the JSON body
    modelGemini: str  # New 'model' field to be sent in the JSON body
    modelX: str       # New 'model' field to be sent in the JSON body
    modelGrok: str    # New 'model' field to be sent in the JSON body
    modelMistral: str # New 'model' field to be sent in the JSON body
    
    kenOpenAi: str
    kenGemini: str
    kenX: str
    kenGroq: str
    kenMistral: str
    
    sys: str = "You are a helpful assistant."

async def OpenAIf(msg: Message):
    """
    Calls Azure's OpenAI endpoint. Since azure.ai.inference does not
    offer an async method out-of-the-box, we wrap the synchronous call
    in asyncio.to_thread to avoid blocking.
    """
    endpoint = "https://models.inference.ai.azure.com"
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(msg.kenOpenAi),)
    # Wrap in to_thread to run in an executor
    response = await asyncio.to_thread(
    client.complete,
    messages=[SystemMessage(content=msg.sys), UserMessage(content=msg.messageOpenAi),],
    temperature=1.0,
    top_p=1.0,
    model=msg.modelOpenAi
    )
    return response.choices[0].message.content

async def Geminif(msg: Message):
    """
    Calls Google Generative AI endpoint. Wrap the generate_content call
    in asyncio.to_thread if the library does not provide asynchronous methods.
    """
    genai.configure(api_key=msg.kenGemini)
    model = genai.GenerativeModel(msg.modelGemini)
    # Wrap in to_thread to run in an executor
    response = await asyncio.to_thread(model.generate_content, msg.messageGemini)
    return response.text

async def Requestf(msg: Message):
    """
    Calls three separate endpoints asynchronously using aiohttp.
    Each request is made in parallel within the same event loop.
    """
    urls = {
    "https://api.x.ai/v1/chat/completions": ["Bearer " + msg.kenX, msg.modelX, msg.messageX],
    "https://api.groq.com/openai/v1/chat/completions": ["Bearer " + msg.kenGroq, msg.modelGrok, msg.messageGrok],
    "https://api.mistral.ai/v1/chat/completions": ["Bearer " + msg.kenMistral, msg.modelMistral, msg.messageMistral],
    }
    
    response_text = []
    async with aiohttp.ClientSession() as session:
        # Gather tasks for each URL
        tasks = []
        for url, API in urls.items():
            headers = {
                "Content-Type": "application/json",
                "Authorization": API[0]
            }
            data = {
                "model": API[1],
                "messages": [{"role": "user", "content": API[2]}]
            }
            tasks.append(fetch_async(session, url, headers, data))
    
        # Run all tasks concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
    
        # Combine non-exception responses
        for resp in responses:
            if isinstance(resp, str):  # If no exception occurred
                response_text.append(resp)
    
    return "".join(response_text)

async def fetch_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict) -> str:
    """
    Helper function for performing a POST asynchronously.
    """
    try:
        # We can pass a timeout via the ClientSession or the .post() method.
        async with session.post(url, headers=headers, json=data, timeout=500) as r:
        r_json = await r.json()
        return r_json['choices'][0]['message']['content']
    except Exception:
        # Catch and return an empty string if any error, or re-raise if you prefer
        return ""

@app.post("/message")
async def receive_message(msg: Message):
    ResponseOpenAI = ''
    ResponseGemini = ''
    ResponseRequest = ''
    
    # Call each endpoint asynchronously within a try/except block
    try:
        ResponseOpenAI = await OpenAIf(msg)
    except:
        pass
    
    try:
        ResponseGemini = await Geminif(msg)
    except:
        pass
    
    try:
        ResponseRequest = await Requestf(msg)
    except:
        pass
    
    return ResponseOpenAI + ResponseGemini + ResponseRequest
    
@app.get("/")
async def root():
    return {"message": "API is running"}
