class PlotManager:

    @staticmethod
    def get_current_plot(plan, chapter):
        """根据章节号找到当前剧情段。range 解析失败时跳过该段（LLM 输出不总是规范）。"""
        for item in (plan or {}).get("chapters", []):
            try:
                start, end = str(item.get("range", "")).split("-")
                if int(start) <= int(chapter) <= int(end):
                    return item
            except (ValueError, AttributeError):
                continue
        return {}
