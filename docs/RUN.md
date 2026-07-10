ollama serve


# AI-Novel-Engine 本地运行说明

## 1. 系统组成

本项目由三个部分组成：

```
AI-Novel-Engine

        |
        |
        ↓

Python Application

        |
        |
        ↓

Ollama AI Runtime

        |
        |
        ↓

Qwen2.5-14B Local Model
```

说明：

* Python 项目负责：

  * 小说生成逻辑
  * Agent 调度
  * Prompt管理
  * 知识库读取

* Ollama负责：

  * 加载本地大模型
  * GPU推理
  * 返回AI生成结果

* Qwen2.5-14B负责：

  * 小说生成
  * 剧情设计
  * 世界观扩展

---

# 2. 第一次启动环境

## 2.1 进入项目目录

```bash
cd ~/workspace/AI-Novel-Engine
```

---

## 2.2 激活 Python 虚拟环境

Mac:

```bash
source venv/bin/activate
```

成功后：

```
(venv) username AI-Novel-Engine %
```

---

## 2.3 启动 Ollama

每次运行 AI 前，需要确保 Ollama 服务运行。

启动：

```bash
ollama serve
```

正常：

```
Listening on 127.0.0.1:11434
```

注意：

这个 Terminal 窗口需要保持运行。

---

# 3. 检查 Ollama 状态

打开新的 Terminal：

进入项目：

```bash
cd ~/workspace/AI-Novel-Engine
```

查看模型：

```bash
ollama list
```

应该看到：

```
NAME             SIZE

qwen2.5:14b      9GB
```

查看正在运行模型：

```bash
ollama ps
```

---

# 4. 运行小说生成程序

新 Terminal：

进入项目：

```bash
cd ~/workspace/AI-Novel-Engine
```

激活环境：

```bash
source venv/bin/activate
```

运行：

```bash
python main.py
```

执行流程：

```
main.py

 ↓

writer_agent.py

 ↓

ollama_client.py

 ↓

Ollama API

 ↓

Qwen2.5-14B

 ↓

生成小说
```

---

# 5. 日常开发流程

每天开始：

## Terminal 1

启动 AI 引擎：

```bash
ollama serve
```

保持。

---

## Terminal 2

开发：

```bash
cd ~/workspace/AI-Novel-Engine

source venv/bin/activate

code .
```

---

运行：

```bash
python main.py
```

---

# 6. 如果 Ollama 已经后台运行

有些情况下 Ollama 会自动启动。

检查：

```bash
ollama ps
```

如果正常：

可以直接：

```bash
python main.py
```

不需要再次：

```bash
ollama serve
```

---

# 7. 停止服务

停止 Python：

```
Ctrl + C
```

停止 Ollama：

在运行 ollama serve 的窗口：

```
Ctrl + C
```

---

# 8. 常见问题

## 问题1：

```
Connection refused
```

原因：

Ollama没有启动。

解决：

```bash
ollama serve
```

---

## 问题2：

程序长时间没有输出

原因：

第一次加载模型。

检查：

```bash
ollama ps
```

等待模型加载完成。

---

## 问题3：

模型不存在

错误：

```
model qwen2.5:14b not found
```

解决：

```bash
ollama pull qwen2.5:14b
```

---

# 9. 当前版本架构

```
VS Code

    |
    |
Python Application

    |
    |
ollama Python SDK

    |
    |
Ollama Server

    |
    |
Qwen2.5-14B

```

---

# 10. 后续升级计划

## Phase 1

完成：

* 本地模型调用
* 小说生成

## Phase 2

加入：

* 世界观数据库
* 人物数据库
* 时间线

## Phase 3

加入：

* Embedding
* Chroma
* RAG

## Phase 4

加入：

* 剧情Agent
* 写作Agent
* 审核Agent

最终成为：

AI 小说创作系统。
