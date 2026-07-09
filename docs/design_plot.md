  planning:
    levels:
      - volume
      - arc
      - plot
      - chapter
      - scene


agents
│
├── planner_agent.py          # 剧情规划
│
├── writer_agent.py           # 正文生成
│
├── memory_agent.py           # 记忆管理
│
├── summary_agent.py          # 总结
│
├── character_agent.py        # 人物管理
│
├── world_agent.py            # 世界变化
│
├── critic_agent.py           # 小说质量检查
│
└── editor_agent.py           # 重写优化