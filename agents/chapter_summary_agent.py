from llm.ollama_client import chat
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def summarize_chapter(context, chapter_content, chapter_number):

    prompt = f"""

你是一名小说记忆管理助手。
请分析下面章节。
小说：
{context.config["novel"]["title"]}

章节：
第 {chapter_number} 章

正文：
{chapter_content}

请输出JSON。
格式：
{{
    "chapter": {chapter_number},
    "events":[],
    "character_changes":{{}},
    "new_items":[],
    "power_changes":{{}},
    "important_points":[]
}}


要求：
1. 只输出JSON
2. 不要解释
3. 提取未来写作需要的信息

"""

    result = chat(prompt)

    # logger.info("====================")
    # logger.info("Planner AI output:\n%s", result)
    # logger.info("====================")

    return json.loads(result)
