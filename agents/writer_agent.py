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
    # =====================================
    # Planning
    # =====================================
    plan = context.current_plan
    before_plots = plan.get("before_plots", {})
    current_plot = plan.get("current_plot", {})
    after_plots = plan.get("after_plots", {})

    chapter_prompt = f"""

【当前章节剧情】
{context.current_plot}


【上一章的剧情】
{context.before_plots}

【下一章的剧情】
{context.after_plots}


【输出要求】

生成 当前章节 正文。

要求：

3500-4500中文字。

"""

    return context.llm.chat(
        prompt=chapter_prompt,
        system=WRITER_SYSTEM,
        options={"temperature": 0.8, "num_predict": 3000, "repeat_penalty": 1.1},
    )
