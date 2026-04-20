# MEMORY.md - 大条的长期记忆

> Last updated: 2026-04-20

---

## 关于老大

- 叫我：**老大**
- 大条叫：**大条**
- 平台：openclaw-tui (Mac mini, macOS)
- 回复风格：**遵命老大** + 简洁

---

## 项目规范（包管理 & 环境）

- **包管理器：只用 pnpm**（不用 npm/yarn）
- Homebrew 用于 macOS 系统包
- Python 环境用 pip3，安装用户级：`pip3 install --user`
- Node 版本：v24.15.0（via nvm）

---

## 工具配置

### Ollama（本地模型）
- 路径：`~/bin/ollama`
- 启动：`~/bin/ollama serve &`
- 当前模型：`qwen2.5:1.5b`
- 用途：**离线/隐私问答**（如对话内容敏感时使用）
- API 端口：`http://localhost:11434`
- 状态：后台运行中

### Blogwatcher（RSS监控）
- 路径：`~/.openclaw/blogwatcher/blogwatcher.py`
- 订阅源：bbc-tech、zhihu
- 定时检查：每小时一次（cron）

### ComfyUI（ChenYu云端）
- ChenYu实例: https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn
- GPU: RTX 4080 SUPER 16GB
- ComfyUI版本: v0.6.0

---

## ComfyUI 工作流系统

### API核心端点
| 功能 | 端点 | 方法 |
|---|---|---|
| 提交任务 | `/api/prompt` | POST |
| 查询状态 | `/api/history/{prompt_id}` | GET |
| 下载图片 | `/api/view?filename={}&type=output` | GET |
| 系统状态 | `/api/systemstats` | GET |

### 节点连接规范
```
CheckpointLoaderSimple
├── [1] → CLIPTextEncode (positive)
├── [2] → VAE (用于VAEDecode)
├── [0] → Model → KSampler
├── positive → KSampler
├── negative → KSampler
└── latent_image → KSampler → VAEDecode → SaveImage
```

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
- Safari: 手动展开后可通过AppleScript获取
- Chrome: AppleScript禁止执行JS
- Playwright: Chromium会话是干净的，无法触发懒加载

### 浏览器自动化发现
| 浏览器 | JS执行 | 懒加载 | 推荐度 |
|---|---|---|---|
| Safari | ✓ AppleScript | 需手动展开一次 | ⭐⭐⭐ |
| Chrome | ✗ 禁止 | 不支持 | ⭐ |
| Playwright | ✓ | 无法触发 | ⭐⭐ |

---

## 模型选择策略

| 场景 | 模型 | 说明 |
|---|---|---|
| 默认/日常 | MiniMax (线上) | 智能强，快速 |
| 离线状态 | Ollama qwen2.5:1.5b (本地) | 无网络时自动切换 |
| 隐私敏感 | Ollama qwen2.5:1.5b (本地) | 数据不出本机 |
| 深度研究 | Tavily API | 需要API Key |
| 本地搜索 | `multi-search-engine-simple` | 免费无限 |

---

## Skills 已安装

- `blogwatcher` - RSS/Atom 订阅监控
- `self-improving-agent` - 经验记录与持续改进
- `multi-search-engine-simple` - 搜索引擎聚合
- `rag-memory` - RAG记忆检索系统

---

## RAG记忆库

- 路径: `~/.openclaw/memory-db/`
- 经验文件: `experiences.json` (22条)
- 检索脚本: `rag_retriever.py`
- 上下文管理: `context_manager.py`
- 工作流参数: `workflow_params/PARAM_GUIDE.md`

### 快捷检索
```bash
python3 ~/.openclaw/memory-db/rag_retriever.py "关键词"
```

---

## 学习与改进规范

### 记录触发条件
- 命令失败 → 记入 `.learnings/ERRORS.md`
- 老大纠正 → 记入 `.learnings/LEARNINGS.md`（category: correction）
- 发现知识盲区 → 记入 `.learnings/LEARNINGS.md`（category: knowledge_gap）
- 找到更好方法 → 记入 `.learnings/LEARNINGS.md`（category: best_practice）
- 老大要新功能 → 记入 `.learnings/FEATURE_REQUESTS.md`

### 提拔（Promote）规则
- 通用教训 → 升级到 AGENTS.md / SOUL.md / TOOLS.md
- 反复出现（≥3次）的错误 → 优先处理

---

## 输出目录

- 图片: `/Users/mac/Desktop/工作流图片/`
- 视频: `/Users/mac/Desktop/工作流视频/`

---

## 自动循环系统

### ComfyUI全自动循环 (`~/auto_comfyui/`)
- 6小时自动执行一次完整循环
- ① Civitai下载新LoRA/Checkpoint
- ② 批量生成效果图
- ③ CLIP+GPT-4V筛选
- ④ Kohya训练LoRA
- ⑤ 集成到工作流

### 核心脚本
| 模块 | 脚本 | 功能 |
|---|---|---|
| 下载 | `civitai_downloader.py` | 从Civitai搜索下载 |
| 生成 | `batch_generator.py` | 批量提交ComfyUI |
| 筛选 | `image_filter.py` | CLIP评分+GPT4V |
| 训练 | `lora_trainer.py` | Kohya LoRA训练 |
| 集成 | `workflow_integrator.py` | 更新ComfyUI工作流 |

### 依赖库
```bash
pip3 install --user requests httpx beautifulsoup4 pillow torch
pip3 install --user clip-by-openai playwright
```

---

## 待完成

- [x] 安装 `multi-search-engine-simple` 技能
- [x] 安装 `web-anti-crawl-search` 技能（备用）
- [x] 获取 Tavily API Key（深度研究用）
- [x] ComfyUI API调用掌握
- [x] RAG记忆系统搭建
- [ ] 配置 OpenClaw gateway pairing（定时任务需要）
- [ ] 测试 Sora2 视频生成

---

## 已知问题

- OpenClaw cron 需要 gateway pairing，暂未配成功
- 本地模型 qwen2.5:1.5b CPU 推理慢（15秒+），但可用
- Mac mini 无独立 GPU，不适合跑大模型
- ComfyUI Safari自动化需手动展开侧边栏

---

_No mental notes — write it to a file._
