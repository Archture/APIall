import os
import asyncio
import aiohttp
import requests
import json
import re
# import google.generativeai as genai
# from azure.ai.inference import ChatCompletionsClient
# from azure.ai.inference.models import SystemMessage, UserMessage
# from azure.core.credentials import AzureKeyCredential
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

timeout = 16

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
    messageBig: str
    messageX: str
    messageGroq: str
    messageMistral: str
    messageBaidu: str
    messageCohere: str
    messageTogether: str
    messageOpenRouter: str 
    messageCF: str
    messageOVH: str = "humorous jokes:"
    messageChutes: str = "a flirtatious and spicy tone:"
    messageTargon: str = "a flirtatious and spicy tone:"
    messageFree: str = "a flirtatious and spicy tone:"
    messageAnywhere: str = "precise wording and a sincere tone to give praise:"
    messagePollination: str = "humorous jokes:"
    
    modelOpenAi: str
    modelGemini: str
    modelBig: str
    modelX: str = "grok-2-1212"
    modelGroq: str = "llama-3.3-70b-versatile"
    modelMistral: str
    modelCohere: str
    modelTogether: str
    modelOpenRouter: str = "qwen/qwen2.5-vl-72b-instruct:free"
    modelCF: str = "openchat/openchat-3.5-0106"
    modelOVH: str = "Mistral-Nemo-Instruct-2407"
    modelChutes: str = "open-r1/OlympicCoder-7B" # "cognitivecomputations/Dolphin3.0-Mistral-24B" # "cognitivecomputations/Dolphin3.0-R1-Mistral-24B" #  "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
    modelTargon: str = "deepseek-ai/DeepSeek-V3-0324"
    modelFree: str = "gpt-4o-mini"
    modelAnywhere: str = "gpt-4o-mini"

    kenOpenAi: str
    kenGemini: str
    kenBig: str
    kenX: str
    kenGroq: str
    kenMistral: str
    kenCohere: str
    kenBaiduId: str
    kenBaiduSec: str
    kenTogether: str
    kenOpenRouter: str
    kenCF: str
    kenOVH: str
    kenChutes: str
    kenTargon: str
    kenFree: str
    kenAnywhere: str
    kenFlow: str
    
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

