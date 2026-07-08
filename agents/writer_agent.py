from llm.ollama_client import chat


def write_chapter(context):

    novel_title = context.config["novel"]["title"]

    volume = context.volume

    current_chapter = context.state["current_chapter"]

    protagonist = context.state["protagonist"]

    # ==========================
    # 小说上下文
    # ==========================

    summary = context.summary

    characters = context.characters

    world_rules = context.world_rules

    timeline = context.timeline

    chapter_history = context.chapter_history

    prompt = f"""


你是一名专业的网络小说作者。


你的任务：

继续创作《{novel_title}》下一章节。



====================
【最高优先级：世界规则】
====================


以下规则必须遵守：

{world_rules}



====================
【长期剧情记忆】
====================


这是小说已经发生的大事件：

{summary}



====================
【人物设定】
====================


人物资料：

{characters}



====================
【时间线】
====================


当前故事时间：

{timeline}



====================
【最近剧情】
====================


以下是最近章节内容：

{chapter_history}



====================
【当前主角状态】
====================


姓名：

{protagonist["name"]}


境界：

{protagonist["level"]}


位置：

{protagonist["location"]}


能力：

{protagonist["abilities"]}



====================

现在开始创作：

第 {current_chapter} 章。



要求：

1. 延续之前剧情，不要重新开始

2. 保持《吞噬星空》世界力量体系

3. 不修改已有历史事件

4. 人物行为符合设定

5. 有战斗、对白、环境描写

6. 推动剧情发展

7. 正文字数不少于100字


"""

    return chat(prompt)
