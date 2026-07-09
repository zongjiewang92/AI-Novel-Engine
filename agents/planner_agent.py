from llm.ollama_client import chat
import yaml
import json


class PlannerAgent:

    def __init__(self, context):

        self.context = context

    # =================================================
    # Volume Planning
    # =================================================

    def create_volume_plan(self):

        prompt = f"""

你是一名资深网络小说总策划。

请为小说创建 Volume（卷）级剧情规划。


小说:

{self.context.config["novel"]}



世界背景:

{self.context.knowledge}



主角:

{self.context.novel_state["protagonist"]}



要求：

生成一个长期剧情 Volume。


必须包含：

- volume id
- name
- goal
- theme
- main_conflict
- ending


输出 YAML。



格式:


volume:

  id: volume001

  name:


  goal:


  theme:

    -


  main_conflict:


  ending:


"""

        result = chat(prompt)

        return yaml.safe_load(result)

    # =================================================
    # Arc Planning
    # =================================================

    def create_arc_plan(self, volume_plan):

        prompt = f"""


你是一名网络小说剧情设计师。


根据 Volume 规划生成 Arc。


Volume:

{volume_plan}



要求：

Arc 是一个连续剧情阶段。


必须包含：

- arc id
- name
- goal
- conflict
- key_events
- ending


输出 YAML。


格式：


arc:

 id: arc001


 name:


 goal:


 conflict:


 key_events:

   -


 ending:


"""

        result = chat(prompt)

        return yaml.safe_load(result)

    # =================================================
    # Plot Planning
    # =================================================

    def create_plot_plan(self, volume_plan, arc_plan):

        prompt = f"""


你是一名小说剧情规划师。


根据：

Volume:

{volume_plan}


Arc:

{arc_plan}



生成 Plot。


Plot 是几个章节完成的关键事件。


必须包含：


plot:

 id:


 name:


 goal:


 events:


   -


 conflict:


 turning_point:


 ending:



输出 YAML。


"""

        result = chat(prompt)

        return yaml.safe_load(result)

    # =================================================
    # Chapter Planning
    # =================================================

    def create_chapter_plan(self, plot_plan):

        prompt = f"""


你是一名章节规划专家。


根据 Plot：

{plot_plan}



拆分章节。


生成一个章节规划。


要求：


chapter:


 id:


 goal:


 conflict:


 characters:


 key_events:


 ending:


 scenes:


   - scene01

   - scene02



输出 YAML。


"""

        result = chat(prompt)

        return yaml.safe_load(result)

    # =================================================
    # Scene Planning
    # =================================================

    def create_scene_plan(self, chapter_plan):

        prompt = f"""


你是一名网文分镜设计师。


根据章节：

{chapter_plan}



生成 Scene。


Scene 是实际写作的小单元。


每个 Scene 必须包含：


scene:

 id:


 location:


 characters:


 goal:


 conflict:


 event:


 emotion:


 ending:


输出 YAML。


"""

        result = chat(prompt)

        return yaml.safe_load(result)

    # =================================================
    # Full Pipeline
    # =================================================

    def generate_full_plan(self):

        volume = self.create_volume_plan()

        arc = self.create_arc_plan(volume)

        plot = self.create_plot_plan(volume, arc)

        chapter = self.create_chapter_plan(plot)

        scenes = []

        for scene_id in chapter["chapter"]["scenes"]:

            scene = self.create_scene_plan(chapter)

            scenes.append(scene)

        return {
            "volume": volume,
            "arc": arc,
            "plot": plot,
            "chapter": chapter,
            "scenes": scenes,
        }
