#!/usr/bin/env python3
"""通过API生成厨房效果图"""
import requests
import json
import time
import os

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz13.chenyu.cn"

def queue_status():
    """检查队列状态"""
    try:
        r = requests.get(f"{COMFYUI_URL}/api/queue", verify=False, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def run_kitchen_workflow():
    """生成厨房效果图"""
    
    # 老王模型 kitchen prompt
    workflow = {
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "老王_Architecutral_MIX V0.3_V0.3.safetensors"}
        },
        "2": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "luxury modern kitchen, high-end marble countertops, professional stainless steel appliances, warm ambient lighting, elegant cabinetry, large kitchen island, interior design magazine quality, 4K", "clip": ["1", 1]}
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "blurry, low quality, distorted, ugly, watermark", "clip": ["1", 1]}
        },
        "4": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 1024, "width": 1024, "compression": 32}
        },
        "5": {
            "class_type": "KSampler",
            "inputs": {
                "seed": 8888,
                "steps": 25,
                "cfg": 8.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0]
            }
        },
        "6": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]}
        },
        "7": {
            "class_type": "SaveImage",
            "inputs": {"images": ["6", 0], "filename_prefix": "kitchen_luxury"}
        }
    }
    
    print("提交厨房生成任务...")
    resp = requests.post(
        f"{COMFYUI_URL}/api/prompt",
        json={"prompt": workflow},
        verify=False,
        timeout=30
    )
    result = resp.json()
    print(f"提交结果: {result}")
    return result.get("prompt_id")

def wait_and_download(prompt_id, output_dir, max_wait=180):
    """等待生成完成并下载"""
    interval = 5
    waited = 0
    
    while waited < max_wait:
        time.sleep(interval)
        waited += interval
        
        status = queue_status()
        running = status.get("queue_running", [])
        pending = status.get("queue_pending", [])
        
        print(f"等待中... ({waited}s) 运行:{len(running)} 等待:{len(pending)}")
        
        # 检查是否完成（队列为空或我们的任务不在队列中）
        if len(running) == 0 and len(pending) == 0:
            print("队列已完成")
            break
        
        # 检查我们的任务是否还在运行
        if running:
            for item in running:
                if len(item) >= 2 and item[1] == prompt_id:
                    print(f"任务仍在运行中...")
                    break
            else:
                print("任务可能已完成")
                break
    
    # 下载图片
    filename = "kitchen_luxury_00001_.png"
    output_path = os.path.join(output_dir, filename)
    
    print(f"下载图片: {filename}")
    try:
        resp = requests.get(
            f"{COMFYUI_URL}/api/view?filename={filename}&type=output",
            verify=False,
            timeout=30
        )
        if resp.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            print(f"✅ 已保存: {output_path}")
            return True
        else:
            print(f"下载失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"下载异常: {e}")
        return False

if __name__ == "__main__":
    output_dir = os.path.expanduser("~/Desktop/工作流图片")
    os.makedirs(output_dir, exist_ok=True)
    
    # 检查队列状态
    status = queue_status()
    print(f"队列状态: running={len(status.get('queue_running',[]))} pending={len(status.get('queue_pending',[]))}")
    
    if status.get("error"):
        print(f"❌ API错误: {status['error']}")
        exit(1)
    
    if len(status.get('queue_running', [])) > 0:
        print("⚠️ 队列仍有任务运行中")
    
    # 提交任务
    prompt_id = run_kitchen_workflow()
    if prompt_id:
        wait_and_download(prompt_id, output_dir)
    else:
        print("❌ 提交失败")