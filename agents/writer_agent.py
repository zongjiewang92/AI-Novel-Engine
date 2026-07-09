from llm.ollama_client import chat


def write_chapter(context):

    novel_title = context.config["novel"]["title"]

    volume = context.volume

    current_chapter = context.novel_state["current_chapter"]

    protagonist = context.novel_state["protagonist"]

    # ==========================
    # 小说上下文
    # ==========================

    summary = context.story_summary

    volume_memory = context.volume_memory

    chapter_memory = context.chapter_memory

    current_plot = context.current_plot

    characters = context.characters

    world_rules = context.world_rules

    timeline = context.timeline

    chapter_history = context.chapter_history

    prompt = f"""

你是一名专业的网络小说作者。


你的任务：

继续创作：

《{novel_title}》



====================
【当前卷信息】
====================


当前卷：

{volume}



当前卷长期目标：

{volume_memory}


====================
【未来剧情规划】
====================


当前卷未来剧情方向：

{current_plot}



写作要求：

1. 当前章节必须服务于未来剧情目标

2. 不提前完成后续剧情

3. 保留伏笔

4. 不改变规划中的核心事件


====================
【世界规则】
====================


以下规则必须严格遵守：

{world_rules}



====================
【整个小说长期记忆】
====================


已经发生的重要事件：

{summary}



====================
【最近章节摘要】
====================


注意：

以下是最近章节发生的事情。

不要重复。

不要修改。


{chapter_memory}



====================
【人物资料】
====================


角色设定：

{characters}



====================
【故事时间线】
====================


当前时间线：

{timeline}



====================
【最近章节正文】
====================


以下内容用于保持文风和剧情连续：

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

第 {current_chapter} 章



要求：

1. 必须承接上一章

2. 不允许重置剧情

3. 不允许改变已有事件

4. 遵守《吞噬星空》力量体系

5. 人物行为符合角色设定

6. 推进当前卷主线目标

7. 有：
   - 环境描写
   - 人物对白
   - 剧情冲突
   - 战斗或事件推进

8. 正文字数不少于100字


"""

    return chat(prompt)
