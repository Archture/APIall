import os
import google.generativeai as genai
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. For more security, specify the origins you need.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Define the model with an additional 'model' field
class Message(BaseModel):
    message: str
    model: str  # New 'model' field to be sent in the JSON body
    ken: str
    sys: str = "You are a helpful assistant."

async def OpenAIf(msg):
    endpoint = "https://models.inference.ai.azure.com"

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(msg.kenOpenAi),
    )

    response = client.complete(
        messages=[
            SystemMessage(content=msg.sys),
            UserMessage(content=msg.messageOpenAi),
        ],
        temperature=1.0,
        top_p=1.0,
        # max_tokens=1000,
        model=msg.modelOpenAi
    )
    Response = response.choices[0].message.content
    return Response

async def Geminif(msg):
    genai.configure(api_key=msg.kenGemini)

    model = genai.GenerativeModel(msg.modelGemini)
    response = model.generate_content(msg.messageGemini)

    Response = response.text
    return Response

async def Requestf(msg):
    urls = {
        "https://api.x.ai/v1/chat/completions": ["Bearer "+msg.kenX, "grok-beta"],
        "https://api.groq.com/openai/v1/chat/completions": ["Bearer "+msg.kenGroq, "llama-3.3-70b-specdec"],
        "https://api.mistral.ai/v1/chat/completions": ["Bearer "+msg.kenMistral, "mistral-large-latest"],
    }

    for url, API in urls.items():
        headers = {
            "Content-Type": "application/json",
            "Authorization": API[0]
        }

        data = {
            "model": API[1],
            "messages": [{"role": "user","content": msg.messageRequest}]
        }

        response = requests.post(url, headers=headers, json=data, timeout=500)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']

@app.post("/message")
async def receive_message(msg: Message):
    ResponseOpenAI = ''
    ResponseGemini = ''
    ResponseRequest = ''

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
