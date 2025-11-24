import logging, traceback
logging.basicConfig(level=logging.INFO)

def self_heal(msg):
    logging.warning(f"[SELF-HEAL] {msg}")

def auto_retry(task, retries=3):
    for i in range(retries):
        try: return task()
        except Exception as e:
            self_heal(f"Retry {i+1} failed: {e}")
    return "(Deterministic fallback)"
