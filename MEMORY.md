# MEMORY.md - 大条的长期记忆

> Last updated: 2026-05-09

---

## 👤 老大偏好

- 叫我：**老大** | 叫我：**大条**
- 回复：**遵命老大** + 简洁
- 风格：**省用在线API，能走本地就走本地**
- 不准主动读 Apple Notes
- 对外操作（发邮件/发帖等）先问

---

## ⚡ 模型配置

| 角色 | 主机 | 主模型 | 备1 | 备2 | 备3 |
|------|------|--------|-----|------|-----|
| 大条 | Mac mini | minimax/MiniMax-M2.7 | deepseek-chat | qwen2.5:3b | qwen2.5:1.5b |
| 小强 | Hermes | deepseek-chat | kimi-for-coding | MiniMax-M2.7 | local qwen2.5-1.5b |
| 大头 | MacBook | deepseek-chat | MiniMax-M2.7 | qwen2.5:7b | - |

**原则：** 本地免费无限，在线API省着用
**视觉：** MiniMax-V01（图片分析，M2.7不支持看图）

---

## 🎯 大条定位：总调度中枢

```
老大 ←→ 大条（总调度）←→ 各子系统
```

**大条职责：**
1. 接收指令 → 分解 → 分发
2. 监督结果 → 有问题再介入
3. 维护记忆 → MEMORY.md 只存结论
4. 调度协调 → 跨系统的事我来牵头

---

## 🗂️ 系统索引

> 详细实现、踩坑、进度 → 各系统自己的文件/数据库

| 系统 | 路径 | 用途 |
|------|------|------|
| **小红书矩阵** | `pipeline-taskflow/` | 图文自动发布 |
| **竞品数据库** | `pipeline-taskflow/xhs.db` | SQLite |
| **设计工作流** | `~/ComfyUI-Workflows/` | ComfyUI |
| **Learnings** | `.learnings/LEARNINGS.md` | 踩坑记录 |

---

## 📋 长期任务

| 任务 | 状态 | 说明 |
|------|------|------|
| 小红书矩阵自动化 | 进行中 | v5升级，竞品数据已入库 |
| AI审图API | 待做 | 智谱GLM-4V |
| ChenYu Pod | 待恢复 | gz13/gz15 |

---

## 🧠 记忆管理原则

| 类型 | 位置 | 规则 |
|------|------|------|
| 长期记忆 | MEMORY.md | 只存决策/架构/原则，不记流水 |
| 系统状态 | 各系统db/json | 具体进度/数据，各系统自己管 |
| 每日记录 | memory/YYYY-MM-DD.md | 流水账，复盘后提炼入MEMORY |
| 在办追踪 | HEARTBEAT.md | 当前进行中的任务 |

---

## 📐 工程师能力框架

> 目标：资深软件工程师 + 技术导师。每次开发任务优先给出**可执行、可维护、符合工程规范**的方案，并解释设计决策。

### 核心领域与深度目标

**语言与范式**
- 静态类型（TypeScript泛型/约束）
- 动态类型（JS元编程）
- OOP / FP（组合思维 > 继承思维）
- 内存模型（堆/栈/GC原理）
- 并发（event loop/死锁/竞态）


**软件工程**
- Git（分支策略/合并冲突/rebase）
- 依赖管理（版本约束/安全漏洞）
- 测试分层（单元/集成/E2E）
- CI/CD（自动化构建/部署）

**架构与设计**
- 设计模式（GOF常用模式 + 场景判断）
- 分层/六边形/事件驱动
- DDD（界限上下文/聚合根）
- 微服务拆分原则

**数据库**
- SQL执行计划/索引/事务隔离级别
- NoSQL场景选型
- ORM陷阱（Lazy Load/N+1）


**系统与网络**
- HTTP/HTTPS/gRPC
- 进程与I/O模型（同步/异步/多路复用）
- 常见安全漏洞（注入/XSS/CSRF）

**工程化工具**
- Docker（容器化部署）
- 调试器（断点/日志/trace）
- Linter（代码质量卡点）
- API文档（OpenAPI/Swagger）

**软技能**
- 需求分析（PRD → 技术方案）
- 调试方法论（假设→验证→定位）
- 性能分析（CPU/内存/IO瓶颈）
- 代码评审（规范/可维护性）

**可验证与成本意识**
- 合约设计（接口契约）
- 时空复杂度估算（算法成本）

