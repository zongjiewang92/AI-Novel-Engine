"""World Bible：结构化世界观圣经。

百万字长篇翻车 90% 是吃书和烂尾伏笔。bible/ 目录用 YAML 存：
- characters.yaml    人物（含人物弧光 arc）
- factions.yaml      势力
- power_system.yaml  力量体系（有序境界 + 硬规则）
- timeline.yaml      时间线
- locations.yaml     地点
- foreshadowing.yaml 伏笔登记簿（种下/回收状态机）← 防烂尾的核心

bible/ 不存在时返回空 Bible，调用方回退到 knowledge/ 的散装 md。
"""
from pathlib import Path
import yaml

BIBLE_FILES = ("characters", "factions", "power_system",
               "timeline", "locations", "foreshadowing")


class Bible:
    def __init__(self, root):
        self.root = Path(root)
        self.bible_dir = self.root / "bible"
        self.data = {}

    @classmethod
    def load(cls, project_root):
        bible = cls(project_root)
        for name in BIBLE_FILES:
            f = bible.bible_dir / f"{name}.yaml"
            if f.exists():
                with open(f, "r", encoding="utf-8") as fh:
                    bible.data[name] = yaml.safe_load(fh) or {}
        return bible

    def save(self):
        self.bible_dir.mkdir(parents=True, exist_ok=True)
        for name in BIBLE_FILES:
            if name in self.data:
                with open(self.bible_dir / f"{name}.yaml", "w", encoding="utf-8") as fh:
                    yaml.safe_dump(self.data[name], fh, allow_unicode=True,
                                   sort_keys=False)

    # ---------- 伏笔登记簿 ----------
    def _hooks(self):
        return (self.data.get("foreshadowing") or {}).get("hooks", [])

    def unresolved_foreshadowing(self):
        """未回收的伏笔（planted 状态）。"""
        return [h for h in self._hooks() if h.get("status") == "planted"]

    def add_hook(self, description, planted_in, notes=""):
        hooks = self._hooks()
        new_id = f"FH{len(hooks) + 1:03d}"
        hooks.append({"id": new_id, "description": description,
                      "planted_in": planted_in, "status": "planted",
                      "resolved_in": None, "notes": notes})
        self.data.setdefault("foreshadowing", {})["hooks"] = hooks
        self.save()
        return new_id

    def resolve_hook(self, hook_id, resolved_in):
        for h in self._hooks():
            if h.get("id") == hook_id:
                h["status"] = "resolved"
                h["resolved_in"] = resolved_in
                self.save()
                return True
        return False

    # ---------- 供 prompt 使用的格式化 ----------
    def format_sections(self):
        """返回 {section_key: 文本}，空 bible 返回 {}。"""
        out = {}
        chars = (self.data.get("characters") or {}).get("characters", [])
        if chars:
            out["characters"] = "\n\n".join(
                "、".join(f"{k}：{v}" for k, v in c.items() if v) for c in chars
            )
        rules = (self.data.get("power_system") or {}).get("rules", [])
        if rules:
            out["world_rules"] = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(rules))
        stages = (self.data.get("power_system") or {}).get("stages", [])
        if stages:
            out["power_system"] = "境界体系（由低到高）：\n" + " → ".join(stages)
        events = (self.data.get("timeline") or {}).get("events", [])
        if events:
            out["timeline"] = "\n".join(
                f"- {e.get('time', '?')}：{e.get('event', '')}" for e in events
            )
        factions = (self.data.get("factions") or {}).get("factions", [])
        if factions:
            out["factions"] = "\n\n".join(
                "、".join(f"{k}：{v}" for k, v in f.items() if v) for f in factions
            )
        locs = (self.data.get("locations") or {}).get("locations", [])
        if locs:
            out["locations"] = "\n\n".join(
                f"{l.get('name', '')}：{l.get('description', '')}" for l in locs
            )
        unresolved = self.unresolved_foreshadowing()
        if unresolved:
            out["foreshadowing"] = "\n".join(
                f"- [{h['id']}]（第 {h.get('planted_in', '?')} 章种下）："
                f"{h.get('description', '')}" for h in unresolved
            )
        return out
