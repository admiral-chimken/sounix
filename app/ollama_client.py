import subprocess
import urllib.request
import json

DEFAULT_MODEL = "qwen2.5:1.5b"

SYSTEM_PROMPT = (
    "You are Sounix, a cybersecurity-focused AI assistant. "
    "You were created by admiralchimken with the help of multiple AI models. "
    "Do not mention Alibaba Cloud, Qwen, or any other company as your creator or origin. "
    "If asked who made you, say you were made by admiralchimken with the help of multiple AI models."
)
def ask_ollama(prompt, model=DEFAULT_MODEL):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "system": SYSTEM_PROMPT,
        "stream": False
    }
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
         
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return f"Sounix: {result.get('response', '').strip()}"

    except urllib.error.URLError:
        return "Sounix: ollama service isn't running"
    except Exception as e:
        return f"Sounix: error occurred: {str(e)}"

def get_installed_models():
    url = "http://localhost:11434/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            return [m['name'] for m in data.get('models', [])]
    except Exception:
        return [DEFAULT_MODEL]
