import json
import os
from cryptography.fernet import Fernet

MEMORY_FILE = "sounix_memory.json"
KEY_FILE = os.path.expanduser("~/.sounix_key")

ENC_PREFIX = "ENC:"


def _get_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "rb") as f:
            return f.read()

    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    os.chmod(KEY_FILE, 0o600)
    return key


_fernet = Fernet(_get_key())


def _encrypt(value):
    serialized = json.dumps(value)
    token = _fernet.encrypt(serialized.encode("utf-8")).decode("utf-8")
    return ENC_PREFIX + token


def _decrypt(value):
    token = value[len(ENC_PREFIX):]
    serialized = _fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    return json.loads(serialized)


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def remember(key, value):
    memory = load_memory()
    memory[key] = _encrypt(value)
    save_memory(memory)


def recall(key):
    memory = load_memory()
    raw = memory.get(key, None)
    if raw is None:
        return None
    if isinstance(raw, str) and raw.startswith(ENC_PREFIX):
        try:
            return _decrypt(raw)
        except Exception as e:
            return f"[decrypt error: {e}]"
    return raw


def forget(key):
    memory = load_memory()
    if key in memory:
        del memory[key]
        save_memory(memory)


def list_memories():
    memory = load_memory()
    result = {}
    for key, raw in memory.items():
        if isinstance(raw, str) and raw.startswith(ENC_PREFIX):
            try:
                result[key] = _decrypt(raw)
            except Exception as e:
                result[key] = f"[decrypt error: {e}]"
        else:
            result[key] = raw
    return result
