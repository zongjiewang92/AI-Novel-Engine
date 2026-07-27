from pathlib import Path
from collections import defaultdict
import yaml
import re
from datetime import datetime

def load_yaml(file: Path):
    text = file.read_text(encoding="utf-8").strip()

    if text.startswith("```yaml"):
        text = text[len("```yaml"):]

    elif text.startswith("```"):
        text = text[len("```"):]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    if not text:
        return {}

    return yaml.safe_load(text) or {}





def load_text(file: Path):

    with open(file, "r", encoding="utf-8") as f:

        return f.read()


        
def save_text(file: Path, content):
    

    with open(file, "w", encoding="utf-8") as f:

        f.write(content)
    return file




