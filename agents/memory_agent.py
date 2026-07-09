from llm.ollama_client import chat
from utils.logger import get_logger
import json

logger = get_logger(__name__)


class MemoryAgent:

    def __init__(self, context):

        self.context = context

    # ==================================================
    # 生成章节 Memory
    # ==================================================

    def create_chapter_memory(self, chapter_content, chapter_id):

        prompt = f"""

你是一名专业的小说记忆管理助手。

你的任务：
分析下面章节内容。
提取未来写作必须记住的信息。

小说：

{self.context.config["novel"]["title"]}


当前章节：
{chapter_id}

章节正文：

====================

{chapter_content}

====================


JSON格式：

{{
    "chapter_id":"",
    "summary":"",
    "events":[
    ],

    "character_changes":[
        {{
            "name":"",
            "change":""
        }}
    ],

    "new_characters":[
    ],

    "items":[

    ],


    "locations":[

    ],

    "power_changes":[

    ],

    "relationships":[

    ],


    "world_changes":[

    ],


    "future_hooks":[

    ],


    "important_dialogues":[

    ]

}}

注意：
1. 不要创造不存在的信息
2. 不修改已有历史
3. 只记录真实发生内容
4. 重点记录未来剧情需要的信息

要求：
1. 只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据
2. 不要解释
3. 提取未来写作需要的信息
"""

        result = chat(prompt)

        return self.parse_json(result)

    # ==================================================
    # 更新 Plot Memory
    # ==================================================

    def update_plot_memory(self, chapter_memory):

        prompt = f"""

你是一名小说剧情整理助手。

当前 Plot 已经发生以下章节：

{chapter_memory}


请生成 Plot Memory。
用于未来继续写作。
输出 JSON:

{{

"plot_progress":"",
"completed_events":[],
"important_events":[],
"character_growth":[],
"remaining_conflicts":[],
"future_direction":""

}}

要求：
1. 只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据
2. 不要解释
3. 提取未来写作需要的信息
"""

        result = chat(prompt)
        return self.parse_json(result)

    # ==================================================
    # 更新 Arc Memory
    # ==================================================

    def update_arc_memory(self, plot_memories):

        prompt = f"""

你是一名长篇小说编辑。

根据多个 Plot Memory。
生成 Arc Memory。
输入：
{plot_memories}

输出:
{{
"arc_summary":"",

"main_events":[],

"character_changes":[],

"world_changes":[],

"unfinished_threads":[],

"ending_direction":""


}}

要求：
1. 只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据
2. 不要解释
3. 提取未来写作需要的信息

"""
        result = chat(prompt)

        return self.parse_json(result)

    # ==================================================
    # 更新 Volume Memory
    # ==================================================

    def update_volume_memory(self, arc_memories):

        prompt = f"""

你是一名小说总编辑。
根据多个 Arc Memory。
生成 Volume Memory。

输入:
{arc_memories}

输出:

{{

"volume_summary":"",

"main_story_progress":"",

"major_events":[],

"main_character_growth":[],

"world_expansion":[],

"future_setup":[]

}}

要求：
1. 只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据
2. 不要解释
3. 提取未来写作需要的信息
"""

        result = chat(prompt)

        return self.parse_json(result)

    # ==================================================
    # 更新人物 Memory
    # ==================================================

    def update_character_memory(self, chapter_memory):

        prompt = f"""


根据章节记忆。
更新人物状态。
输入：

{chapter_memory}

输出 JSON:

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

要求：
1. 只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据，只输出JSON, 纯JSON数据
2. 不要解释
3. 提取未来写作需要的信息

"""

        result = chat(prompt)

        return self.parse_json(result)

    # ==================================================
    # JSON解析
    # ==================================================

    def parse_json(self, result):
        try:
            return json.loads(result)
        except Exception:

            logger.error("AI输出不是JSON:\n" + result)

            # # 防止模型输出 markdown
            # start = result.find("{")
            # end = result.rfind("}")
            # if start != -1 and end != -1:
            #     return json.loads(result[start : end + 1])
            # raise Exception("AI输出不是JSON:\n" + result)
