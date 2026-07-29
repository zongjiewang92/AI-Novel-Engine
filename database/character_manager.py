from pathlib import Path
import yaml


class CharacterManager:

    def __init__(self, project_root):

        self.root = Path(project_root)

        self.character_root = self.root / "z_ai_memory" / "characters"

        self.character_root.mkdir(parents=True, exist_ok=True)

    # ==================================================
    # path
    # ==================================================

    def character_path(self, name):

        filename = name.replace(" ", "_") + ".yaml"

        return self.character_root / filename

    # ==================================================
    # load
    # ==================================================

    def load_character(self, name):
        file = self.character_path(name)
        if not file.exists():
            return {}
        with open(file, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    # ==================================================
    # save
    # ==================================================

    def save_character(self, name, data):

        file = self.character_path(name)

        with open(file, "w", encoding="utf-8") as f:

            yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    # ==================================================
    # update
    #
    # 合并人物变化
    #
    # ==================================================

    def update_character(self, name, changes):

        character = self.load_character(name)

        if not character:

            character = {
                "name": name,
                "basic": {},
                "personality": [],
                "realm": {},
                "abilities": [],
                "relationships": {},
                "growth_history": [],
            }

        # --------------------------
        # 当前状态
        # --------------------------

        for key, value in changes.items():

            if key in ["personality", "abilities"]:

                old = character.get(key, [])

                for item in value:

                    if item not in old:

                        old.append(item)

                character[key] = old

            else:

                character[key] = value

        # --------------------------
        # 历史记录
        # --------------------------

        character["growth_history"].append(changes)

        self.save_character(name, character)

        return character

    # ==================================================
    # batch update
    #
    # MemoryAgent 输出:
    #
    # [
    # {
    # name:
    # change:
    # }
    # ]
    #
    # ==================================================

    def update_from_memory(self, character_memory):

        result = []

        characters = character_memory.get("characters", [])

        for item in characters:

            name = item["name"]

            updated = self.update_character(name, item)

            result.append(updated)

        return result
