from pathlib import Path
import json
import yaml

from database.project_manager import ProjectManager
from utils.file import load_text, save_text

PROJECT_NAME = "swallowing_star_fanfic"


def main():

    project = ProjectManager("swallowing_star_fanfic")
    
    


    input_dir = project.root / "knowledge_ai" / "raw_timeline"

    output_dir = project.root / "knowledge_ai" / "output"/ "timeline.yaml"

    


    yaml_files = list(input_dir.rglob("*.yaml"))

    time_line = ""

    for file in yaml_files:

        data = load_text(file)

        time_line += data


    save_text(output_dir, time_line)

   

if __name__ == "__main__":

    main()
