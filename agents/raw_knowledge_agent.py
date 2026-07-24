from llm.ollama_client import chat
from utils.logger import get_logger
import yaml

logger = get_logger(__name__)


def raw_summarize(source_id, context):

    prompt = f"""
================================================
你是一名专业的小说知识库工程师。

你的任务：
根据输入的 YMAL 数据，对内部的内容进行整理合并，去掉重复
================================================
下面是输入的数据：
{context}

================================================
目标：
构建 AI 长篇小说生成系统 Knowledge Base。
================================================
【输出要求】
输出 YAML 格式的数据。 重要，重要，重要。
仅仅输出 YAML 格式的数据。 重要，重要，重要。
要求出的的内容 必须能装换为 YAML 数据格式

禁止输出:
- Markdown
- ```yaml
- 解释
- ```
```yaml
```
================================================
"""
    return chat(prompt)
