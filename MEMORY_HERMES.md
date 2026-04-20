> Last updated: 2026-04-20
§
---
§
关于老大: 叫我：**老大**
§
关于老大: 大条叫：**大条**
§
关于老大: 平台：Hermes-tui (Mac mini, macOS)
§
关于老大: 回复风格：**遵命老大** + 简洁
§
关于老大: ---
§
项目规范（包管理 & 环境）: **包管理器：只用 pnpm**（不用 npm/yarn）
§
项目规范（包管理 & 环境）: Homebrew 用于 macOS 系统包
§
项目规范（包管理 & 环境）: Python 环境用 pip3，安装用户级：`pip3 install --user`
§
项目规范（包管理 & 环境）: Node 版本：v24.15.0（via nvm）
§
项目规范（包管理 & 环境）: ---
§
工具配置 > Ollama（本地模型）: 路径：`~/bin/ollama`
§
工具配置 > Ollama（本地模型）: 启动：`~/bin/ollama serve &`
§
工具配置 > Ollama（本地模型）: 当前模型：`qwen2.5:1.5b`
§
工具配置 > Ollama（本地模型）: 用途：**离线/隐私问答**（如对话内容敏感时使用）
§
工具配置 > Ollama（本地模型）: API 端口：`http://localhost:11434`
§
工具配置 > Ollama（本地模型）: 状态：后台运行中
§
工具配置 > Blogwatcher（RSS监控）: 路径：`~/.Hermes/blogwatcher/blogwatcher.py`
§
工具配置 > Blogwatcher（RSS监控）: 订阅源：bbc-tech、zhihu
§
工具配置 > Blogwatcher（RSS监控）: 定时检查：每小时一次（cron）
§
工具配置 > ComfyUI（ChenYu云端）: ChenYu实例: https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn
§
工具配置 > ComfyUI（ChenYu云端）: GPU: RTX 4080 SUPER 16GB
§
工具配置 > ComfyUI（ChenYu云端）: ComfyUI版本: v0.6.0
§
工具配置 > ComfyUI（ChenYu云端）: ---
§
ComfyUI 工作流系统 > SaveImage格式（重要！）: 正确: `["6", 0]` — 节点ID + 插槽索引
§
ComfyUI 工作流系统 > SaveImage格式（重要！）: 错误: `[["6", 0]]` — 不要嵌套数组
§
ComfyUI 工作流系统 > 常用模型: `老王_Architecutral_MIX V0.3_V0.3.safetensors` — 建筑专用
§
ComfyUI 工作流系统 > 常用模型: `陈诺-kaka通用模型库/*` — 通用
§
ComfyUI 工作流系统 > 常用模型: `比鲁斯建筑室内通用大模型SD1.5` — 建筑室内
§
ComfyUI 工作流系统 > 工作流文件: 保存路径: `~/ComfyUI-Workflows/`
§
ComfyUI 工作流系统 > 工作流文件: 已学习: 48个
§
ComfyUI 工作流系统 > 工作流文件: 命名规范: `nano_pro_*.json`
§
ComfyUI 工作流系统 > 懒加载问题: ComfyUI侧边栏使用PrimeReact p-tree，懒加载
§
ComfyUI 工作流系统 > 懒加载问题: Playwright: Chromium会话是干净的，无法触发懒加载
§
ComfyUI 工作流系统 > 浏览器自动化发现: ---
§
模型选择策略: ---
§
Skills 已安装: `blogwatcher` - RSS/Atom 订阅监控
§
Skills 已安装: `self-improving-agent` - 经验记录与持续改进
§
Skills 已安装: `multi-search-engine-simple` - 搜索引擎聚合
§
Skills 已安装: `rag-memory` - RAG记忆检索系统
§
Skills 已安装: ---
§
RAG记忆库: 路径: `~/.Hermes/memory-db/`
§
RAG记忆库: 经验文件: `experiences.json` (22条)
§
RAG记忆库: 检索脚本: `rag_retriever.py`
§
RAG记忆库: 上下文管理: `context_manager.py`
§
RAG记忆库: 工作流参数: `workflow_params/PARAM_GUIDE.md`
§
RAG记忆库 > 快捷检索: ---
§
学习与改进规范 > 提拔（Promote）规则: ---
§
待完成: ---
§
WPS Office Mac: 主程序 /Applications/wpsoffice.app (运行中)，安装器 /Applications/WPS Office Installer.app