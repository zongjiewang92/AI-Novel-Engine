from llm.ollama_client import chat
from utils.logger import get_logger
import json

logger = get_logger(__name__)


def create_plot_plan(context):

    prompt = f"""

你是一名长篇小说剧情策划。
小说：
{context.config["novel"]["title"]}

当前卷：
{context.volume}

已有剧情总结：
{context.story_summary}

当前卷总结：
{context.volume_memory}

人物状态：
{context.characters}

请设计未来剧情。
输出JSON:
格式:
{{
"volume_goal":"",
"main_conflict":"",
"chapters":[
    {{
    "range":"",
    "goal":"",
    "events":[]
    }}]
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
