import os
import google.generativeai as genai
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, Request, Header
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

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


async def OpenAIf(msg)
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

async def Requestf(url, msg):
    headers = {
        "Content-Type": "application/json",
        "Authorization": API[0]
    }
    data = {
        # "model": ,
        "model": API[1],
        "messages": [{"role": "user","content": "Who are you?"}]
    try:
        # Make the POST request with a timeout (e.g., 30 seconds)
        response = requests.post(url, headers=headers, json=data, timeout=500)

        # Check if the request was successful
        if response.status_code == 200:
            # print("Response received:", response.json()['choices'][0]['message']['content'])
            print(response.json()['data'][0]['url'])
        else:
            print("Request failed with status code:", response.status_code)
    except requests.exceptions.Timeout:
        print("The request timed out")
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


      
    return Response



@app.post("/message")
async def receive_message(msg: Message):
    ResponseOpenAI = OpenAIf(msg)
    ResponseGemini = Geminif(msg)



  
    
    # Log the message and model received
    print(f"Received message: {msg.message}")
    print(f"Received model: {msg.model}")

    # For the sake of this example, the response will return the message and model
    print(f"Sent response: {Response}")

    return Response






@app.get("/")
async def root():
    return {"message": "API is running"}
