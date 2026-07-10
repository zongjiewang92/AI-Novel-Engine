from llm.ollama_client import chat



def extract_knowledge(
        source_id,
        text
):


    prompt = f"""

你是一名专业的小说知识库工程师。


你的任务：

阅读小说原文。

提取所有具有长期价值的世界知识。


目标：

构建 AI 长篇小说生成系统 Knowledge Base。


================================================

小说：

《吞噬星空》


来源:

{source_id}


================================================


【抽取原则】

1.

只提取原文明确出现的信息。


2.

禁止编造。


3.

禁止推测。


4.

保持原著设定。


5.

保留上下文关系。


6.

不要总结剧情。


7.

不要写评论。



================================================

【需要发现的知识类型】

根据文本自动判断。


包括但不限于：



## Character 人物

例如:

- 姓名
- 身份
- 年龄
- 实力
- 性格
- 能力
- 关系



## Location 地点

例如:

- 星球
- 城市
- 秘境
- 遗迹
- 战场



## Civilization 文明

例如:

- 人类文明
- 虫族文明
- 机械族文明



## Species 种族

例如:

- 人类
- 金角巨兽
- 星空巨兽



## Organization 组织

例如:

- 公司
- 家族
- 学院
- 国家



## Cultivation 修炼体系

例如:

- 等级
- 境界
- 突破条件



## Ability 能力

例如:

- 天赋
- 秘法
- 技能



## Item 物品

例如:

- 武器
- 宝物
- 装备



## Event 事件

例如:

- 战争
- 战斗
- 历史事件
- 转折事件



## Relationship 关系

例如:

人物之间关系变化。



## Dialogue 对话

保存：

具有代表性的关键对白。



## Timeline 时间线

记录：

发生时间和顺序。



## Mystery 伏笔

记录：

未解决信息。



================================================


【输出要求】

输出 YAML。


禁止:

- Markdown
- ```yaml
- 解释


================================================


格式:


source:

  id:


entities:


  - id:

    type:

    name:


    aliases:


    description:


    attributes:


relationships:


events:


dialogues:


timeline:


mysteries:



================================================


原文:


{text}


"""


    return chat(prompt)