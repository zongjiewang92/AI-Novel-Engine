import yaml

from utils.logger import get_logger

logger = get_logger(__name__)


PLANNER_SYSTEM = """

你是一名专业的长篇网络小说策划编辑。


你的任务：

设计长篇网络小说剧情规划。


必须遵守：

1. 尊重已有世界观
2. 尊重力量体系
3. 尊重时间线
4. 保持剧情递进
5. 不提前消耗核心剧情
6. 保留长期伏笔


输出要求：

只输出 YAML。

禁止：

- Markdown
- 解释
- 分析
- 作者说明


"""


class PlannerAgent:

    def __init__(self, context):

        self.context = context

    # =================================================
    # LLM
    # =================================================

    def call_llm(self, prompt):

        result = self.context.llm.chat(
            prompt=prompt,
            system=PLANNER_SYSTEM,
            options={"temperature": 0.5, "num_predict": 3000, "repeat_penalty": 1.1},
        )

        return self.parse_yaml(result)

    # =================================================
    # Volume
    # =================================================

    def create_volume_plan(self):

        logger.info("生成 Volume Planning")

        prompt = f"""

【小说信息】

{self.context.config["novel"]}



【世界规则】

{self.context.global_rules}



【主角状态】

{self.context.novel_state.get("protagonist")}



任务：

设计一个 Volume。


要求：

包含：

- id
- title
- goal
- theme
- main_conflict
- ending



输出格式：


volume:

  id:

  title:

  goal:

  theme:

    -


  main_conflict:


  ending:


"""

        return self.call_llm(prompt)

    # =================================================
    # Arc
    # =================================================

    def create_arc_plan(self, volume_plan):

        logger.info("生成 Arc Planning")

        prompt = f"""


【Volume规划】

{volume_plan}



任务：

设计一个 Arc。


Arc 是 Volume 内连续剧情阶段。


必须包含：

- id
- title
- goal
- conflict
- key_events
- ending



输出：


arc:

  id:

  title:

  goal:

  conflict:


  key_events:

    -


  ending:


"""

        return self.call_llm(prompt)

    # =================================================
    # Plot
    # =================================================

    def create_plot_plan(self, volume_plan, arc_plan):

        logger.info("生成 Plot Planning")

        prompt = f"""


【Volume】

{volume_plan}



【Arc】

{arc_plan}



任务：

设计 Plot。


Plot 是：

几个章节完成的核心剧情事件。


必须包含：


plot:

 id:


 title:


 goal:


 events:

   -


 conflict:


 turning_point:


 ending:



"""

        return self.call_llm(prompt)

    # =================================================
    # Chapter
    # =================================================

    def create_chapter_plan(self, plot_plan):

        logger.info("生成 Chapter Planning")

        prompt = f"""


【Plot】

{plot_plan}



任务：

拆分章节。


一个 Chapter 是实际生成正文单位。


输出：


chapter:

 id:


 goal:


 conflict:


 characters:


 key_events:


 ending:


 scenes:


   - scene_01



"""

        return self.call_llm(prompt)

    # =================================================
    # Scene
    # =================================================

    def create_scene_plan(self, chapter_plan):

        logger.info("生成 Scene Planning")

        prompt = f"""


【Chapter】

{chapter_plan}



任务：

生成 Scene。


Scene 是最小写作单元。


输出：


scene:

 id:


 location:


 characters:


 goal:


 conflict:


 event:


 emotion:


 ending:


"""

        return self.call_llm(prompt)

    # =================================================
    # Full
    # =================================================

    def generate_full_plan(self):

        volume = self.create_volume_plan()

        arc = self.create_arc_plan(volume)

        plot = self.create_plot_plan(volume, arc)

        chapter = self.create_chapter_plan(plot)

        scenes = []

        scene_ids = chapter.get("chapter", {}).get("scenes", [])

        for scene_id in scene_ids:

            scene = self.create_scene_plan(chapter)

            scenes.append(scene)

        return {
            "volume": volume,
            "arc": arc,
            "plot": plot,
            "chapter": chapter,
            "scenes": scenes,
        }

    # =================================================
    # YAML Parser
    # =================================================

    def parse_yaml(self, result):

        try:

            return yaml.safe_load(result)

        except Exception:

            logger.error("Planner YAML解析失败:\n%s", result)

            start = result.find("volume:")

            if start != -1:

                try:

                    return yaml.safe_load(result[start:])

                except:

                    pass

            raise ValueError("Planner输出无法解析")
