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
    messageOpenRouter: str 
    messageCF: str

    modelOpenAi: str
    modelGemini: str
    modelX: str
    modelGroq: str
    modelMistral: str
    modelCohere: str
    modelTogether: str
    modelOpenRouter: str = "qwen/qwen2.5-vl-72b-instruct:free"
    modelCF: str = "microsoft/phi-2"

    kenOpenAi: str
    kenGemini: str
    kenX: str
    kenGroq: str
    kenMistral: str
    kenCohere: str
    kenBaiduId: str
    kenBaiduSec: str
    kenTogether: str
    kenOpenRouter: str
    kenCF: str
    
    sys: str = "You are a helpful assistant."
    sentence: str
    prompt: str

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
        "messages": [{"role": "user", "content": msg.prompt + msg.messageBaidu + msg.sentence}]
    })
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=35)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error making Baidu API request: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with Baidu API.")

async def RequestfCF(msg: Message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenCF
    }
    data = {
        "messages": [{"role": "user", "content": msg.prompt + msg.messageCF + msg.sentence}]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                r'https://api.cloudflare.com/client/v4/accounts/53a4ab7d625890920e433def35a30c59/ai/run/@cf/'+msg.modelCF,
                headers=headers,
                json=data,
                timeout=35
            ) as response:
                # Ensure the request was successful
                response.raise_for_status()
                
                # Parse JSON response
                response_json = await response.json()
                
                # Safely access nested properties
                response_text = response_json['result']['response']
                
                print("RequestCF: "+response_text)
                
                return response_text
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfAlt: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfAlt: {e}")
        return ''

async def RequestfOVH(msg: Message):
    url = "https://mistral-nemo-instruct-2407.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1/chat/completions"
    payload = {
        "max_tokens": 512,
        "messages": [
            {
                "content": "Explain gravity for a 6 years old",
                "name": "User",
                "role": "user"
            }
        ],
        "model": "Mistral-Nemo-Instruct-2407",
        "temperature": 0,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJFZERTQSJ9.eyJwcm9qZWN0IjoiMzBhOWM0MmNjNDNjNGQ3Nzk3NmU0NjFhNDk3MTIyM2YiLCJhdWQiOiIzNzM4NjExNjY0MDQzMDM0IiwiZXhwIjoxMDk2MjcxMjY4MywianRpIjoiNmE0YTVlMTUtNTM1ZC00NGEzLWIzMDEtYTU4NTBmNzg0OWQwIiwiaXNzIjoidHJhaW5pbmcuYWkuY2xvdWQub3ZoLm5ldCIsInN1YiI6ImNuNDg4MDUwLW92aCIsIm92aFRva2VuIjoieDdWRVlxZHZEOHRIazYtaHRWenRxb2hZY1lhNUhLMXZ2OHpJUGpRX09KWFhqU192X1NOeG54ZHAtV3lGVDA4ekxwWDZNZUZ4MlVyQnNNVHdWcDlPRlhtTUdoQktGejFjZ19hQWFwMGpxcFhwQU5kOFYzYnFSRTlBbzMzQVpKd1VHQmRNT0pmMXAtaFpibUM5eTJVTkNyT3JSbGYzbk84dHRNSWxTR3h4XzRVSTFaMW9jVVdfY3RVWmphaFFiVUhwdXpQTWtva18tYXBkTmhkZUVUUjNXYUtXdHU0U29mSURQRmxoNExvdEFHQTNkMXRqUm94VGU0LVhhajhQUm9GeDJyZlZ4RGc3WmlNQzBJUDltUkxoZkRDRE9PVWFOQVJLRHMtMUFNMlp0X01FOVdJVEc2alF6NW1rNUZmTmoyR0tPVVVwcVRvaW01MjcwY1FhZlM0dTdYOXBFUS15eEZsMEhoc3FYc0VnNExqbzZmQVVaV0JncnFVYkNwMXZKQ25kSlZQR0lfeE9EbllSNkVoNWpjS2h2ZUFMdHNtajdfVV9fMGRxUHdEdExibFJWNDlGandxRE8wWGF3Sk80aU5pVF9PS2lyQ0hGLTdPdGdCampDZVJCUGxsUmZZYm1lZ0hUM1poS00zT1l2a3A0R3pmUlVYekpobWhfSGtCSGxDemtBdzR4VzJBMmdkOXF2WmYxQXpzUDhRTFBBLWk3Nk9SaTZJQ2cxV3dCVGVKNVN1ZkdmWnpKTWZSOXJzTzJxUnVDQzJLOGFDZlhGc3FqSkQ2OWhVcUpGcDR0S09qQWZuN1RwZHRyemdONFVySHJPZVhJOWJSc2xDVm4wUHUxejEzQktKUVJ0NWRuajZpS0FyUHhxYjRCdnhHS2ZJZGg0Y3dIMGgyelZDZGREMkMtWndXQ0xRTTZJR0E5TUREYXgzVUlneXQ1dm44REhuU0ZGaUF0dmkya3JHcnVicWRtMUxwU3ktN29fdjlfNDNmQnNxMW1xdXZ0R0N4NHZveEFNUl9XREtQWjBMeXMtX09zMGtOWTd0b3FiVDJ4alYwU1FOLWMtV1BIZ19ValJBVkJtTFZYQ1ZxRUw2dXlEODU4ODg5NzYyZ05xT1g1OENQaUozendvSzVFVUpHY3ZHNVdLVHN1dS1LWnRfVlRwR2o4ZHlKMWN5Y0pZZHFsWjQzSVhFVTc0dTk1SThidXVsZ3VidTVKcEhSZ0hHRTJ4SFlPS2MxTm5tWXdLd0tKRzhDVWNwYmU0X2M3UW0zRkZzSEpNeTNWdzd5LWV3UWh3WTc1cUhGMmdGRXR4OXRLUDRUdkVFVkhMNmRhcXBrVnBmWmEifQ.RaNRzGB_3p5zwfP-RS9MZHS2cZDCU-H1ccFrZWDr-iBFQPrYgpFPtmdnKfyGnZerSEcK93M-aPnYZ_X1IsHkDQ",
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        # Handle response
        response_data = response.json()
        # Parse JSON response
        choices = response_data["choices"]
        for choice in choices:
            text = choice["message"]["content"]
            # Process text and finish_reason
            print('OVH:' + text)
    else:
        print("Error:", response.status_code)

async def OpenAIf(msg: Message):
    endpoint = "https://models.inference.ai.azure.com"
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(msg.kenOpenAi))
    response = await asyncio.to_thread(
        client.complete,
        messages=[SystemMessage(content=msg.sys), UserMessage(content=msg.prompt + msg.messageOpenAi + msg.sentence)],
        temperature=1.0,
        top_p=1.0,
        model=msg.modelOpenAi
    )
    return response.choices[0].message.content

