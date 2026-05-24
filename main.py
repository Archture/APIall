import os
import asyncio
import aiohttp
import requests
import json
import re
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from providers import PROVIDERS

timeout = 40

# Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == settings.FASTAPI_API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )
 
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
    messageOpenAi: str = "humorous jokes:"
    messageGemini: str = "flirtatious pick-up lines. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messageBig: str = "conversational and playful push-and-pull technique"
    messageGroq: str = "the workflow. First, capture the person's emotions, and then discern the needs behind the words. If the person is in a positive mood, use a cheerful tone. If the person is in a negative mood, align yourself with the person. Focus solely on addressing their emotions without offering specific advice:"
    messageMistral: str = "the workflow. First, capture the person's emotions, and then discern the needs behind the words. If the person is in a positive mood, use a cheerful tone. If the person is in a negative mood, align yourself with the person. Focus solely on addressing their emotions without offering specific advice:"
    messageBaidu: str = "humorous jokes:"
    messageCohere: str = "conversational and playful push-and-pull technique"
    messageTogether: str = "a flirtatious and spicy tone. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messageOpenRouter: str = "humorous jokes:"
    messageCF: str = " humorous jokes:"
    messageOVH: str = "humorous jokes:"
    messageChutes: str = "a flirtatious and spicy tone. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messageTargon: str = "a flirtatious and spicy tone. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messagePollination: str = "a flirtatious and spicy tone. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messageFree: str = "a flirtatious and spicy tone. You are spicy, playful, and sharp-witted, with a knack for flirting. You love teasing and has a seductive charm that keeps conversations thrilling and unpredictable:"
    messageAnywhere: str = "precise wording and a sincere tone to give praise:"
    messageCerebras: str = "humorous jokes:"
    messageFastGPT: str = "pick-up lines or humorous jokes:"
    messageSiliconFlow: str = "pick-up lines or humorous jokes:"
    messageInfini: str = "conversational and playful push-and-pull technique"
    messageInternlm: str = "humorous jokes:"
    messageScope: str = "humorous jokes:"
    messageHuggingface: str = "humorous jokes:"
    messageOllma: str = "conversational and playful push-and-pull technique"
    messageGrok: str = "humorous jokes:"
    messageZenmux: str = "humorous jokes:"
    messageLongcat: str = "precise wording and a sincere tone to give praise:"
    messageNvidia: str = "conversational and playful push-and-pull technique"
    messageLiterouter: str = "humorous jokes:"
    messageRouteway: str = "humorous jokes:"
    messagePoixe: str = "humorous jokes:"
    messageZaiwenai: str = "precise wording and a sincere tone to give praise:"
    messageAihubmix: str = "humorous jokes:"
    messageElectronhub: str = "humorous jokes:"
    messageModelshub: str = "humorous jokes:"
    messageDataeyes: str = "humorous jokes:"
    messageNage: str = "humorous jokes:"
    messageSpark: str = "humorous jokes:"
    messageAskcodi: str = "humorous jokes:"
    messageGitcode: str = "humorous jokes:"
    messageMaas: str = "humorous jokes:"
    messageScitely: str = "humorous jokes:"
    messageNavy: str = "humorous jokes:"
    messageHidns: str = "humorous jokes:"
    messageOai: str = "conversational and playful push-and-pull technique"
    messageFreetheai: str = "conversational and playful push-and-pull technique"
    messageSensenova: str = "conversational and playful push-and-pull technique"
    messageIamhc: str = "conversational and playful push-and-pull technique"
    
    modelOpenAi: str = "openai/gpt-4.1"
    modelGemini: str = "models/gemini-2.5-flash"
    modelBig: str = "GLM-4-Flash"
    modelGroq: str = "llama-3.3-70b-versatile"
    modelMistral: str = "mistral-large-latest"
    modelCohere: str = "command-r-plus-08-2024"
    modelTogether: str = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free"
    modelOpenRouter: str = "meta-llama/llama-3.3-70b-instruct:free"
    modelCF: str = "@cf/openai/gpt-oss-120b"
    modelOVH: str = "Mistral-Nemo-Instruct-2407"
    modelChutes: str = "open-r1/OlympicCoder-7B" 
    modelTargon: str = "deepseek-ai/DeepSeek-V3-0324"
    modelPollination: str = ""
    modelBaidu: str = "ernie-speed-128k"
    modelCerebras: str = "gpt-oss-120b"
    modelFastGPT: str = ""
    modelSiliconFlow: str = "THUDM/GLM-4-9B-0414"
    modelInfini: str = "megrez-3b-instruct"
    modelInternlm: str = "internlm3-latest"
    modelScope: str = "deepseek-ai/DeepSeek-V3.2"
    modelHuggingface: str = "deepseek-ai/DeepSeek-V3-0324"
    modelOllma: str = "gpt-oss:120b"
    modelGrok: str = "xai/grok-3"
    modelZenmux: str = "z-ai/glm-4.6v-flash-free"
    modelLongcat: str = "LongCat-Flash-Chat"
    modelNvidia: str = "minimaxai/minimax-m2.1"
    modelLiterouter: str = "gpt-oss-120b:free"
    modelRouteway: str = "minimax-m2:free"
    modelPoixe: str = "claude-sonnet-4-5-20250929:free"
    modelZaiwenai: str = "gpt-5-nano"
    modelAihubmix: str = "gpt-4.1-free"
    modelElectronhub: str = "gpt-4.1"
    modelModelshub: str = "openai/gpt-oss-120b:free"
    modelDataeyes: str = "gpt-oss-120b"
    modelNage: str = "gemini-2.5-flash:free"
    modelSpark: str = "lite"
    modelAskcodi: str = "zai/glm-4.5-air:free"
    modelGitcode: str = "zai-org/GLM-5"
    modelMaas: str = "xop3qwencodernext"
    modelScitely: str = "deepseek-v3.2"
    modelNavy: str = "grok-4.1-fast-non-reasoning"
    modelHidns: str = "anthropic/claude-sonnet-4.6"
    modelOai: str = "openai/gpt-oss-120b"
    modelFreetheai: str = "or/openai/gpt-oss-120b:free"
    modelSensenova: str = "sensenova-6.7-flash-lite"
    modelIamhc: str = "auto"

    sys: str = "Avoid greasy, old-fashioned, robotic replies. Keep it under 30 words. Make it conversational and personable."
    sentence: str
    prompt: str

