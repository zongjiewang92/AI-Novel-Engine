from llm.ollama_client import chat
import json


def create_plot_plan(context):

    prompt = f"""

你是一名长篇小说剧情策划。


小说：

{context.config["novel"]["title"]}


当前卷：

{context.volume}


已有剧情总结：

{context.summary}


当前卷总结：

{context.volume_memory}


人物状态：

{context.characters}



请设计未来剧情。


输出JSON:


{{
"volume_goal":"",

"main_conflict":"",

"chapters":[

    {{
    "range":"",
    "goal":"",
    "events":[]
    }}

]

}}

"""

    result = chat(prompt)

    return json.loads(result)
