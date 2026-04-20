#!/usr/bin/env python3
"""
ComfyUI 工作流学习自动化 v3
正确的Y位置 - 展开后的树
"""

import subprocess
import time
import json
import os

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"

# 从展开的树结构读取的正确Y位置
WORKFLOWS = [
    (322, "nano_pro_arch_multi.json", 40),
    (391, "nano_pro_arch_maopi_style.json", 40),
    (439, "nano_pro_arch_maopi_text.json", 40),
    (487, "nano_pro_arch_cad.json", 40),
    (535, "nano_pro_arch_sketch_style.json", 40),
    (583, "nano_pro_arch_sketch_text.json", 40),
    (665, "nano_pro_landscape_maopi_style.json", 40),
    (713, "nano_pro_landscape_maopi_text.json", 40),
    (761, "nano_pro_landscape_sketch_style.json", 40),
    (809, "nano_pro_landscape_sketch_text.json", 40),
    (905, "nano_pro_kitchen.json", 40),
    (953, "nano_pro_living.json", 40),
    (1001, "nano_pro_study.json", 40),
    (1049, "nano_pro_bathroom.json", 40),
    (1097, "nano_pro_bedroom.json", 40),
    (1193, "nano_pro_cad_home.json", 40),
]

def run_osascript(script):
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()

def ensure_comfyui():
    script = 'tell application "Safari" to URL of front document'
    url = run_osascript(script)[1] if run_osascript(script)[0] else ""
    if "chenyu.cn" not in url:
        run_osascript(f'tell application "Safari" to set URL of front document to "{COMFYUI_URL}"')
        time.sleep(3)

def reset_scroll():
    run_osascript('''tell application "Safari"
        do JavaScript "
        var sidebar = document.querySelector('[class*=sidebar]');
        if(sidebar) sidebar.scrollTop = 0;
        " in front document
    end tell''')

def click_at_y(y, clicks=40):
    run_osascript(f'''tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        
        for(var el of all) {{
            var text = el.textContent || '';
            var rect = el.getBoundingClientRect();
            if(Math.abs(rect.y - {y}) < 5 && text.includes('.json')) {{
                for(var i = 0; i < {clicks}; i++) {{
                    el.dispatchEvent(new MouseEvent('mousedown', {{
                        view: window, bubbles: true, cancelable: true, button: 0,
                        clientX: rect.x + rect.width/2, clientY: rect.y + rect.height/2
                    }}));
                }}
                break;
            }}
        }}
        " in front document
    end tell''')

def get_workflow():
    run_osascript('''tell application "Safari"
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
    end tell''')
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return result.stdout

def save(workflow_json, filename):
    try:
        data = json.loads(workflow_json)
        nodes = data.get('nodes', [])
        filepath = os.path.join(COMFYUI_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(nodes)
    except:
        return 0

def main():
    print("=" * 60)
    print("ComfyUI 工作流学习自动化 v3")
    print("=" * 60)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    print("\n初始化...")
    ensure_comfyui()
    reset_scroll()
    
    # 重置滚动位置
    run_osascript('''tell application "Safari"
        do JavaScript "window.location.reload();" in front document
    end tell''')
    print("刷新页面...")
    time.sleep(5)
    
    # 已有文件
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"已有: {len(existing)}")
    
    total = 0
    saved = 0
    
    for y_pos, filename, clicks in WORKFLOWS:
        if filename in existing:
            print(f"\n跳过(已有): {filename}")
            continue
        
        print(f"\n>>> [{y_pos}] {filename}")
        click_at_y(y_pos, clicks)
        time.sleep(1.2)
        
        wf = get_workflow()
        if wf and len(wf) > 1000:
            nodes = save(wf, filename)
            if nodes:
                print(f"  ✓ {nodes}节点")
                saved += 1
                existing.add(filename)
            else:
                print(f"  ✗ 保存失败")
        else:
            print(f"  ✗ 获取失败:{len(wf) if wf else 0}")
        
        total += 1
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"完成! 学习{total}, 新增{saved}")
    print("=" * 60)

if __name__ == "__main__":
    main()
