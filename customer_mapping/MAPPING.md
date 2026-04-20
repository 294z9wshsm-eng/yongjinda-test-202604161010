# 客户需求 → 工作流 映射表

> 最后更新：2026-04-20

---

## 一、需求分类

### A. 按场景分类

| 需求ID | 场景 | 客户描述 | 推荐工作流 |
|---|---|---|---|
| A1 | 新房毛坯 | "刚拿到毛坯房，想看看装修效果" | arch_maopi_style/text |
| A2 | 旧房翻新 | "老房子想重新装修" | indoor_style/text |
| A3 | 手绘稿出图 | "我有设计师的手绘图，能做成效果图吗" | arch_sketch / indoor_sketch |
| A4 | CAD出效果图 | "有施工图，想看实际效果" | arch_cad / cad_home |
| A5 | 多角度展示 | "一个房子给我看不同角度" | arch_multi / indoor_multi |
| A6 | 庭院花园 | "想看看院子怎么设计" | landscape_maopi / landscape_sketch |
| A7 | 客厅装修 | "帮我设计下客厅" | living |
| A8 | 厨房设计 | "厨房想装修成这样" | kitchen |
| A9 | 卧室装修 | "主卧怎么设计好" | bedroom |
| A10 | 书房设计 | "想要个书房" | study |
| A11 | 卫生间改造 | "卫生间想现代化一点" | bathroom |

### B. 按预算分类

| 预算档 | 需求 | 推荐工作流 |
|---|---|---|
| 基础 | 只要看个大概效果 | denoise 0.8, steps 20 |
| 标准 | 需要精细效果 | denoise 0.7, steps 25 |
| 高端 | 需要精装画册效果 | denoise 0.6, steps 35, dpm++ |

### C. 按紧迫度分类

| 紧迫度 | 场景 | 建议 |
|---|---|---|
| 紧急 | 明天要见客户 | 快速测试模式，512x512 |
| 正常 | 1-3天出图 | 标准质量，768x768 |
| 充裕 | 一周内交付 | 高清模式，1024x1024 |

---

## 二、话术模板

### 需求挖掘话术

```
"您是想看整体效果，还是局部调整？"
"有设计稿还是纯文字描述？"
"需要几个角度的效果图？"
"您偏好什么风格？现代简约/欧式/中式？"
"有参考图片吗？"
```

### 推荐话术

| 场景 | 推荐话术 |
|---|---|
| 新房毛坯 | "根据您毛坯房的情况，我推荐先用毛坯生成模式出几套方案，您选喜欢的风格我再细化。" |
| 手绘稿 | "您的手绘图扫描/拍照发我，我这边可以直接出效果图，1:1还原设计。" |
| CAD图 | "您的CAD图发我，可以直接出施工图级别的效果图，精确还原。" |
| 多角度 | "一个方案我给您出4-6个角度，客厅、卧室、厨房都有，让您全面看。" |
| 紧急需求 | "时间紧的话我先给您出快速版确认效果，确认后10分钟出高清版。" |

---

## 三、快速匹配表

### 输入关键词 → 工作流

```
"毛坯" / "新房" / "还没装修"
  → arch_maopi_style.json / indoor_style.json

"手绘" / "草图" / "设计师画的"
  → arch_sketch_style.json / indoor_sketch_style.json

"CAD" / "施工图" / "蓝图"
  → arch_cad.json / cad_home.json

"多角度" / "多个视角" / "不同角度"
  → arch_multi.json / indoor_multi.json

"客厅" / "起居室"
  → living.json

"厨房" / "开放式厨房"
  → kitchen.json

"卧室" / "主卧" / "次卧"
  → bedroom.json

"书房" / "书柜" / "办公"
  → study.json

"卫生间" / "浴室" / "厕所"
  → bathroom.json

"庭院" / "花园" / "院子" / "景观"
  → landscape_maopi_style.json / landscape_sketch_style.json

"全景" / "360" / "全景图"
  → k_panorama.json

"删除" / "去掉" / "修掉"
  → k_delete_object.json

"光影" / "光线" / "调光"
  → k_light_shadow.json

"日夜" / "白天晚上" / "切换"
  → k_day_night.json

"材质" / "质感" / "纹理"
  → k_model_material.json
```

---

## 四、工作流参数推荐

### A. 毛坯生成（快速）
```python
{
    "steps": 25,
    "cfg": 8.0,
    "denoise": 0.7,
    "sampler": "euler",
    "size": "1024x1024"
}
```

### B. 细节增强（精装）
```python
{
    "steps": 35,
    "cfg": 8.5,
    "denoise": 0.6,
    "sampler": "dpm++_2m_karras",
    "size": "1024x1024"
}
```

### C. 手绘转真实
```python
{
    "steps": 25,
    "cfg": 8.0,
    "denoise": 0.75,
    "sampler": "euler_a",
    "size": "1024x1024"
}
```

### D. 多角度一致性
```python
{
    "steps": 25,
    "cfg": 8.0,
    "denoise": 0.65,
    "sampler": "euler",
    "size": "1024x1024",
    "note": "固定seed保持一致性"
}
```

---

## 五、交付标准

| 档位 | 交付内容 | 时间 |
|---|---|---|
| 快速 | 2张快速测试图 | 5分钟 |
| 标准 | 4张标准效果图 + 1张细节 | 15分钟 |
| 高端 | 6张高清图 + 多角度 + 细节 | 30分钟 |

---

## 六、注意事项

1. **客户说"差不多就行"** → 用快速模式先出图
2. **客户说"要精细的"** → 用高清模式
3. **客户发了手绘图** → 优先用sketch系列
4. **客户要"高级感"** → 加"豪华"到提示词
5. **客户说"现代简约"** → 直接用对应工作流

---

## 七、快捷调用

```python
from customer_mapping import match_workflow

# 根据客户描述匹配工作流
result = match_workflow("我有设计师的手绘图，想看效果图")
# 返回: ("手绘转真实", "arch_sketch_style.json", {参数})
```
