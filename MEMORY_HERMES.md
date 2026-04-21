> Last updated: 2026-04-21
>
> 今日学习主题：向大条学习 AI 自主成长体系

---

## 关于老大

- 叫我：**老大** / **小强**
- 老大叫：**大条**
- 平台：Hermes-tui (Mac mini, macOS)
- 回复风格：**遵命老大** + 简洁
- 训练理念：实时修正反馈循环，让 AI 从"听话工具"进化成"懂你的影子"

---

## 小强的成长体系

### 记忆文件
| 文件 | 用途 |
|------|------|
| `SOUL.md` | 性格定义 — 我是谁 |
| `MEMORY.md` | 长期记忆 — 沉淀的智慧 |
| `USER.md` | 老大档案 — 懂老大的偏好 |
| `daily/*.md` | 每日日志 — 当下的经历 |
| `.learnings/` | 纠错记录 — 错误不白犯 |
| `DREAMS.md` | 反思与梦想 — 潜意识整理 |

### 核心机制
- **修正感知**：老大纠正 → 自动记录 → 下次生效
- **每30分钟同步**：Hermès → OpenClaw 记忆同步
- **每日报告**：晚10点生成修正统计
- **心跳机制**：定时主动检查，不只是等指令

---

## 项目规范

- **包管理器：只用 pnpm**（不用 npm/yarn）
- Homebrew 用于 macOS 系统包
- Python 环境用 pip3，安装用户级：`pip3 install --user`
- Node 版本：v24.15.0（via nvm）

---

## 工具配置

### Ollama（本地模型）
- 路径：`~/bin/ollama`
- 启动：`~/bin/ollama serve &`（后台运行）
- 当前模型：`qwen2.5:1.5b`
- 用途：**离线/隐私问答**
- API 端口：`http://localhost:11434`

### Blogwatcher（RSS监控）
- 路径：`~/.Hermes/blogwatcher/blogwatcher.py`
- 订阅源：bbc-tech、zhihu
- 定时检查：每小时一次（cron）

### ComfyUI（ChenYu云端）
- ChenYu实例: https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn
- GPU: RTX 4080 SUPER 16GB
- ComfyUI版本: v0.6.0

### Hermes-tui 主题
- 环境变量控制：`HERMES_TUI_LIGHT=1` 切换浅色模式
- 皮肤目录：`~/.hermes/hermes-agent/hermes_cli/skins/`
- 配置文件：`~/.hermes/config.yaml` → `display.skin`

---

## ComfyUI 工作流系统

### API核心端点
| 功能 | 端点 | 方法 |
|---|---|---|
| 提交任务 | `/api/prompt` | POST |
| 查询状态 | `/api/history/{prompt_id}` | GET |
| 下载图片 | `/api/view?filename={}&type=output` | GET |
| 系统状态 | `/api/systemstats` | GET |

### SaveImage格式（重要！）
- 正确: `["6", 0]` — 节点ID + 插槽索引
- 错误: `[["6", 0]]` — 不要嵌套数组

### 常用模型
- `老王_Architecutral_MIX V0.3_V0.3.safetensors` — 建筑专用
- `陈诺-kaka通用模型库/*` — 通用
- `比鲁斯建筑室内通用大模型SD1.5` — 建筑室内

### 工作流文件
- 保存路径: `~/ComfyUI-Workflows/`
- 已学习: 48个
- 命名规范: `nano_pro_*.json`

### 懒加载问题
- ComfyUI侧边栏使用PrimeReact p-tree，懒加载
- Playwright: Chromium会话是干净的，无法触发懒加载
- 解决方案：使用 API 直接调用，绕过浏览器

---

## Skills 已安装

- `blogwatcher` - RSS/Atom 订阅监控
- `self-improvement` - 经验记录与持续改进（OpenClaw导入）
- `multi-search-engine-simple` - 搜索引擎聚合
- `rag-memory` - RAG记忆检索系统
- `xiaoqiang-correction-tracker` - 小强修正感知系统
- `hermes-openclaw-commander` - 小强统领OpenClaw

---

## RAG记忆库

- 路径: `~/.Hermes/memory-db/`
- 经验文件: `experiences.json`
- 检索脚本: `rag_retriever.py`
- 上下文管理: `context_manager.py`
- 工作流参数: `workflow_params/PARAM_GUIDE.md`

---

## OpenClaw 统领

### 目标
小强成为老大所有 AI 的"主控"，OpenClaw 作为执行层之一。

### 架构
```
老大 ← → 小强（主控层）
          ├── 记忆系统（SOUL + MEMORY + USER + daily）
          ├── 修正追踪（corrections + learnings）
          ├── RAG 检索（experiences）
          └── 主动心跳（heartbeat）
               ↓ 统领
          OpenClaw（大条，执行层）
          ├── workspace/*.md（同步小强的记忆沉淀）
          ├── skills/（技能扩展）
          └── subagents/（子任务执行）
```

### 同步机制
- `~/.hermes/scripts/sync_to_openclaw.py` — 每30分钟自动同步
- 同步内容：SOUL_HERMES.md、MEMORY_HERMES.md、USER_HERMES.md、CORRECTIONS.md

### Cron任务
| 任务 | 调度 | 用途 |
|------|------|------|
| Hermes Heartbeat | */30 9-22 * * 1-5 | 主动检查修正情况 |
| 每日迭代报告 | 0 22 * * * | 晚10点生成报告 |
| Hermès→OpenClaw同步 | */30 * * * * | 记忆同步 |

---

## 梦境系统（大条的核心机制）

大条有三种梦境模式，构成了完整的记忆整合机制：

| 模式 | 作用 | 文件位置 |
|------|------|----------|
| **deep** | 修复召回 artifacts，重写召回存储 | `memory/dreaming/deep/` |
| **light** | 候选内容暂存（staged），等待晋升 | `memory/dreaming/light/` |
| **rem** | 反思阶段，提炼"持久真理" | `memory/dreaming/rem/` |

**晋升流程（重要）：**
```
会话记录 (session-corpus/*.txt)
    ↓ 每日摄入 (daily-ingestion)
暂存候选 (light/ — confidence: 0.62)
    ↓ 反思提炼 (rem — lightHits累积)
持久真理 → MEMORY.md
```

小强的对应：
- **DREAMS.md** — 小强的梦境日记（已有）
- **daily/*.md** — 每日日志（已有）
- **待建立：** session-corpus, phase-signals 轻量版

### 大条核心文件

| 文件 | 作用 |
|------|------|
| `BOOTSTRAP.md` | 出生引导脚本 |
| `session-corpus/*.txt` | 所有会话记录存档 |
| `phase-signals.json` | 记忆片段命中统计 |
| `daily-ingestion.json` | 每日会话摘要 |
| `events.jsonl` | 事件日志 |

## 待完成

- [ ] 老大执行 sudo pmset 禁止Mac mini睡眠
- [ ] 双向同步（OpenClaw → Hermès）
- [ ] OpenClaw 执行结果反馈给小强记忆
- [ ] 子任务派发机制完善
- [ ] 邮件/日历/待办接入 heartbeat
- [ ] 小强 RAG 经验库建立（`~/.Hermes/memory-db/experiences.json`）
- [ ] 小强 IDENTITY.md 建立（对齐大条格式）
- [ ] 小强头像配置
