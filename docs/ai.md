这些参数是 **LLM 推理时的控制旋钮**。理解它们非常重要，因为你的 AI-Novel-Engine 后面会大量依赖这些参数控制：

* 写正文（创造力）
* 剧情规划（逻辑）
* 战力审核（严谨）
* 知识提取（准确）

我按照 **从最重要 → 次重要** 给你解释。

---

# 1. model

```python
model: str = "qwen2.5:14b"
```

## 含义

指定使用哪个大语言模型。

例如：

```python
model="qwen2.5:14b"
```

表示：

使用：

> Qwen 2.5 参数量 140亿 的模型

其他例子：

```python
model="llama3.1:8b"
```

使用 Llama。

```python
model="deepseek-r1:14b"
```

使用 DeepSeek。

---

## 对你的项目影响

这个决定：

* 文笔能力
* 推理能力
* 世界理解能力
* 中文能力

你的：

```yaml
qwen2.5:14b
```

适合：

✅ 中文小说
✅ 世界观构建
✅ YAML知识整理

但是：

14B 写 500万字长篇，会需要：

* memory
* summary
* context管理

否则不是模型不行，而是上下文丢失。

---

# 2. prompt

```python
prompt
```

这是：

> 你发送给 AI 的主要内容

例如：

```python
prompt="""
请写第100章。

剧情目标：
林玄突破恒星级。

要求：
符合吞噬星空世界规则。
"""
```

模型看到：

```
用户：
请写第100章...
```

然后生成。

---

# 3. system

```python
system="""
你是一名专业网络小说作者。
请严格遵守吞噬星空世界规则。
"""
```

这个叫：

> System Prompt（系统指令）

它的优先级高于普通 prompt。

消息结构：

```json
[
 {
  "role":"system",
  "content":"你是一名小说作者"
 },

 {
  "role":"user",
  "content":"写第一章"
 }
]
```

AI理解：

```
系统：
你的身份是什么

用户：
现在让你做什么
```

---

## 举例

没有 system：

```
用户：
写小说
```

AI可能：

```
我可以帮你写小说。
```

---

有 system：

```
system:
你是起点白金作者

user:
写小说
```

AI：

直接进入创作状态。

---

# 4. temperature

```python
temperature=0.75
```

这是最重要参数之一。

它控制：

> 随机性 / 创造力

范围：

```
0 ~ 2
```

---

## temperature=0

非常稳定。

例如：

问：

```
罗峰是什么境界？
```

回答：

每次几乎一样。

适合：

* 知识查询
* YAML生成
* 数据分析

---

## temperature=0.3

稍微创造。

适合：

```
剧情规划
时间线整理
```

---

## temperature=0.8

创造性强。

适合：

```
小说正文
人物对白
战斗描写
```

你的：

```python
0.75
```

比较适合小说。

---

## temperature过高

例如：

```
1.5
```

容易：

林玄：

第一章：

恒星级

第二章：

宇宙之主

第三章：

创造宇宙

战力崩坏。

---

# 5. max_tokens / num_predict

你的：

```python
max_tokens=6000
```

对应：

```python
num_predict=6000
```

含义：

> AI最多生成多少 token

注意：

不是字。

---

中文大概：

```
1 token ≈ 1.5~2 中文字
```

所以：

```
6000 tokens
≈ 9000~12000 字
```

---

你的小说：

一章：

6000字

非常合适。

---

如果：

```python
num_predict=1000
```

输出：

短：

```
几千字以内
```

---

# 6. num_ctx

```python
num_ctx=32768
```

这是：

> 上下文窗口大小

也就是：

AI一次最多能"记住"多少内容。

公式：

```
上下文 =
system
+
prompt
+
历史消息
+
输出
```

---

例如：

你的：

```
num_ctx=32768
```

里面：

输入：

```
25000 tokens
```

输出：

```
6000 tokens
```

刚好：

```
31000 tokens
```

可以。

---

如果：

```python
num_ctx=8192
```

你的小说：

```
世界观
+
人物
+
历史章节
```

很容易被截断。

---

# 7. top_p

```python
top_p=0.9
```

叫：

> nucleus sampling（核采样）

简单理解：

控制 AI 从多少候选答案里面选择。

---

比如生成：

```
林玄看着天空
```

下一词：

候选：

```
A 星辰
概率40%

B 苍穹
概率30%

C 世界
概率20%

D 苹果
概率1%
```

top_p决定：

保留哪些候选。

---

top_p=1：

全部考虑。

top_p=0.9：

只考虑累计概率90%的词。

---

小说：

推荐：

```
0.85~0.95
```

---

# 8. top_k

```python
top_k=40
```

意思：

每一步：

只考虑概率最高的40个词。

---

例如：

模型有：

10000个可能词。

top_k=40：

只看：

```
最可能的40个
```

---

效果：

减少：

* 奇怪词
* 发疯输出

小说：

推荐：

```
40~100
```

---

# 9. repeat_penalty

```python
repeat_penalty=1.1
```

重复惩罚。

防止：

AI一直写：

```
林玄心中震撼。

林玄非常震撼。

林玄感到无比震撼。
```

---

范围：

```
1.0
```

没有惩罚。

```
1.1
```

轻微。

```
1.5
```

强烈。

小说：

推荐：

```
1.05~1.15
```

你的：

```
1.1
```

很好。

---

# 10. options覆盖机制

你代码：

```python
self.default_options={
    "temperature":0.75,
    "num_predict":6000
}
```

默认：

写小说。

但是：

调用：

```python
self.llm.chat(

 prompt,

 options={
    "temperature":0.3
 }

)
```

会覆盖：

原来：

```
0.75
```

变：

```
0.3
```

---

所以：

默认：

```yaml
writer
```

可以：

```yaml
temperature:0.8
```

特殊 Agent：

覆盖。

---

# 针对你的小说项目，推荐配置

## WriterAgent（写正文）

```python
{
"temperature":0.8,
"num_predict":6000,
"num_ctx":32768,
"top_p":0.9,
"top_k":50,
"repeat_penalty":1.1
}
```

---

## PlannerAgent（设计剧情）

```python
{
"temperature":0.5,
"num_predict":3000,
"top_p":0.9,
"repeat_penalty":1.05
}
```

---

## ReviewerAgent（检查战力）

```python
{
"temperature":0.2,
"num_predict":2000,
"top_p":0.8
}
```

---

## 最后总结一句：

你的 AI 小说系统里：

| 参数             | 控制什么       |
| -------------- | ---------- |
| model          | 用谁的大脑      |
| system         | 给 AI 身份和规则 |
| prompt         | 当前任务       |
| temperature    | 创造力        |
| num_predict    | 写多长        |
| num_ctx        | 记多少上下文     |
| top_p          | 选择范围       |
| top_k          | 候选数量       |
| repeat_penalty | 防重复        |

对于你的《吞噬星空之浑源道主》，最重要排序：

```
1. num_ctx      防遗忘
2. system       保持世界规则
3. temperature  控制文风
4. num_predict  控制章节长度
5. repeat_penalty 防水文重复
```

你现在重构 `ollama_client.py` 是正确方向，因为这些参数以后必须由不同 Agent 灵活控制。
