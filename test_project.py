from database.project_manager import ProjectManager

project = ProjectManager("swallowing_star_fanfic")


config = project.load_config()


print(config)

print(project.get_path("chapters"))
