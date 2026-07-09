from database.project_context import ProjectContext

context = ProjectContext("projects/swallowing_star_fanfic")


print("小说:")
print(context.config["novel"]["title"])


print("\n当前章节:")
print(context.novel_state["current_chapter"])


print("\n剧情摘要:")
print(context.story_summary)


print("\n最近章节:")
print(len(context.chapter_history))


print("\n人物:")
print(context.characters)


print("\n世界规则:")
print(context.world_rules)


print("\n当前卷记忆:")
print(context.volume_memory)


print("\n最近章节摘要:")
print(context.chapter_memory)
