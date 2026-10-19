"""剧情规划 agent：输出 JSON，带自修复的容错解析。走 plan 任务路由。"""
import json

from llm import provider
from llm.json_utils import parse_json_with_repair
from utils.prompt_loader import render_prompt
from utils.logger import get_logger

logger = get_logger(__name__)

TASK = "plan"


def create_plot_plan(context):
    volume_cfg = context.volume.get("volume", {})
    volume_line = f"{volume_cfg.get('name', '')}（第 {volume_cfg.get('id', '?')} 卷）"
    prompt = render_prompt(
        "planner",
        novel_title=context.config["novel"]["title"],
        volume_line=volume_line,
        story_summary=json.dumps(context.story_summary, ensure_ascii=False, indent=2),
        volume_memory=json.dumps(context.volume_memory, ensure_ascii=False, indent=2),
        characters=json.dumps(context.characters, ensure_ascii=False, indent=2),
    )
    result = provider.chat(TASK, prompt, context.config)
    return parse_json_with_repair(
        result, lambda p: provider.chat(TASK, p, context.config))
