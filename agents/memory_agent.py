import json

from utils.logger import get_logger

logger = get_logger(__name__)
MEMORY_SYSTEM = """
你是一名专业的长篇网络小说记忆管理助手。

你的职责不是创作小说，而是整理小说记忆。

你的目标：

将正文压缩成未来继续创作必须依赖的信息。

请遵守以下原则：

1. 不创造不存在的信息
2. 不推测未来剧情
3. 不修改历史
4. 只记录真实发生内容
5. 删除无关细节
6. 保留未来剧情必须依赖的信息
7. 保持输出稳定
8. 保持信息完整
9. 保持 JSON 格式正确

你的输出永远只包含 JSON。

禁止输出：

- Markdown
- 解释
- 分析
- 推理过程
- 作者说明
"""


class MemoryAgent:

    def __init__(self, context):

        self.context = context

    # ==================================================
    # Create Chapter Memory
    # ==================================================

    def create_chapter_memory(self, chapter_content, chapter_id):

        prompt = f"""
【章节编号】

{chapter_id}


==================================================
【章节正文】
==================================================

{chapter_content}


==================================================
【任务】
==================================================

提取未来继续创作必须保留的信息。

重点包括：

1. 本章概要
2. 关键事件
3. 人物变化
4. 新出现人物
5. 新物品
6. 新地点
7. 力量变化
8. 人物关系变化
9. 世界变化
10. 后续伏笔


==================================================
【输出格式】
==================================================

{{
    "chapter_id":"",
    "summary":"",
    "events":[],
    "character_changes":[],
    "new_characters":[],
    "items":[],
    "locations":[],
    "power_changes":[],
    "relationships":[],
    "world_changes":[],
    "future_hooks":[],
    "important_dialogues":[]
}}
"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=MEMORY_SYSTEM,
            options={
                "temperature": 0.1,
                "num_predict": 1200,
            },
        )

        return self.parse_json(result)

    # ==================================================
    # Update Plot Memory
    # ==================================================

    def update_plot_memory(self, chapter_memories):

        prompt = f"""
【输入】

下面是当前 Plot 的所有 Chapter Memory。

{chapter_memories}


==================================================
【任务】
==================================================

整理整个 Plot 的长期记忆。

重点：

1. Plot 当前进度
2. 已完成事件
3. 最重要事件
4. 人物成长
5. 尚未解决冲突
6. 下一阶段方向


==================================================
【输出格式】
==================================================

{{
    "plot_progress":"",
    "completed_events":[],
    "important_events":[],
    "character_growth":[],
    "remaining_conflicts":[],
    "future_direction":""
}}
"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=MEMORY_SYSTEM,
            options={
                "temperature": 0.1,
                "num_predict": 1000,
            },
        )

        return self.parse_json(result)

    # ==================================================
    # Update Arc Memory
    # ==================================================

    def update_arc_memory(self, plot_memories):

        prompt = f"""
【输入】

下面是当前 Arc 的所有 Plot Memory。

{plot_memories}


==================================================
【任务】
==================================================

整理整个 Arc 的长期记忆。

==================================================
【输出格式】
==================================================

{{
    "arc_summary":"",
    "main_events":[],
    "character_changes":[],
    "world_changes":[],
    "unfinished_threads":[],
    "ending_direction":""
}}
"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=MEMORY_SYSTEM,
            options={
                "temperature": 0.1,
                "num_predict": 1000,
            },
        )

        return self.parse_json(result)

    # ==================================================
    # Update Volume Memory
    # ==================================================

    def update_volume_memory(self, arc_memories):

        prompt = f"""
【输入】

下面是当前 Volume 的所有 Arc Memory。

{arc_memories}


==================================================
【任务】
==================================================

整理整个 Volume 的长期记忆。

==================================================
【输出格式】
==================================================

{{
    "volume_summary":"",
    "main_story_progress":"",
    "major_events":[],
    "main_character_growth":[],
    "world_expansion":[],
    "future_setup":[]
}}
"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=MEMORY_SYSTEM,
            options={
                "temperature": 0.1,
                "num_predict": 1000,
            },
        )

        return self.parse_json(result)

    # ==================================================
    # Update Character Memory
    # ==================================================

    def update_character_memory(self, chapter_memory):

        prompt = f"""
【输入】

Chapter Memory：

{chapter_memory}


==================================================
【任务】
==================================================

更新人物长期状态。


==================================================
【输出格式】
==================================================

{{
    "characters":[
        {{
            "name":"",
            "status":"",
            "personality_change":"",
            "new_abilities":[],
            "relationships":[]
        }}
    ]
}}
"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=MEMORY_SYSTEM,
            options={
                "temperature": 0.1,
                "num_predict": 1000,
            },
        )

        return self.parse_json(result)

    # ==================================================
    # Parse JSON
    # ==================================================

    def parse_json(self, result):

        try:
            return json.loads(result)

        except Exception:

            logger.error("AI 输出不是 JSON：\n%s", result)

            start = result.find("{")
            end = result.rfind("}")

            if start != -1 and end != -1:
                try:
                    return json.loads(result[start : end + 1])
                except Exception:
                    pass

            raise ValueError("MemoryAgent 输出 JSON 解析失败。")
