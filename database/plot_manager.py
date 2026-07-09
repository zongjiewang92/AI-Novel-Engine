class PlotManager:

    @staticmethod
    def get_current_plot(plan, chapter):
        for item in plan.get("chapters", []):
            start, end = item["range"].split("-")
            if int(start) <= chapter <= int(end):
                return item

        return {}
