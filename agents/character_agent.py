from llm.ollama_client import chat
from utils.logger import get_logger
import json

logger = get_logger(__name__)


class CharacterAgent:

    def __init__(self, context):

        self.context = context

    # ==================================================
    # 根据章节memory提取人物变化
    #
    # 输出:
    #
    # {
    #   characters:[
    #       {
    #          name:
    #          changes:
    #       }
    #   ]
    # }
    #
    # ==================================================

    def analyze_character_changes(self, chapter_memory):

        prompt = f"""

你是一名小说人物分析专家。


小说:

{self.context.config["novel"]["title"]}



请分析章节记忆。

章节Memory:

{chapter_memory}



提取人物变化。


输出JSON:


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



规则:

1. 只记录真实发生的人物变化

2. 不创造不存在的信息

3. 没有变化的人物不要输出

4. 只输出JSON


"""

        result = chat(prompt)

        return self.parse_json(result)

    # ==================================================
    # 更新人物档案
    #
    # 调用 CharacterManager
    #
    # ==================================================

    def update_characters(self, character_changes):

        from database.character_manager import CharacterManager

        manager = CharacterManager(self.context.root)

        result = []

        for item in character_changes.get("characters", []):

            name = item["name"]

            changes = {k: v for k, v in item.items() if k != "name"}

            character = manager.update_character(name, changes)

            result.append(character)

        return result

    # ==================================================
    # 一次完整更新
    #
    # main调用这个即可
    #
    # ==================================================

    def process(self, chapter_memory):

        changes = self.analyze_character_changes(chapter_memory)

        characters = self.update_characters(changes)

        return characters

    # ==================================================
    # JSON
    # ==================================================

    def parse_json(self, result):

        try:

            return json.loads(result)

        except Exception:

            logger.error("Character AI 输出错误:\n" + result)

            start = result.find("{")
            end = result.rfind("}")

            if start != -1 and end != -1:

                return json.loads(result[start : end + 1])

            raise Exception("无法解析Character JSON")
