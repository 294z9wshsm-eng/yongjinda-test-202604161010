#!/usr/bin/env python3
"""
ComfyUI 工作流学习自动化脚本 v2
使用 osascript + JavaScript 模拟点击

原理：
1. 用 osascript 获取 Safari 窗口位置
2. 用 osascript 执行 JavaScript 点击侧边栏元素
3. 用 osascript 执行 JavaScript 获取 localStorage workflow
4. 保存到文件
"""

import subprocess
import time
import json
import os
import sys

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"


def run_osascript(script):
    """执行 osascript 命令"""
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip(), result.stderr


def js_click(safari_win, target_y, click_count=30):
    """通过 JavaScript 点击 Safari 侧边栏元素"""
    script = f'''
    tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        
        for(var el of all) {{
            var text = el.textContent || '';
            var rect = el.getBoundingClientRect();
            if(Math.abs(rect.y - {target_y}) < 5) {{
                for(var i = 0; i < {click_count}; i++) {{
                    el.dispatchEvent(new MouseEvent('mousedown', {{
                        view: window,
                        bubbles: true,
                        cancelable: true,
                        button: 0,
                        clientX: rect.x + rect.width/2,
                        clientY: rect.y + rect.height/2
                    }}));
                }}
                break;
            }}
        }}
        " in front document
    end tell
    '''
    run_osascript(script)


def js_get_workflow():
    """通过 JavaScript 获取 localStorage workflow"""
    script = '''
    tell application "Safari"
        do JavaScript "
        var w = localStorage.getItem('workflow');
        var ta = document.createElement('textarea');
        ta.value = w;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        'done';
        " in front document
    end tell
    '''
    success, _, _ = run_osascript(script)
    if success:
        result = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return result.stdout
    return None


def js_get_safari_title():
    """获取 Safari 当前窗口标题"""
    script = 'tell application "Safari" to return name of window 1'
    _, title, _ = run_osascript(script)
    return title


def save_workflow(workflow_json, filename):
    """保存工作流到文件"""
    try:
        data = json.loads(workflow_json)
        nodes = data.get('nodes', [])
        filepath = os.path.join(COMFYUI_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(nodes)
    except Exception as e:
        print(f"  错误: {e}")
        return 0


def learn_single_workflow(target_y, filename, click_count=40):
    """学习单个工作流"""
    print(f"\n>>> 学习: {filename} (Y={target_y})")
    
    # 1. 点击
    print(f"  点击侧边栏...")
    js_click(None, target_y, click_count)
    time.sleep(1.5)
    
    # 2. 检查标题
    title = js_get_safari_title()
    print(f"  窗口: {title}")
    
    # 3. 获取工作流
    print(f"  获取工作流...")
    workflow_json = js_get_workflow()
    
    if workflow_json and len(workflow_json) > 1000:
        nodes = save_workflow(workflow_json, filename)
        print(f"  ✓ 保存成功! ({nodes}节点)")
        return True
    else:
        print(f"  ✗ 获取失败或内容太短: {len(workflow_json) if workflow_json else 0}")
        return False


def learn_batch(workflows):
    """批量学习工作流"""
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    success = 0
    for y_pos, filename, clicks in workflows:
        if learn_single_workflow(y_pos, filename, clicks):
            success += 1
        time.sleep(2)
    
    return success


def main():
    """主函数"""
    print("=" * 60)
    print("ComfyUI 工作流学习自动化 v2")
    print("=" * 60)
    
    # 先确保 Safari 打开正确的页面
    print("\n检查 Safari 页面...")
    script = 'tell application "Safari" to URL of front document'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    current_url = result.stdout.strip() if result.returncode == 0 else ""
    
    if "chenyu.cn" not in current_url:
        print(f"当前页面: {current_url}")
        print("跳转到 ComfyUI...")
        subprocess.run(["osascript", "-e", 
            'tell application "Safari" to set URL of front document to "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"'
        ])
        time.sleep(3)
    else:
        print(f"✓ 已在 ComfyUI 页面")
    
    # 重置侧边栏滚动位置
    subprocess.run(["osascript", "-e", '''
        tell application "Safari"
            do JavaScript "
            var sidebar = document.querySelector('[class*=sidebar]');
            if(sidebar) sidebar.scrollTop = 0;
            " in front document
        end tell
    '''])
    
    # 要学习的工作流列表
    # (Y位置, 文件名, 点击次数)
    workflows = [
        # --- 未完成的 ---
        (280, "nano_pro_indoor_multi.json", 40),
        (349, "nano_pro_sketch_indoor_style.json", 40),
        (397, "nano_pro_sketch_indoor_text.json", 40),
        (445, "nano_pro_extract_soft.json", 40),
        (493, "nano_pro_extract_hard.json", 40),
        # --- 额外系列 ---
        (957, "k_model_material.json", 50),
        (1005, "k_delete_object.json", 50),
        (1053, "k_light_shadow.json", 50),
        (1101, "k_panorama.json", 50),
        (1149, "k_maopi_direct.json", 50),
        (1197, "k_day_night.json", 50),
        (1245, "qwen_multiangle.json", 50),
        (1293, "qwen_single_edit.json", 50),
        (1362, "qwen_dual_edit.json", 50),
    ]
    
    print(f"\n共 {len(workflows)} 个工作流待学习")
    print("开始自动学习...")
    
    success = learn_batch(workflows)
    
    print("\n" + "=" * 60)
    print(f"完成! 成功 {success}/{len(workflows)} 个")
    print("=" * 60)


if __name__ == "__main__":
    main()
