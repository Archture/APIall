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
    messageOpenAi: str
    messageGemini: str
    messageX: str
    messageGrok: str
    messageMistral: str
    
    modelOpenAi: str  # New 'model' field to be sent in the JSON body
    modelGemini: str  # New 'model' field to be sent in the JSON body
    modelX: str  # New 'model' field to be sent in the JSON body
    modelGrok: str  # New 'model' field to be sent in the JSON body
    modelMistral: str  # New 'model' field to be sent in the JSON body
    
    kenOpenAi: str
    kenGemini: str
    kenX: str
    kenGroq: str
    kenMistral: str
    
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
        "https://api.x.ai/v1/chat/completions": ["Bearer "+msg.kenX, msg.modelX, msg.messageX],
        "https://api.groq.com/openai/v1/chat/completions": ["Bearer "+msg.kenGroq, msg.modelGrok, msg.messageGrok],
        "https://api.mistral.ai/v1/chat/completions": ["Bearer "+msg.kenMistral, msg.modelMistral, msg.messageMistral],
    }
    Response = ''
    for url, API in urls.items():
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": API[0]
            }
    
            data = {
                "model": API[1],
                "messages": [{"role": "user","content": API[2]}]
            }
    
            response = requests.post(url, headers=headers, json=data, timeout=500)
    
            Response += response.json()['choices'][0]['message']['content']
        except:
            pass
    return Response

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
