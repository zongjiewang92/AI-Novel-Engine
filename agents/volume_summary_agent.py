from llm.ollama_client import chat
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def summarize_volume(context):

    prompt = f"""
你是一名长篇小说剧情总监。
小说：
{context.config["novel"]["title"]}

当前卷：
{context.volume}

已有卷总结：
{context.volume_memory}

最近章节摘要：
{context.chapter_memory}

请更新当前卷长期总结。
输出JSON:
格式:
{{
"main_goal":"",
"current_progress":[],
"important_events":[],
"character_changes":{{}},
"future_direction":""
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
