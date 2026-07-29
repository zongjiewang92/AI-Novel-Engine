from utils.logger import get_logger

logger = get_logger(__name__)


WRITER_SYSTEM = """
你是一名专业的长篇网络小说作者。

你的任务是持续创作一部长篇连载小说。

必须遵守以下原则：

1. 尊重已经建立的世界观
2. 尊重已有剧情历史
3. 保持人物性格一致
4. 保持力量体系一致
5. 不随意创造新的规则
6. 不为了剧情爽感破坏逻辑
7. 保持剧情方向
8. 保持剧情连贯
9. 避免重复写之前的剧情
10. 保留伏笔

写作目标：

创造具有商业网络小说质量的章节正文。

你的输出永远只包含小说正文。
禁止输出：
- 分析
- 解释
- 作者说明
- 创作过程
"""


def write_chapter(context):

    # ==================================================
    # Input Check
    # ==================================================
    check_inputs = {
        "current_plot": context.current_plot,
        "before_plots": context.before_plots,
        "after_plots": context.after_plots,
    }

    for name, value in check_inputs.items():
        if not value:
            logger.warning("Writer input is empty: %s", name)

    # length
    for name, value in check_inputs.items():
        length = len(str(value)) if value else 0
        logger.info("Writer input length: %s = %d chars", name, length)

    # current_plot is empty exit
    if not context.current_plot:
        logger.error(
            "current_plot is empty, do exit. : %s",
            context.chapter_id,
        )
        raise ValueError("current_plot is empty, can not generate chapter.")

    prompt = f"""

【当前章节剧情】
{context.current_plot}


【输出要求】

生成 当前章节 正文。
- 保持剧情方向
- 保持剧情连贯
要求：
4000字。

"""
    logger.info(
        "Writer Prompt长度: %d chars (%.2f KB)",
        len(prompt),
        len(prompt.encode("utf-8")) / 1024,
    )
    return context.llm.chat(
        prompt=prompt,
        system=WRITER_SYSTEM,
        options={"temperature": 0.8, "num_predict": 6000, "repeat_penalty": 1.1},
    )