def remove_think_tags(text: str) -> str:
    """移除 <think>...</think> 包裹的内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

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
        response = requests.post(url, headers=headers, data=payload, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error making Baidu API request: {e}")
        raise HTTPException(status_code=500, detail="Error communicating with Baidu API.")

async def RequestfCF(msg: Message):
    url = r'https://api.cloudflare.com/client/v4/accounts/53a4ab7d625890920e433def35a30c59/ai/run/@cf/'+msg.modelCF
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenCF
    }
    data = {
        "messages": [{"role": "user", "content": msg.prompt + msg.messageCF + msg.sentence}]
    }
    
    try:
        response = requests.post(url, headers=headers,json=data,timeout=timeout)
        if response.status_code == 200:
            response_json = response.json()
            # Safely access nested properties
            response_text = response_json['result']['response']
            print("RequestCF: "+response_text)
            return response_text
        else:
            print("Error cloudflare:", response.status_code)
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfCF: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfCF: {e}")
        return ''

async def RequestfOVH(msg: Message):
    url = "https://"+ msg.modelOVH.lower() +".endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1/chat/completions"
    payload = {
        "max_tokens": 512,
        "messages": [
            {
                "content": msg.prompt + msg.messageOVH + msg.sentence,
                "name": "User",
                "role": "user"
            }
        ],
        "model": msg.modelOVH,
        "temperature": 0,
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer " + msg.kenOVH
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
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
    
    return text

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

async def fetch_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        # Create a proper ClientTimeout object
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        # Perform the POST request and raise for non-2xx statuses
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()  # Raises aiohttp.ClientResponseError if status is 4xx/5xx
            
            # Safely parse the response as JSON
            r_json = await response.json()
            
            # Safely navigate the nested JSON structure
            # e.g., r_json['choices'][0]['message']['content']
            choices = r_json.get('choices', [])
            if len(choices) > 0:
                message_dict = choices[0].get('message', {})
                return message_dict.get('content', "")
            
            # If the expected fields are not present, return a fallback/string
            print("Response JSON does not contain the expected structure. r_json:"+str(r_json))
            return ""
    
    except asyncio.TimeoutError:
        print(f"Timeout error for {url}")
        return ""
    
    # Handle errors for non-2xx status codes
    except aiohttp.ClientResponseError as e:
        print(f"HTTP error (status={e.status}) in fetch_async for {url}: {e}")
        return ""
    
    # Handle JSON decoding/content-type issues
    except aiohttp.ContentTypeError as e:
        print(f"Unable to parse JSON in response for {url}: {e}")
        return ""
    
    # Catch other types of client errors (e.g., connection issues)
    except aiohttp.ClientError as e:
        print(f"Client error in fetch_async for {url}: {e}")
        return ""
    
    # Catch all other unexpected exceptions
    except Exception as e:
        print(f"Unexpected error in fetch_async for {url}: {e}")
        return ""


async def Requestf(msg: Message):
    urls = {
        "https://api.x.ai/v1/chat/completions": ["Bearer " + msg.kenX, msg.modelX, msg.prompt + msg.messageX + msg.sentence],
        "https://open.bigmodel.cn/api/paas/v4/chat/completions": ["Bearer " + msg.kenBig, msg.modelBig, msg.prompt + msg.messageBig + msg.sentence],
        "https://api.groq.com/openai/v1/chat/completions": ["Bearer " + msg.kenGroq, msg.modelGroq, msg.prompt + msg.messageGroq + msg.sentence],
        "https://api.mistral.ai/v1/chat/completions": ["Bearer " + msg.kenMistral, msg.modelMistral, msg.prompt + msg.messageMistral + msg.sentence],
        "https://api.together.xyz/v1/chat/completions":["Bearer " + msg.kenTogether, msg.modelTogether, msg.prompt + msg.messageTogether + msg.sentence],
        "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions":["Bearer " + msg.kenGemini, msg.modelGemini, msg.prompt + msg.messageGemini + msg.sentence],
        "https://models.inference.ai.azure.com/chat/completions":["Bearer " + msg.kenOpenAi, msg.modelOpenAi, msg.prompt + msg.messageOpenAi + msg.sentence],
        "https://openrouter.ai/api/v1/chat/completions":["Bearer " + msg.kenOpenRouter, msg.modelOpenRouter, msg.prompt + msg.messageOpenRouter + msg.sentence],   
        "https://chutes-"+ msg.modelChutes.lower().replace(r'/', '-').replace('.', '-') +".chutes.ai/v1/chat/completions":["Bearer " + msg.kenChutes, msg.modelChutes, msg.prompt + msg.messageChutes + msg.sentence],    
        "https://free.v36.cm/v1/chat/completions": ["Bearer " + msg.kenFree, msg.modelFree, msg.prompt + msg.messageFree + msg.sentence],
        "https://api.chatanywhere.org/v1/chat/completions": ["Bearer " + msg.kenAnywhere, msg.modelAnywhere, msg.prompt + msg.messageAnywhere + msg.sentence],
    }

    response_text = []
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_async(session, url, {"Content-Type": "application/json", "Authorization": API[0]}, {
                "model": API[1],
                "messages": [{"role": "user", "content": API[2]}]
            }, timeout) for url, API in urls.items()
        ]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        for i,resp in enumerate(responses):
            if isinstance(resp, str):
                response_text.append(resp)
                print(str(i)+resp)

    return "||".join(response_text)

async def RequestfAlt(msg: Message):
    url = r"https://api.cohere.com/v2/chat"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + msg.kenCohere
    }
    data = {
        "model": msg.modelCohere,
        "messages": [{"role": "user", "content": msg.prompt + msg.messageCohere + msg.sentence}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        # Parse JSON response
        response_json = response.json()
        
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

async def RequestfWorkflow(msg: Message):
    url = r"https://api.vectorshift.ai/api/chatbots/run"
    headers = {
        "Api-Key": msg.kenFlow
    }
    data = {
        "input": msg.sentence,"chatbot_name": "chat","username": "loveoraclevery","conversation_id": None
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=timeout)
        
        # Parse JSON response
        response_json = response.json()
        
        # Safely access nested properties
        response_text = response_json.get('output', '')
        
        # print("Response:", response)
        print("RequestfWorkflow: "+response_text)
        
        return response_text
                
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfWorkflow: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfWorkflow: {e}")
        print("Full JSON Response:", response_json)
        return ''


async def Requestfstream(msg: Message):
    url = r"https://api.targon.com/v1/chat/completions"
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
        response = requests.post(url, headers=headers, json=data, timeout=timeout, stream=True)
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

        print("Requestfstream: "+ full_response)
        return full_response
    except Exception as e:
        print(f"Error in Requestfstream: {e}")
        return ""

async def baidu_request_async(msg: Message):
    try:
        raw_response = ask_Q(msg)
        response = raw_response.json().get('result', 'No result retrieved')
        print('baidu: '+response)
        return response
    except Exception as e:
        print(f"Error in baidu_request_async: {e}")
        return ""

async def RequestfPollination(msg: Message):
    url = r"https://text.pollinations.ai/"
    try:
        # Use aiohttp for async request instead of synchronous requests
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url + msg.prompt + msg.messagePollination + msg.sentence, 
                timeout=timeout
            ) as response:
                # Get text content from the response
                response_text = await response.text()
                print(f"RequestfPollination response: {response_text}")
                return response_text
    except aiohttp.ClientError as e:
        print(f"Request error in RequestfPollination: {e}")
        return ''
    except (KeyError, IndexError, ValueError) as e:
        print(f"Response parsing error in RequestfPollination: {e}")
        # Remove reference to undefined response_json variable
        return ''




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
        RequestfOVH(msg),
        Requestfstream(msg),
        RequestfWorkflow(msg),
        RequestfPollination(msg),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    response_texts = [result for result in results if isinstance(result, str)]
    
    return remove_think_tags("||".join(response_texts))

@app.get("/")
async def root():
    return {"message": "API is running"}
