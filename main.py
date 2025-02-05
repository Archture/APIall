import os
import asyncio
import aiohttp
import requests
import json
# import google.generativeai as genai
# from azure.ai.inference import ChatCompletionsClient
# from azure.ai.inference.models import SystemMessage, UserMessage
# from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# -------------------- FastAPI Setup --------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    messageOpenAi: str
    messageGemini: str
    messageX: str
    messageGroq: str
    messageMistral: str
    messageBaidu: str
    messageCohere: str
    messageTogether: str

    modelOpenAi: str
    modelGemini: str
    modelX: str
    modelGroq: str
    modelMistral: str
    modelCohere: str
    modelTogether: str

    kenOpenAi: str
    kenGemini: str
    kenX: str
    kenGroq: str
    kenMistral: str
    kenCohere: str
    kenBaiduId: str
    kenBaiduSec: str
    kenTogether: str
    sys: str = "You are a helpful assistant."

def get_access_token(msg: Message):
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": msg.kenBaiduId,
        "client_secret": msg.kenBaiduSec
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

def ask_Q(msg: Message):
    access_token = get_access_token(msg)
    if not access_token:
        raise HTTPException(status_code=500, detail="Failed to retrieve access token.")

    url = (
        f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/"
        f"wenxinworkshop/chat/ernie-speed-128k?access_token={access_token}"
    )
    payload = json.dumps({
        "messages": [{"role": "user", "content": msg.messageBaidu}]
    })
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error making Baidu API request: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with Baidu API.")

async def OpenAIf(msg: Message):
    endpoint = "https://models.inference.ai.azure.com"
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(msg.kenOpenAi))
    response = await asyncio.to_thread(
        client.complete,
        messages=[SystemMessage(content=msg.sys), UserMessage(content=msg.messageOpenAi)],
        temperature=1.0,
        top_p=1.0,
        model=msg.modelOpenAi
    )
    return response.choices[0].message.content

async def Geminif(msg: Message):
    genai.configure(api_key=msg.kenGemini)
    model = genai.GenerativeModel(msg.modelGemini)
    response = await asyncio.to_thread(model.generate_content, msg.messageGemini)
    return response.text

async def fetch_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict) -> str:
    try:
        async with session.post(url, headers=headers, json=data, timeout=30) as r:
            r_json = await r.json()
            return r_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in fetch_async: {e}")
        return ""

async def Requestf(msg: Message):
    urls = {
        "https://open.bigmodel.cn/api/paas/v4/chat/completions": ["Bearer " + msg.kenX, msg.modelX, msg.messageX],
        "https://api.groq.com/openai/v1/chat/completions": ["Bearer " + msg.kenGroq, msg.modelGroq, msg.messageGroq],
        "https://api.mistral.ai/v1/chat/completions": ["Bearer " + msg.kenMistral, msg.modelMistral, msg.messageMistral],
        "https://api.together.xyz/v1/chat/completions":["Bearer " + msg.kenTogether, msg.modelTogether, msg.messageTogether],
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions":["Bearer " + msg.kenGemini, msg.modelGemini, msg.messageGemini],
        "https://models.inference.ai.azure.com/chat/completions":["Bearer " + msg.kenOpenAi, msg.modelOpenAi, msg.messageOpenAi]

    }

    response_text = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_async(session, url, {"Content-Type": "application/json", "Authorization": API[0]}, {
                "model": API[1],
                "messages": [{"role": "user", "content": API[2]}]
            }) for url, API in urls.items()
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for resp in responses:
            if isinstance(resp, str):
                response_text.append(resp)

    return "".join(response_text)

async def RequestfAlt(msg: Message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenCohere
    }
    data = {
        "model": msg.modelCohere,
        "messages": [{"role": "user", "content": msg.messageCohere}]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.cohere.com/v2/chat",
                headers=headers,
                json=data,
                timeout=500
            ) as response:
                # Ensure the request was successful
                response.raise_for_status()
                
                # Parse JSON response
                response_json = await response.json()
                
                # Safely access nested properties
                response_text = response_json.get('message', {}).get('content', [{}])[0].get('text', '')
                
                # print("Response:", response)
                # print("Response text:", response_text)
                
                return response_text
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfAlt: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfAlt: {e}")
        return ''

async def baidu_request_async(msg: Message):
    try:
        raw_response = await asyncio.to_thread(ask_Q, msg)
        return raw_response.json().get('result', 'No result retrieved')
    except Exception as e:
        print(f"Error in baidu_request_async: {e}")
        return ""

@app.post("/message")
async def receive_message(msg: Message):
    # Create the tasks
    tasks = [
        # asyncio.create_task(OpenAIf(msg)),
        # asyncio.create_task(Geminif(msg)),
        asyncio.create_task(Requestf(msg)),
        asyncio.create_task(RequestfAlt(msg)),
        asyncio.create_task(baidu_request_async(msg))
    ]

    # Wait up to 30 seconds for the tasks to complete
    done, pending = await asyncio.wait(tasks, timeout=35)

    # Cancel any tasks that didn't finish
    for p in pending:
        p.cancel()

    # Gather results from the tasks that completed
    results = []
    for d in done:
        try:
            result = d.result()  # May raise an exception if the task failed
            if isinstance(result, str):
                results.append(result)
        except Exception:
            # Handle or ignore exceptions in tasks
            pass

    # Return a combined string of valid results
    return "".join(results)

@app.get("/")
async def root():
    return {"message": "API is running"}
