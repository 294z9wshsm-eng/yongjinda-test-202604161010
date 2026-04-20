#!/usr/bin/env python3
"""
ComfyUI 工作流自动化学习脚本包
包含：v3(已知位置)、full(自动扫描)、quick(快速补漏)
"""

import subprocess
import time
import json
import os
import sys

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"


def run_osascript(script):
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()


def ensure_comfyui():
    script = 'tell application "Safari" to URL of front document'
    url = run_osascript(script)[1] if run_osascript(script)[0] else ""
    if "chenyu.cn" not in url:
        run_osascript(f'tell application "Safari" to set URL of front document to "{COMFYUI_URL}"')
        time.sleep(3)


def reload_page():
    """刷新页面"""
    run_osascript('''tell application "Safari"
        do JavaScript "window.location.reload();" in front document
    end tell''')
    time.sleep(6)


def expand_tree():
    """展开主文件夹"""
    run_osascript('''tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        
        for(var el of all) {
            var text = el.textContent || '';
            if(text.includes('超强NanoPro系列31') && text.length < 100) {
                var rect = el.getBoundingClientRect();
                for(var i = 0; i < 80; i++) {
                    el.dispatchEvent(new MouseEvent('mousedown', {
                        view: window, bubbles: true, cancelable: true, button: 0,
                        clientX: rect.x + 25, clientY: rect.y + rect.height/2
                    }));
                }
                break;
            }
        }
        " in front document
    end tell''')
    time.sleep(2)


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


def scan_workflows():
    """扫描当前可见工作流"""
    script = '''tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        var results = [];
        
        for(var el of all) {
            var text = el.textContent || '';
            var rect = el.getBoundingClientRect();
            if(text.includes('.json') && rect.width > 0 && rect.y > 0) {
                var filename = text.match(/([^.]+\\.json)/)?.[1] || text.substring(0, 30);
                results.push({
                    y: Math.round(rect.y),
                    filename: filename,
                    text: text.substring(0, 60)
                });
            }
        }
        
        results.sort(function(a, b) { return a.y - b.y; });
        JSON.stringify(results, null, 2);
        " in front document
    end tell'''
    
    success, output = run_osascript(script)
    if success and output:
        try:
            return json.loads(output)
        except:
            return []
    return []


# ========== 已知工作流位置 ==========
KNOWN_WORKFLOWS = [
    # (Y位置, 文件名)
    (322, "nano_pro_arch_multi.json"),
    (391, "nano_pro_arch_maopi_style.json"),
    (439, "nano_pro_arch_maopi_text.json"),
    (487, "nano_pro_arch_cad.json"),
    (535, "nano_pro_arch_sketch_style.json"),
    (583, "nano_pro_arch_sketch_text.json"),
    (665, "nano_pro_landscape_maopi_style.json"),
    (713, "nano_pro_landscape_maopi_text.json"),
    (761, "nano_pro_landscape_sketch_style.json"),
    (809, "nano_pro_landscape_sketch_text.json"),
    (905, "nano_pro_kitchen.json"),
    (953, "nano_pro_living.json"),
    (1001, "nano_pro_study.json"),
    (1049, "nano_pro_bathroom.json"),
    (1097, "nano_pro_bedroom.json"),
    (1193, "nano_pro_cad_home.json"),
]


def learn_known():
    """学习已知Y位置的工作流"""
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"已有: {len(existing)}")
    
    print("\n刷新页面...")
    reload_page()
    
    print("展开树...")
    expand_tree()
    
    total = 0
    saved = 0
    
    for y, filename in KNOWN_WORKFLOWS:
        if filename in existing:
            continue
        
        print(f"\n[{y}] {filename}")
        click_at_y(y, 50)
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
            print(f"  ✗ 获取失败")
        
        total += 1
        time.sleep(1)
    
    print(f"\n完成! 学习{total}, 新增{saved}")


def learn_auto():
    """自动扫描学习"""
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"已有: {len(existing)}")
    
    print("\n刷新页面...")
    reload_page()
    
    print("展开树...")
    expand_tree()
    
    # 重置滚动
    run_osascript('''tell application "Safari"
        do JavaScript "
        var sidebar = document.querySelector('[class*=sidebar]');
        if(sidebar) sidebar.scrollTop = 0;
        " in front document
    end tell''')
    time.sleep(0.5)
    
    total = 0
    saved = 0
    
    # 扫描3轮
    for round_num in range(3):
        print(f"\n=== 第{round_num+1}轮扫描 ===")
        
        items = scan_workflows()
        print(f"发现 {len(items)} 个")
        
        for item in items:
            y = item['y']
            filename = item['filename']
            
            if filename in existing:
                continue
            
            print(f"\n[{y}] {filename}")
            click_at_y(y)
            time.sleep(1)
            
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
                print(f"  ✗ 获取失败")
            
            total += 1
            time.sleep(0.8)
        
        # 滚动继续
        run_osascript('''tell application "Safari"
            do JavaScript "
            var sidebar = document.querySelector('[class*=sidebar]');
            if(sidebar) sidebar.scrollTop += 400;
            " in front document
        end tell''')
        time.sleep(0.5)
    
    print(f"\n完成! 学习{total}, 新增{saved}")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 comfyui_automator.py [known|auto]")
        print("  known - 学习已知Y位置的工作流")
        print("  auto  - 自动扫描学习")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "known":
        print("=" * 50)
        print("ComfyUI 工作流学习 - 已知位置模式")
        print("=" * 50)
        ensure_comfyui()
        learn_known()
    elif cmd == "auto":
        print("=" * 50)
        print("ComfyUI 工作流学习 - 自动扫描模式")
        print("=" * 50)
        ensure_comfyui()
        learn_auto()
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
