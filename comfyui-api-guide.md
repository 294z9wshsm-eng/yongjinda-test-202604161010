# ComfyUI API 工作流模板

> 大条学会的高效工作流模板，节约 API 调用
> Last updated: 2026-04-19

---

## ✅ API 调用关键发现

### 1. 图片下载路径
```
GET /api/view?filename={文件名}&type={output|temp|input}
```

### 2. SaveImage 正确格式
```json
"images": ["6", 0]  // 不是 [["6", 0]]，直接是 [node_id, slot_index]
```

### 3. CLIPTextEncode 正确链接
```json
"clip": ["1", 1]  // 从 CheckpointLoader 的第1个输出(CLIP)连接
```

### 4. KSampler 必需参数
```json
{
  "seed": 12345,
  "steps": 20,
  "cfg": 8.0,
  "sampler_name": "euler",
  "scheduler": "normal",
  "denoise": 1.0,
  "model": ["1", 0],
  "positive": ["2", 0],
  "negative": ["3", 0],
  "latent_image": ["4", 0]
}
```

---

## 📝 基础文生图工作流（高效版）

```python
import requests
import json

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
API_KEY = ""  # 如果需要

def run_workflow(prompt_text, negative_text="模糊，低质量", seed=12345, steps=20):
    """运行文生图工作流"""
    
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "老王_Architecutral_MIX V0.3_V0.3.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode", 
            "inputs": {"text": prompt_text, "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": negative_text, "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 512, "width": 512}  # 低分辨率测试
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed, "steps": steps, "cfg": 8.0,
                "sampler_name": "euler", "scheduler": "normal",
                "denoise": 1.0, "model": ["1", 0],
                "positive": ["2", 0], "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage", 
            "inputs": {"images": ["6", 0], "filename_prefix": "daztiao_result"}
        }
    }
    
    # 提交工作流
    resp = requests.post(
        f"{COMFYUI_URL}/api/prompt",
        json={"prompt": workflow},
        verify=False
    )
    return resp.json()["prompt_id"]

def download_image(filename, output_path="result.png"):
    """下载生成的图片"""
    resp = requests.get(
        f"{COMFYUI_URL}/api/view?filename={filename}&type=output",
        verify=False
    )
    with open(output_path, 'wb') as f:
        f.write(resp.content)
    return output_path
```

---

## 🎨 进阶工作流

### 图生图（Img2Img）
在基础工作流上，把 `EmptyLatentImage` 替换为：
```json
"4": {
    "class_type": "LoadImage",
    "inputs": {"image": "your_image.png"}
},
"5": {
    "class_type": "VAEEncode",
    "inputs": {"pixels": ["4", 0], "vae": ["1", 2]}
}
```

### 高清放大（SDXL）
```json
"8": {
    "class_type": "ImageUpscaleWithModel",
    "inputs": {"upscale_model": ["1", 0], "image": ["7", 0]}
}
```

---

## 💡 节约 API 技巧

1. **先用低分辨率测试**（512x512），确认满意后再用高分辨率
2. **steps 不必太高**（20-25 足够，不需要 50+）
3. **batch_size=1** 节省内存
4. **用 seed 控制** 便于复现
5. **Cache 是你的朋友** - 相同节点会被缓存

---

## 🔧 ChenYu 可用模型

- 老王_Architecutral_MIX V0.3（建筑室内）
- 陈诺-kaka通用模型库/ARC空间设计师XL
- 比鲁斯建筑室内通用大模型SD1.5