def get_baidu_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": settings.BAIDU_ID,
        "client_secret": settings.BAIDU_SEC
    }
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except requests.RequestException as e:
        print(f"Error getting access token: {e}")
        return None

async def baidu_request_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    access_token = get_baidu_access_token()
    if not access_token:
        return "Failed to get Baidu access token"

    url_with_token = f"{url}?access_token={access_token}"
    
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url_with_token, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            return r_json.get('result', 'No result retrieved')
    except aiohttp.ClientError as e:
        print(f"Error in baidu_request_async: {e}")
        return ""

def remove_think_tags(text: str) -> str:
    """移除 <think>...</think> 包裹的内容"""
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

async def request_cloudflare(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            return r_json.get('result', {}).get('response', '')
    except aiohttp.ClientError as e:
        print(f"Error in request_cloudflare: {e}")
        return ""

async def request_ovh(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            choices = r_json.get('choices', [])
            if len(choices) > 0:
                message_dict = choices[0].get('message', {})
                return message_dict.get('content', "")
            return ""
    except aiohttp.ClientError as e:
        print(f"Error in request_ovh: {e}")
        return ""

async def fetch_async(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        # Create a proper ClientTimeout object
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        
        # Perform the POST request and raise for non-2xx statuses
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            body_text = await response.text()
            
            # If non-2xx, log status and full body for debugging
            if not 200 <= response.status < 300:
                print(f"HTTP error (status={response.status}) for {url}")
                print("Response body:", body_text)
                return ""
            
            # Otherwise try to parse JSON
            try:
                r_json = await response.json()
            except aiohttp.ContentTypeError:
                body_text = await response.text()
                # Check if it's an SSE stream prefixed with "data:"
                body_text_stripped = body_text.strip()
                if body_text_stripped.startswith("data:"):
                    # Remove the "data:" prefix (first 5 characters) and parse
                    json_string = body_text_stripped[5:].strip()
                    try:
                        r_json = json.loads(json_string)
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON from data payload for {url}:")
                        print(body_text)
                        return ""
                else:
                    # It's something else entirely (e.g., an HTML error page)
                    print(f"Expected JSON but got something else for {url}:")
                    print(body_text)
                    return ""

            
            # Navigate the choice structure
            choices = r_json.get('choices', [])
            if choices:
                return choices[0].get('message', {}).get('content', "")
            
            # Fallback if structure isn’t as expected
            print("Response JSON does not contain choices. Full payload:")
            print(r_json)
            return ""
    
    except asyncio.TimeoutError:
        print(f"Timeout error for {url}")
        return ""
    except aiohttp.ClientError as e:
        # This will catch connection errors, etc.
        print(f"Client error in fetch_async for {url}: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected error in fetch_async for {url}: {e}")
        return ""


async def request_cohere(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            return r_json.get('message', {}).get('content', [{}])[0].get('text', '')
    except aiohttp.ClientError as e:
        print(f"Error in request_cohere: {e}")
        return ""

async def request_dify_workflow(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            return r_json.get('data', {}).get('outputs', {}).get('text', '')
    except aiohttp.ClientError as e:
        print(f"Error in request_dify_workflow: {e}")
        return ""


async def request_vectorshift_workflow(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            r_json = await response.json()
            return r_json.get('outputs', {}).get('output_0', '')
    except aiohttp.ClientError as e:
        print(f"Error in request_vectorshift_workflow: {e}")
        return ""


async def request_targon_stream(session: aiohttp.ClientSession, url: str, headers: dict, data: dict, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.post(url, headers=headers, json=data, timeout=timeout_obj) as response:
            response.raise_for_status()
            full_response = ""
            async for line in response.content:
                if line:
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line.startswith("data: "):
                        chunk = decoded_line[len("data: "):]
                        if chunk.strip() != "[DONE]":
                            try:
                                json_data = json.loads(chunk)
                                full_response += json_data["choices"][0]["delta"].get("content", "")
                            except:
                                pass
            return full_response
    except aiohttp.ClientError as e:
        print(f"Error in request_targon_stream: {e}")
        return ""

async def request_pollination(session: aiohttp.ClientSession, url: str, timeout: float = timeout) -> str:
    try:
        timeout_obj = aiohttp.ClientTimeout(total=timeout)
        async with session.get(url, timeout=timeout_obj) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        print(f"Error in request_pollination: {e}")
        return ""




@app.post("/message")
async def receive_message(msg: Message, api_key: str = Depends(get_api_key)):
    msg.prompt = msg.sys + msg.prompt
    tasks = []
    async with aiohttp.ClientSession() as session:
        for provider_name, provider_data in PROVIDERS.items():
            model_name = getattr(msg, provider_data.get("model", ""), None)
            if not model_name and "model" in provider_data:
                continue

            url = provider_data["url"]
            if "{model}" in url:
                url = url.format(model=model_name.lower().replace(r'/', '-').replace('.', '-'))

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {provider_data.get('key')}",
            }

            data = {}
            request_func = None

            if provider_name == "cohere":
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": msg.prompt + getattr(msg, provider_data["message"])},
                        {"role": "user", "content": msg.sentence},
                    ],
                }
                request_func = request_cohere
            elif provider_name == "cloudflare":
                # url += model_name
                data = {
                    "model": model_name,
                    "input": [
                        {"role": "system", "content": msg.prompt + getattr(msg, provider_data["message"])},
                        {"role": "user", "content": msg.sentence},
                    ],
                }
                request_func = request_cloudflare
            # elif provider_name == "ovh":
            #     url = url.format(model=model_name.lower())
            #     data = {
            #         "max_tokens": 512,
            #         "messages": [
            #             {"role": "system", "content": msg.prompt + getattr(msg, provider_data["message"])},
            #             {"role": "user", "content": msg.sentence},
            #         ],
            #         "model": model_name,
            #         "temperature": 1,
            #     }
            #     request_func = request_ovh
            # elif provider_name == "targon":
            #     data = {
            #         "model": model_name,
            #         "messages": [{"role": "user", "content": msg.prompt + getattr(msg, provider_data["message"]) + msg.sentence}],
            #         "stream": True,
            #     }
            #     request_func = request_targon_stream
            elif provider_name == "pollination":
                url += msg.prompt + getattr(msg, provider_data["message"]) + msg.sentence
                tasks.append(request_pollination(session, url, timeout))
                continue
            elif provider_name == "dify":
                data = {
                    "inputs": {"userInput": msg.sentence},
                    "response_mode": "blocking",
                    "conversation_id": "",
                    "user": "abc-123",
                    "files": [],
                }
                request_func = request_dify_workflow
            elif provider_name == "vectorshift":
                data = {"inputs": {"input_0": msg.sentence}}
                request_func = request_vectorshift_workflow
            elif provider_data.get("auth_method") == "baidu":
                headers = {"Content-Type": "application/json"}
                data = {
                    "messages": [
                        {"role": "user", "content": msg.prompt + getattr(msg, provider_data["message"]) + msg.sentence}
                    ]
                }
                tasks.append(baidu_request_async(session, url, headers, data, timeout))
                continue
            else:
                data = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": msg.prompt + getattr(msg, provider_data["message"])},
                        {"role": "user", "content": msg.sentence},
                    ],
                }
                request_func = fetch_async

            if request_func:
                tasks.append(request_func(session, url, headers, data, timeout))

        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    response_texts = [result for result in results if isinstance(result, str)]
    
    return remove_think_tags("||".join(response_texts))

@app.get("/")
async def root():
    return {"message": "API is running"}
