import json

from utils.logger import get_logger

logger = get_logger(__name__)
CHARACTER_SYSTEM = """

你是一名专业的小说人物档案管理助手。


你的任务：

根据章节 Memory 更新人物状态。


原则：

1. 只记录真实发生的信息

2. 不创造人物经历

3. 不推测未来

4. 不修改历史

5. 只记录长期人物状态变化

6. 没有变化的人物不要输出


输出：

只输出 JSON。


禁止：

- Markdown
- 解释
- 分析
- 作者说明

"""


class CharacterAgent:

    def __init__(self, context):

        self.context = context

    # ==================================================
    # 分析人物变化
    #
    # input:
    #
    # chapter_memory
    #
    # output:
    #
    # {
    #   characters:[]
    # }
    #
    # ==================================================

    def analyze(self, chapter_memory):

        prompt = f"""
【章节 Memory】

{chapter_memory}



==================================================
【任务】
==================================================


分析本章发生的人物变化。


只提取：

1. 状态变化

2. 境界变化

3. 新能力

4. 性格变化

5. 关系变化

6. 重要事件


注意：

没有变化的人物不要输出。


==================================================
【输出格式】
==================================================


{{
    "characters":[

        {{
            "name":"",

            "status_change":"",

            "realm_change":"",

            "new_abilities":[],

            "personality_change":[],

            "relationship_change":[],

            "important_events":[]

        }}

    ]
}}

"""

        result = self.context.llm.chat(
            prompt=prompt,
            system=CHARACTER_SYSTEM,
            options={"temperature": 0.1, "num_predict": 1000},
        )

        return self.parse_json(result)

    # ==================================================
    # 更新人物数据库
    # ==================================================

    def update(self, character_changes):

        from database.character_manager import CharacterManager

        manager = CharacterManager(self.context.root)

        result = []

        for character in character_changes.get("characters", []):

            name = character.get("name")

            if not name:

                continue

            changes = {k: v for k, v in character.items() if k != "name"}

            updated = manager.update_character(name, changes)

            result.append(updated)

        return result

    # ==================================================
    # Pipeline
    # ==================================================

    def process(self, chapter_memory):

        changes = self.analyze(chapter_memory)

        if not changes:

            return []

        return self.update(changes)

    # ==================================================
    # JSON Parser
    # ==================================================

    def parse_json(self, result):

        try:

            return json.loads(result)

        except Exception:

            logger.error("CharacterAgent JSON错误:\n%s", result)

            start = result.find("{")

            end = result.rfind("}")

            if start != -1 and end != -1:

                try:

                    return json.loads(result[start : end + 1])

                except Exception:

                    pass

            raise ValueError("CharacterAgent 输出无法解析")
