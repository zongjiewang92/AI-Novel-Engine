from llm.ollama_client import chat
import json


class CriticAgent:

    def __init__(self, context):

        self.context = context

    # =====================================================
    # 章节检查
    # =====================================================

    def review_chapter(self, chapter_content):

        prompt = f"""


你是一名资深网络小说编辑。


你的任务：

审核下面章节。


小说：

{self.context.config["novel"]["title"]}



========================
【章节正文】
========================


{chapter_content}




========================
【当前规划 Planning】
========================


Volume:

{self.context.current_plan.get("volume")}



Arc:

{self.context.current_plan.get("arc")}



Plot:

{self.context.current_plan.get("plot")}



Chapter Goal:

{self.context.current_plan.get("chapter")}




========================
【历史 Memory】
========================


Volume Memory:

{self.context.volume_memory}



Arc Memory:

{self.context.arc_memory}



Plot Memory:

{self.context.plot_memory}



Recent Chapter Memory:

{self.context.chapter_memory}




========================
【世界知识】
========================


{self.context.knowledge}




================================================
请检查：
================================================



1.
世界观一致性


检查：

- 力量体系
- 世界规则
- 时间线



2.
剧情规划一致性


检查：

- 是否完成章节目标
- 是否提前完成未来剧情
- 是否偏离Plot



3.
人物一致性


检查：

- 性格
- 行为
- 动机



4.
逻辑问题


检查：

- 不合理行为
- 矛盾
- BUG



5.
阅读质量


检查：

- 是否拖沓
- 是否缺少冲突
- 是否缺少推进




输出 JSON:



{{

"score":0,


"pass":true,


"issues":[

{{

"type":"",
"description":"",
"severity":"low"

}}

],


"world_consistency":"",

"planning_consistency":"",

"character_consistency":"",

"logic_problems":"",


"suggestions":[]


}}



评分：

90-100:
优秀


70-90:
可以发布


50-70:
需要修改


<50:
重新生成



"""

        result = chat(prompt)

        return self.parse_json(result)

    # =====================================================
    # JSON解析
    # =====================================================

    def parse_json(self, result):

        try:

            return json.loads(result)

        except Exception:

            start = result.find("{")

            end = result.rfind("}")

            if start != -1 and end != -1:

                return json.loads(result[start : end + 1])

            raise Exception("Critic输出错误:\n" + result)
