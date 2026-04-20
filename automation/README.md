# 自动化工具包

## 目录结构
```
automation/
├── comfyui_automator.py  # 主自动化脚本
└── README.md

customer_mapping/
├── matcher.py             # 需求匹配器
├── MAPPING.md             # 映射表文档
└── README.md

../memory-db/
├── workflow_params/       # 参数调优指南
│   └── PARAM_GUIDE.md
└── experiences.json       # 经验库(已更新22条)
```

## 使用方法

### 1. 自动化学习
```bash
# 已知位置模式（更稳定）
python3 ~/.openclaw/workspace/automation/comfyui_automator.py known

# 自动扫描模式
python3 ~/.openclaw/workspace/automation/comfyui_automator.py auto
```

### 2. 客户需求匹配
```bash
python3 ~/.openclaw/workspace/customer_mapping/matcher.py "我有手绘图想看效果图"
```

### 3. 参数查询
参考 `~/.openclaw/memory-db/workflow_params/PARAM_GUIDE.md`

## 快捷命令
```bash
# 快速测试
python3 ~/.openclaw/workspace/comfyui_test.py --scene arch_maopi --quick

# 高清出图
python3 ~/.openclaw/workspace/comfyui_test.py --scene kitchen --hd
```
