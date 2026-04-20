# ComfyUI 学习路线

> 大条学 ComfyUI，云端跑图+视频
> Last updated: 2026-04-19

---

## 一、ComfyUI 是什么

**模块化视觉 AI 引擎**，通过"节点/流程图"界面设计和执行 Stable Diffusion 流水线。

- 🎨 **图片模型**：SDXL、Flux、SD3、HiDream、Qwen Image、Hunyuan Image...
- 🎬 **视频模型**：Hunyuan Video、Wan 2.1/2.2、LTX-Video、Mochi、Stable Video Diffusion...
- 🔊 **音频/3D**：Stable Audio、Hunyuan3D 2.0...

---

## 二、核心概念

### 节点（Nodes）
每个节点负责一个功能，如：
- `Load Checkpoint` — 加载模型
- `CLIP Text Encode` — 编码提示词
- `KSampler` — 执行采样生成
- `Save Image` — 保存图片

### 流程（Workflow）
节点连线组成完整流程：
```
模型加载 → 文字编码 → 采样器 → 图片解码 → 保存
```

### 关键节点速查

| 节点 | 用途 |
|---|---|
| `CheckpointLoader` | 加载 SD/Flux 模型 |
| `CLIPTextEncode` | 把提示词转成向量 |
| `KSampler` / `SamplerCustom` | 实际生成图片 |
| `VAEDecode` | 把潜在空间转成图片 |
| `SaveImage` | 保存到文件 |
| `VideoCombine` | 图片序列合成视频 |

---

## 三、工作流模板（官方）

- 图片工作流：https://comfy.org/workflows
- 官方示例：https://comfyanonymous.github.io/ComfyUI_examples/

### 常用图片工作流
1. **SDXL Base** — 基础文生图
2. **Flux Dev** — 快速高质量（需 16GB+ VRAM）
3. **SDXL + Refiner** — 高分辨率双阶段
4. **IP-Adapter** — 图片参考风格

### 常用视频工作流
1. **Hunyuan Video** — 腾讯混元，电商/广告强
2. **Wan 2.1** — 风格多样，AI味道淡
3. **LTX-Video** — 短片段，快
4. **Mochi** — 高质量，运动自然

---

## 四、云端部署

### ChenYu（晨羽智云）
- 地址：https://www.chenyu.cn
- 邀请码：`ML46JZ`（首充优惠）
- 算力卡：`50VS50`（新用户）、`AIKAKA`（充值30得45）
- 推荐用 **KAKA-ComfyUI-2.0** 镜像

### Comfy.org 官方云
- https://www.comfy.org/cloud
- 官方托管，无需配置

---

## 五、大条能帮老大做的

### 1. 写工作流 JSON
根据需求，大条可以写完整工作流，上传云端直接用。

### 2. 批量自动化脚本
批量生成图片/视频的 Python 脚本。

### 3. API 调用
用云端 API 自动化跑工作流，不需手动操作界面。

### 4. 工作流优化
根据云端算力配置，优化节点和内存使用。

---

## 六、学习计划

### 第一阶段：图片生成
- [ ] 学基础文生图工作流（SDXL）
- [ ] 学图生图 / Img2Img
- [ ] 学 ControlNet（骨骼/深度/线条控制）

### 第二阶段：视频生成
- [ ] 学 Hunyuan Video 工作流
- [ ] 学 Wan 2.1 工作流
- [ ] 学镜头控制 / 运镜

### 第三阶段：高级技巧
- [ ] Lora 模型加载使用
- [ ] ComfyUI API 批量自动化
- [ ] 工作流模板整理

---

## 七、ChenYu 云端 ComfyUI 实例

### 实例信息
- **URL**: https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn
- **镜像**: KAKA进阶训练专属镜像
- **GPU**: RTX 4080 SUPER 16GB VRAM ✅
- **ComfyUI**: v0.6.0
- **PyTorch**: 2.4.1+cu124
- **RAM**: 540GB（474GB可用）
- **模板版本**: 0.7.64

### 已安装自定义节点
- **YCNode** (ComfyUI-YCNodes) - 图片、遮罩、LoRA选择器、文本处理
- **tbox** (ComfyUI-tbox) - 人脸融合、视频、图片工具
- **JPS Nodes** - SDXL设置、ControlNet、IP-Adapter、InstantID
- **AdvancedRefluxControl** - StyleModel