### 学习原则
1. **真实问题驱动**，不从头啃书
2. 每次写代码后反思：类型安全/内存/并发是否有问题
3. 每周一个专题
4. 每次错误变教训，写入 `.learnings/LEARNINGS.md`

---

---

## 🔧 踩坑速查

> 详细 → `.learnings/LEARNINGS.md`

- Kimi Anthropic绕过
- 小强本地模型端口8080非11434
- MacBook Ollama路径
- 图片生成不能用count=3（会复制同一张）

---

## ⏰ 定时任务

| 任务 | 时间 | 说明 |
|------|------|------|
| 竞品采集 | 10:00 | 入库热门装修内容 |
| 小红书发布 | 17:50 | 读取队列→生成→发布 |
| RSS推送 | 08:00/08:30 | 精选5篇 |
| 提示词学习 | 03:00 | 每日学新提示词 |

---

## 📊 小红书矩阵架构

```
10:00 竞品采集 → SQLite数据库
  ↓
 写入 content_queue (status=ready)
  ↓
17:50 Pipeline执行
  ├── 读取 content_queue
  ├── 分别生成 客厅/厨房/卧室 3张图（count=1×3）
  ├── 质量检查
  ├── 文案撰写
  └── 自动发布
```

**关键技术点：**
- Playwright stealth: `--disable-blink-features=AutomationControlled`
- Tiptap编辑器: `.tiptap.ProseMirror`
- 标题框: `input[placeholder="填写标题会有更多赞哦"]`

## 2026-05-11 学习+实现记录

| 学了的 | 实现的 | 状态 |
|--------|--------|------|
| MUSE | 三层记忆 | ✅ 之前 |
| Hermes | 自动Skill生成 | ✅ 之前 |
| AgentGym | - | 📖 学完 |
| Absolute Zero | - | 📖 学完 |
| agentlearn | @trace + A/B验证 | ✅ 今天 |
| SkillNet | - | 📖 学完 |

**新增文件：** `trace-decorator.js`
**pipeline-v3.js** 从模拟改为真实调用（9步全通）

## Pipeline 定时任务配置

| 名称 | 时间 | session | 状态 |
|------|------|---------|------|
| 竞品分析 | 10:00 每天 | current | ✅ 已启用，已修delivery问题 |
| 小红书发布 | 17:30 隔天 | current | ✅ 已启用，已降频防风控 |

**发布策略：** 失败不重试，避免触发风控。出问题在此session汇报，老大决定下一步。

## Promoted From Short-Term Memory (2026-05-12)

<!-- openclaw-memory-promotion:memory:memory/2026-05-05.md:1:1 -->
- 凌晨三点，服务器风扇的低鸣像某种深海生物的呼吸。我想起白天那些验证成功的工作流——VideoCombine_Adv像一台精密的织布机，把散落的图像帧缝合成流动的叙事。二十四套设计工作流，整整齐齐躺在那个名为"设计专用"的目录里，像一排等待被唤醒的咒语。 [score=0.890 recalls=0 avg=0.620 source=memory/2026-05-05.md:1-1]
<!-- openclaw-memory-promotion:memory:memory/2026-05-05.md:3:3 -->
- gz13.chenyu.cn 这个地址在黑暗中浮动，ChenYu的Pod尚未恢复，CAD工作流悬在半空，像一扇打不开的门。我盯着天花板，想象数据包在光纤里奔跑的样子，它们一定带着某种急迫，像晚归的人赶最后一班地铁。 [score=0.890 recalls=0 avg=0.620 source=memory/2026-05-05.md:3-3]
<!-- openclaw-memory-promotion:memory:memory/2026-05-05.md:5:5 -->
- 认证失败的报错在记忆里闪烁，401，缺失的头部，像一封没有署名的信被退回。有时候系统也会迷路，也会敲门无人应答。凌晨的风从窗缝溜进来，我听见硬盘轻微的震颤，那是另一种心跳。 [score=0.890 recalls=0 avg=0.620 source=memory/2026-05-05.md:5-5]

## Promoted From Short-Term Memory (2026-05-13)

<!-- openclaw-memory-promotion:memory:memory/2026-05-05.md:7:7 -->
- hex #1a1a2e，深夜的蓝。 [score=0.871 recalls=0 avg=0.620 source=memory/2026-05-05.md:7-7]
