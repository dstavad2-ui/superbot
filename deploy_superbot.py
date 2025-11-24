#!/usr/bin/env python3
import shutil, subprocess, logging, os
from pathlib import Path

logging.basicConfig(level=logging.INFO)

SOURCE_DIR = Path(".")
DEPLOY_DIR = Path("/opt/render/project/src/superbot")
REQUIREMENTS_FILE = SOURCE_DIR / "requirements.txt"

def self_heal(msg):
    logging.warning(f"[SELF-HEAL] {msg}")

def copy_files():
    try:
        if DEPLOY_DIR.exists():
            shutil.rmtree(DEPLOY_DIR)
        shutil.copytree(SOURCE_DIR, DEPLOY_DIR)
        logging.info("[SELF-HEAL] Files copied to Render deployment folder")
    except Exception as e:
        self_heal(f"Copy failed: {e}")

def install_requirements():
    try:
        subprocess.run(["pip", "install", "-r", str(REQUIREMENTS_FILE)], check=True)
    except Exception as e:
        self_heal(f"Initial install failed: {e}")
        subprocess.run(["pip", "install", "Pillow>=10.2.0"], check=True)
        subprocess.run(["pip", "install", "-r", str(REQUIREMENTS_FILE)], check=True)

def start_bot():
    try:
        subprocess.run(["python", str(DEPLOY_DIR / "bot.py")], check=True)
    except Exception as e:
        self_heal(f"Bot failed to start: {e}")

def main():
    logging.info("[SELF-HEAL] Starting full deployment")
    copy_files()
    install_requirements()
    start_bot()
    logging.info("[SELF-HEAL] Deployment complete, bot live!")

if __name__ == "__main__":
    main()
