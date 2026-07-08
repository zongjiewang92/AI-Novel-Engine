from llm.ollama_client import chat
import json


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


{{
"main_goal":"",

"current_progress":[],

"important_events":[],

"character_changes":{{}},

"future_direction":""

}}


"""

    result = chat(prompt)

    return json.loads(result)