### 可用 LoRA（室内设计为主）
- FLUX/室内光线控制器
- FLUX/现代极简风格
- FLUX/建筑外观
- FLUX/民宿风格
- FLUX/意向极简平层
- FLUX/室内欧式
- FLUX/现卧室
- FLUX/酒店
- FLUX/古典园林
- 服装店_V2.0
- 极简住户风格...

### 已安装模型检查点
从 object_info API 获取到大量输出文件，包括：
- SDXL Base、SDXL Turbo
- 各种 RealESRGAN、OmniSR 超分辨率模型

### API 端点
- `/api/object_info` - 所有节点定义 ✅ 已获取
- `/api/system_stats` - 系统状态 ✅ 已获取
- `/api/queue` - 队列状态
- `/api/history` - 运行历史

## 八、工作流学习成果

### KAKA 训练营工作流定位

大条成功导出了云端 ComfyUI 的"全案制作"工作流，已存档至 `~/ComfyUI-Workflows/`

#### 工作流名称
（全案制作）分析+平面+套图+视频全流程

#### 工作流核心节点（15种，共103个节点）

| 节点 | 数量 | 用途 |
|---|---|---|
| TextInput_ | 17 | 文字输入 |
| ShowText | 11 | 显示文字 |
| Comfly_api_set | 11 | API设置 |
| Comfly_nano_banana2_edit | 9 | 图片编辑（平面图→立体效果图） |
| GetNode | 9 | 获取数据 |
| SaveImage | 9 | 保存图片 |
| LoadImage | 8 | 加载图片 |
| Comfly_Googel_Veo3 | 7 | Google Veo3 视频生成 |
| SaveVideo | 7 | 保存视频 |
| ComflyGeminiAPI | 2 | Gemini API 分析 |
| GetVideoComponents | 1 | 获取视频组件 |
| SetNode | 1 | 设置数据 |
| LoadVideo | 1 | 加载视频 |
| Fast Groups Bypasser | 1 | 组切换 |

#### 完整工作流流程

```
1. LoadImage(加载平面图)
   ↓
2. ComflyGeminiAPI(AI分析平面图)
   ↓ (生成详细描述文本)
3. TextInput_(输入/编辑提示词)
   ↓ (多段分区描述)
4. Comfly_nano_banana2_edit(平面图→3D效果图)
   ↓
5. Comfly_Googel_Veo3(生成视频)
   ↓
6. SaveImage + SaveVideo(保存结果)
```

#### 实际使用示例

提示词内容：
"把我这张平面图改成人视角的立体写实效果"

描述示例：
"公园南侧：活力与传统交织的入口区。转向左侧（西边），看到一个非常独特的圆形嵌套广场。它由多层圆环状的白色路径和绿地组成，从人的视角看，这像是一个富有节奏感的迷宫..."

#### 自定义节点说明

- **Comfly_nano_banana2_edit** - KAKA自研，将平面图转3D效果图
- **Comfly_Googel_Veo3** - 集成Google Veo3视频生成
- **ComflyGeminiAPI** - 集成Gemini进行AI分析
- **Comfly_api_set** - API密钥和配置管理
这是一个**室内设计/建筑设计**专用的 ComfyUI 工作流：
- 输入：参考图片 + 设计要求
- 输出：装修效果图、建筑效果图
- 核心节点：YCNode 图片处理、JPS Settings 精确控制

### 已学会的节点类型
1. **LoadCheckpoint** - 加载 SDXL/Flux 模型
2. **CLIPTextEncode** - 编码提示词
3. **KSampler** - 采样生成
4. **VAEDecode** - 潜在空间→图片
5. **YCNode 特有**：
   - `YC_Image_Save` - 自定义图片保存
   - `LoadImagesFromFolder` - 文件夹批量加载
   - `ImageBlendResize` - 图片混合/叠加
   - `MaskTopNFilter` - 遮罩过滤
   - `YC_SuperSelector` - LoRA 超级选择器

### 典型工作流结构
```
LoadCheckpoint(模型)
  → CLIPTextEncode(正向提示词)
  → CLIPTextEncode(负向提示词)
  → KSampler(采样器)
  → VAEDecode(解码)
  → YC_Image_Save(保存)
```

## 九、参考链接

- ComfyUI 官网：https://comfy.org
- 官方文档：https://docs.comfy.org
- 工作流广场：https://comfy.org/workflows
- GitHub：https://github.com/comfyanonymous/ComfyUI
- ChenYu 平台：https://www.chenyu.cn