async def Geminif(msg: Message):
    genai.configure(api_key=msg.kenGemini)
    model = genai.GenerativeModel(msg.modelGemini)
    response = await asyncio.to_thread(model.generate_content, msg.prompt + msg.messageGemini + msg.sentence)
    print('Gemini: '+ response)
    return response.text

async def fetch_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict) -> str:
    try:
        async with session.post(url, headers=headers, json=data, timeout=35) as r:
            r_json = await r.json()
            return r_json['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in fetch_async: {e}")
        print(r_json)
        return ""

async def Requestf(msg: Message):
    urls = {
        "https://open.bigmodel.cn/api/paas/v4/chat/completions": ["Bearer " + msg.kenX, msg.modelX, msg.prompt + msg.messageX + msg.sentence],
        "https://api.groq.com/openai/v1/chat/completions": ["Bearer " + msg.kenGroq, msg.modelGroq, msg.prompt + msg.messageGroq + msg.sentence],
        "https://api.mistral.ai/v1/chat/completions": ["Bearer " + msg.kenMistral, msg.modelMistral, msg.prompt + msg.messageMistral + msg.sentence],
        "https://api.together.xyz/v1/chat/completions":["Bearer " + msg.kenTogether, msg.modelTogether, msg.prompt + msg.messageTogether + msg.sentence],
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions":["Bearer " + msg.kenGemini, msg.modelGemini, msg.prompt + msg.messageGemini + msg.sentence],
        "https://models.inference.ai.azure.com/chat/completions":["Bearer " + msg.kenOpenAi, msg.modelOpenAi, msg.prompt + msg.messageOpenAi + msg.sentence],
        "https://openrouter.ai/api/v1/chat/completions":["Bearer " + msg.kenOpenRouter, msg.modelOpenRouter, msg.prompt + msg.messageOpenRouter + msg.sentence],
        "https://chutes-deepseek-ai-deepseek-r1-distill-llama-70b.chutes.ai/v1/chat/completions":["Bearer " + msg.ken, "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", msg.prompt + msg.message + msg.sentence],
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
        for i,resp in enumerate(responses):
            if isinstance(resp, str):
                response_text.append(resp)
                print(str(i)+resp)

    return "".join(response_text)

async def RequestfAlt(msg: Message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenCohere
    }
    data = {
        "model": msg.modelCohere,
        "messages": [{"role": "user", "content": msg.prompt + msg.messageCohere + msg.sentence}]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.cohere.com/v2/chat",
                headers=headers,
                json=data,
                timeout=35
            ) as response:
                # Ensure the request was successful
                response.raise_for_status()
                
                # Parse JSON response
                response_json = await response.json()
                
                # Safely access nested properties
                response_text = response_json.get('message', {}).get('content', [{}])[0].get('text', '')
                
                # print("Response:", response)
                print("RequestfAlt: "+response_text)
                
                return response_text
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfAlt: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfAlt: {e}")
        return ''

async def Requestfstream(msg: Message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenTargon
    }
    data = {
        "model": msg.modelTargon,
        "messages": [{"role": "user", "content": msg.prompt + msg.messageTargon + msg.sentence}],
        "stream": True,
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.cohere.com/v2/chat",
                headers=headers,
                json=data,
                timeout=35,
                stream=True
            ) as response:
                # Ensure the request was successful
                response.raise_for_status()
                
                full_response = ""
            
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        if decoded_line.startswith("data: "):  # OpenAI sends data in this format
                            chunk = decoded_line[len("data: "):]  # Remove 'data: ' prefix
                            if chunk.strip() != "[DONE]":  # Ignore the termination signal
                                try:
                                    json_data = json.loads(chunk)
                                    full_response += json_data["choices"][0]["delta"].get("content", "")
                                except:
                                    pass  # Ignore malformed JSON parts
            
                print("Requestfstream:", full_response)
                
                return full_response
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfAlt: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfAlt: {e}")
        return ''



async def baidu_request_async(msg: Message):
    try:
        raw_response = await asyncio.to_thread(ask_Q, msg)
        response = raw_response.json().get('result', 'No result retrieved')
        print('baidu: '+response)
        return response
    except Exception as e:
        print(f"Error in baidu_request_async: {e}")
        return ""

@app.post("/message")
async def receive_message(msg: Message):
    # Create the tasks
    tasks = [
        # OpenAIf(msg),
        # Geminif(msg),
        Requestf(msg),
        RequestfAlt(msg),
        baidu_request_async(msg),
        RequestfCF(msg),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    response_texts = [result for result in results if isinstance(result, str)]
    return "".join(response_texts)

@app.get("/")
async def root():
    return {"message": "API is running"}
