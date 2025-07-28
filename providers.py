from config import settings

# A dictionary of all providers, with their API endpoint, model, and message
# The key is the provider name, and the value is a dictionary of its settings
PROVIDERS = {
    "baidu": {
        "url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-128k",
        "auth_method": "baidu",
        "model": "modelBaidu",
        "message": "messageBaidu",
    },
    "big": {
        "url": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "key": settings.BIG_API_KEY,
        "model": "modelBig",
        "message": "messageBig",
    },
    "groq": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "key": settings.GROQ_API_KEY,
        "model": "modelGroq",
        "message": "messageGroq",
    },
    "mistral": {
        "url": "https://api.mistral.ai/v1/chat/completions",
        "key": settings.MISTRAL_API_KEY,
        "model": "modelMistral",
        "message": "messageMistral",
    },
    "together": {
        "url": "https://api.together.xyz/v1/chat/completions",
        "key": settings.TOGETHER_API_KEY,
        "model": "modelTogether",
        "message": "messageTogether",
    },
    "gemini_openai": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        "key": settings.GEMINI_API_KEY,
        "model": "modelGemini",
        "message": "messageGemini",
    },
    "openai_azure": {
        "url": "https://models.inference.ai.azure.com/chat/completions",
        "key": settings.OPENAI_API_KEY,
        "model": "modelOpenAi",
        "message": "messageOpenAi",
    },
    "openrouter": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key": settings.OPENROUTER_API_KEY,
        "model": "modelOpenRouter",
        "message": "messageOpenRouter",
    },
    "chutes": {
        "url": "https://chutes-{model}.chutes.ai/v1/chat/completions",
        "key": settings.CHUTES_API_KEY,
        "model": "modelChutes",
        "message": "messageChutes",
    },
    "cohere": {
        "url": "https://api.cohere.com/v2/chat",
        "key": settings.COHERE_API_KEY,
        "model": "modelCohere",
        "message": "messageCohere",
    },
    "cloudflare": {
        "url": "https://api.cloudflare.com/client/v4/accounts/53a4ab7d625890920e433def35a30c59/ai/run/@cf/",
        "key": settings.CF_API_KEY,
        "model": "modelCF",
        "message": "messageCF",
    },
    "ovh": {
        "url": "https://{model}.endpoints.kepler.ai.cloud.ovh.net/api/openai_compat/v1/chat/completions",
        "key": settings.OVH_API_KEY,
        "model": "modelOVH",
        "message": "messageOVH",
    },
    "targon": {
        "url": "https://api.targon.com/v1/chat/completions",
        "key": settings.TARGON_API_KEY,
        "model": "modelTargon",
        "message": "messageTargon",
    },
    "pollination": {
        "url": "https://text.pollinations.ai/",
        "model": "modelPollination",
        "message": "messagePollination",
    },
    "dify": {
        "url": "https://api.dify.ai/v1/workflows/run",
        "key": settings.DIFY_API_KEY,
    },
    "vectorshift": {
        "url": "https://api.vectorshift.ai/v1/pipeline/67bf6cfa207790ac67e917d0/run",
        "key": settings.FLOW_API_KEY,
    },
        "free": {
        "url": "https://free.v36.cm/v1/chat/completions",
        "key": settings.FREE_API_KEY,
        "model": "modelFree",
        "message": "messageFree",
    },
    "chatanywhere": {
        "url": "https://api.chatanywhere.org/v1/chat/completions",
        "key": settings.ANYWHERE_API_KEY,
        "model": "modelAnywhere",
        "message": "messageAnywhere",
    },
    "cerebras": {
        "url": "https://api.cerebras.ai/v1/chat/completions",
        "key": settings.CEREBRAS_API_KEY,
        "model": "modelCerebras",
        "message": "messageCerebras",
    },
    "fastgpt": {
        "url": "https://cloud.fastgpt.cn/api/v1/chat/completions",
        "key": settings.FASTGPT_API_KEY,
        "model": "modelFastGPT",
        "message": "messageFastGPT",
    },    
    "siliconflow": {
        "url": "https://api.siliconflow.cn/v1/chat/completions",
        "key": settings.SILICONFLOW_API_KEY,
        "model": "modelSiliconFlow",
        "message": "messageSiliconFlow",
    },        
    "infini": {
        "url": "https://internlm-chat.intern-ai.org.cn/puyu/api/v1/chat/completions",
        "key": settings.INFINI_API_KEY,
        "model": "modelInfini",
        "message": "messageInfini",
    },   
    "internlm": {
        "url": "https://internlm-chat.intern-ai.org.cn/puyu/api/v1/chat/completions",
        "key": settings.INTERNLM_API_KEY,
        "model": "modelInternlm",
        "message": "messageInternlm",
    },
    "scope": {
        "url": "https://api-inference.modelscope.cn/v1/chat/completions",
        "key": settings.SCOPE_API_KEY,
        "model": "modelScope",
        "message": "messageScope",
    },               
    "huggingface": {
        "url": "https://router.huggingface.co/featherless-ai/v1/chat/completions",
        "key": settings.HUGGINGFACE_API_KEY,
        "model": "modelHuggingface",
        "message": "messageHuggingface",
    }, 
}
