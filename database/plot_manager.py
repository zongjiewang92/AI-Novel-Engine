class PlotManager:

    @staticmethod
    def get_current_plot(context):
        plan = context.plot_plan
        chapter = context.state["current_chapter"]

        for item in plan.get("chapters", []):
            start, end = item["range"].split("-")
            if int(start) <= chapter <= int(end):
                return item

        return {}
