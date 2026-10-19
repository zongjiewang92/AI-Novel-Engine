# AI-Novel-Engine

本地大模型驱动的长篇小说连载引擎：一次写一章，自动做剧情规划、章节总结与三级记忆管理，断点可续写。纯本地运行（Ollama + Qwen2.5-14B），不花 API 钱。

## 特性

- **多 Agent 分工**：剧情规划（planner）→ 章节写作（writer）→ 章节总结 → 卷总结，各管一摊
- **三级记忆**：章节记忆 / 卷记忆 / 剧情规划记忆，写到几百章也不崩人设、不忘伏笔
- **断点续写**：`state/novel_state.json` 记录当前章节，随时停、随时从下一章继续
- **多项目**：`projects/` 下一个目录就是一本书，`main.py` 命令行切换

## 快速开始

```bash
# 1. 启动 Ollama（需已安装，并拉好模型）
ollama serve
ollama pull qwen2.5:14b

# 2. 建虚拟环境并装依赖
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. 跑起来（默认项目 swallowing_star_fanfic，可换成 projects/ 下任意目录名）
python main.py
python main.py my_new_novel
```

详细步骤见 [docs/RUN.md](docs/RUN.md)。

## 项目结构

```
AI-Novel-Engine
├── main.py                  # 入口：加载项目 → 写章节 → 存记忆 → 更新状态
├── llm/ollama_client.py     # 大模型调用封装（Ollama）
├── agents/                  # 四个 Agent
│   ├── planner_agent.py         # 剧情规划（输出 JSON）
│   ├── writer_agent.py          # 章节写作
│   ├── chapter_summary_agent.py # 章节总结 → 章节记忆
│   └── volume_summary_agent.py  # 卷总结 → 卷记忆（每 10 章）
├── database/                # 项目与状态管理
│   ├── project_manager.py       # 项目目录/配置文件
│   ├── project_context.py       # 聚合上下文（给 Agent 的"弹药库"）
│   ├── state_manager.py         # novel_state.json 读写
│   ├── memory_manager.py        # 三级记忆存取
│   └── plot_manager.py
├── utils/                   # 日志、文件工具
├── projects/                # 一书一目录
│   └── swallowing_star_fanfic/  # 《吞噬星空之浑源道主》（当前在写第 7 章）
│       ├── config.yaml          # 书名、模型、温度
│       ├── plot_plan.json
│       ├── state/               # novel_state.json、story_summary.json
│       └── volumes/volume01_地球篇/
├── docs/                    # 运行说明与设计文档
└── requirements.txt         # ollama + pyyaml，仅此而已
```

## 写一本新书

```bash
cp -r projects/swallowing_star_fanfic projects/my_new_novel
# 改 projects/my_new_novel/config.yaml（书名、作者）
# 清掉 state/ 和 volumes/ 下的旧进度（或保留当模板）
python main.py my_new_novel
```

## 当前进度

- 《吞噬星空之浑源道主》（吞噬星空同人）：第一卷「地球篇」，已写完 6 章，`current_chapter = 7`

## 规划中（还没做）

- `rag/`：检索增强（人物/世界观知识库，预留了 chromadb 位置）
- API 服务：FastAPI 对外提供写作接口（依赖已从 requirements 暂时移除，用时加回）
