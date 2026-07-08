from llm.ollama_client import chat


def summarize_story(context):

    chapters = context.chapter_history

    prompt = f"""


你是一名小说剧情总结助手。

请根据下面章节内容，更新长期剧情记忆。

====================

已有长期总结：

{context.summary}

====================

最近章节：

{chapters}

====================


输出JSON格式:


{{
    
"main_story":"",
    
"important_events":[],
    
"character_changes":[]

}}


"""

    result = chat(prompt)

    return result
