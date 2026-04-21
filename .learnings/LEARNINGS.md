# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice

---

## Error Handling Principle (from 老大)
**每次错误都被立刻标记、显式纠正、并让纠正结果在下一轮生效**

When an error occurs:
1. **立刻标记** - Explicitly identify what went wrong
2. **显式纠正** - State the correct approach clearly
3. **下一轮生效** - Verify the fix works before continuing

**Example (from today)**:
- ❌ Error: osascript long JS returns empty → 改用无分号单行写法
- ❌ Error: workflow切换双击不生效 → 改用 app.loadGraphData()
- ❌ Error: VHS_VideoCombine 缺 format 参数 → 添加 "format": "video/h264-mp4"

**Why it matters**: Small errors compound. Catching and fixing immediately prevents wasted time debugging stale issues.

---

## Safari+AppleScript Patterns

### 可靠写法 (confirmed)
- 返回字符串才能被AppleScript捕获
- 无分号写法比有分号更可靠
- 简单属性访问(document.title, app.graph)总是有效
- 复杂JS先测试单行

### app.graph 访问模式
```javascript
// 总是有效
app.graph._nodes.length
app.graph._nodes[i].type
nodes[i].widgets_values[0].slice(0, 80)

// 注意：osascript中返回字符串写法
"string"  // ✅
return "string"  // ⚠️ 有时失败
```

# 2026-04-21 学习汇报

## ChenYu ComfyUI API 核心掌握
- 端点: /api/prompt, /api/history, /api/view, /api/queue, /api/models
- CheckpointLoader → [MODEL, CLIP, VAE]
- 本地SD免费可用: 老王_Architecutral_MIX V0.3
- 关键: denoise=0.65(照片) / 0.45(CAD), steps≤20防Pod挂

## 已创建
- 24个设计工作流 (~/ComfyUI-Workflows/设计专用/)
- 中英文提示词库 (~/ComfyUI-Workflows/提示词库/)
- README完整文档

## 待解决
- Grsai API Key (grsai.com/zh)
- Hermes MINIMAX_CN_API_KEY
