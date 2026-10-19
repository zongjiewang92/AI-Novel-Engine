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

# 开新卷（建目录 + 切换 current_volume_id）
python main.py swallowing_star_fanfic --new-volume "星空篇"

# 跑单元测试（无需 Ollama）
python -m unittest discover -s tests
```

详细步骤见 [docs/RUN.md](docs/RUN.md)。

## 项目结构

```
AI-Novel-Engine
├── main.py                  # 薄 CLI（参数解析），编排在 pipeline.py
├── pipeline.py              # 步骤注册表：LLM 先行→原子落盘→幂等可重跑
├── llm/
│   ├── provider.py          # 双后端路由：ollama（本地）+ OpenAI-compatible（线上）
│   │                           # config.yaml 按任务配模型，key 走环境变量
│   ├── ollama_client.py     # 旧版直调（保留兼容）
│   ├── token_budget.py      # prompt token 预算：超限按优先级截断/丢弃
│   └── json_utils.py        # JSON 自修复解析（裸 json.loads 的终结者）
├── prompts/                 # prompt 模板（调 prompt 不用改代码）
│   ├── writer.txt               # 写章节（含 bible 章节：力量体系/伏笔/势力地点）
│   ├── critique.txt / revise.txt# 审稿 / 改稿
│   ├── chapter_summary.txt / volume_summary.txt / planner.txt
│   └── memory_update.txt        # 长期记忆合并
├── agents/                  # 七个 Agent
│   ├── writer_agent.py          # 写章节（token 预算组装 prompt，bible 优先）
│   ├── critic_agent.py          # 审稿：按 beat+bible+伏笔打分判 pass/revise
│   ├── reviser_agent.py         # 改稿：按审稿意见重写
│   ├── chapter_summary_agent.py # 章节总结 → 章节记忆
│   ├── volume_summary_agent.py  # 卷总结 → 卷记忆（每 10 章）
│   ├── planner_agent.py         # 剧情规划
│   └── memory_agent.py          # 长期记忆合并 → story_summary（记忆闭环）
├── database/                # 项目与状态管理
│   ├── project_manager.py       # 项目目录/配置文件
│   ├── project_context.py       # 聚合上下文（卷定位收敛到单一方法）
│   ├── bible_manager.py         # World Bible：人物/势力/力量体系/时间线/地点/伏笔登记簿
│   ├── volume_manager.py        # 建卷/切卷显式化
│   ├── state_manager.py         # novel_state.json 读写（原子写）
│   ├── memory_manager.py        # 三级记忆存取（原子写）
│   └── plot_manager.py          # 当前剧情段定位（range 解析容错）
├── utils/                   # 日志、文件工具（含原子写、prompt 加载）
├── tests/                   # 单元测试（unittest，零新依赖）
├── projects/                # 一书一目录
│   └── swallowing_star_fanfic/  # 《吞噬星空之浑源道主》（当前在写第 7 章）
│       ├── config.yaml          # 书名、模型、温度、LLM 路由、审稿开关
│       ├── bible/               # World Bible（人物/势力/力量体系/时间线/地点/伏笔登记簿）
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

## 架构说明（2026-10-18 重构后）

- **LLM 路由**：`llm/provider.py` 双后端。`config.yaml` 的 `llm.tasks` 按任务配模型——写章节/审稿/改稿走强模型（线上），总结/规划/记忆走本地。线上 key 走环境变量（`export DEEPSEEK_API_KEY=sk-...`），不写配置文件。预设：deepseek / openai / qwen（DashScope）/ moonshot / ollama，全 OpenAI-compatible 零新依赖
- **写→审→改**：每章初稿经 critic 打分（剧情/一致性/人物/节奏/伏笔五维），`verdict=revise` 或低于阈值自动改稿，轮数可配（`critique_rounds: 0` 关闭）
- **World Bible**：`bible/` 六份 YAML（人物/势力/力量体系/时间线/地点/**伏笔登记簿**）。写手每章都能看到未回收伏笔；bible 优先于 `knowledge/` 散装 md
- **Token 预算**：写章节的 prompt 按优先级组装（剧情目标 > 世界规则 > 未回收伏笔 > 本卷目标 > 近章正文 > 人物 > 力量体系 > 章节摘要 > 长期记忆 > 时间线 > 势力 > 地点），超 `max_prompt_tokens` 自动截断/丢弃，日志会告诉你丢了什么
- **先算后写**：流水线里所有 LLM 调用都在落盘之前，中途崩了重跑安全；已生成的章节/记忆会复用，不重复烧 token
- **配置即生效**：`config.yaml` 的 temperature / max_tokens / max_prompt_tokens 真正传给模型（以前改了没用）
- **记忆闭环**：每 10 章自动把章节记忆合并进 `story_summary.json`（以前这个文件永远是空的）
- **开新卷**：`--new-volume` 一行命令建卷并切换，不用手动改 state

## 规划中（还没做）

- `rag/`：检索增强（人物/世界观知识库，替代现在的全文加载）
- API 服务：FastAPI 对外提供写作接口（依赖已从 requirements 暂时移除，用时加回）
