#!/usr/bin/env python3
"""
ComfyUI 工作流学习自动化 v4 (优化版)
- 先展开树 + 等待
- 一次性扫描所有可见工作流
- 按Y位置批量学习
"""

import subprocess
import time
import json
import os

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
                for(var i = 0; i < 60; i++) {
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


def scan_workflows():
    """扫描当前可见的所有工作流"""
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


def scroll_and_scan():
    """滚动并扫描"""
    results = []
    
    # 重置到顶部
    run_osascript('''tell application "Safari"
        do JavaScript "
        var sidebar = document.querySelector('[class*=sidebar]');
        if(sidebar) sidebar.scrollTop = 0;
        " in front document
    end tell''')
    time.sleep(0.5)
    
    # 扫描多轮，每轮滚动一些
    for _ in range(15):
        items = scan_workflows()
        for item in items:
            if item not in results:
                results.append(item)
        
        # 滚动
        run_osascript('''tell application "Safari"
            do JavaScript "
            var sidebar = document.querySelector('[class*=sidebar]');
            if(sidebar) sidebar.scrollTop += 400;
            " in front document
        end tell''')
        time.sleep(0.5)
    
    # 去重
    seen = set()
    unique = []
    for item in results:
        key = item['y']
        if key not in seen:
            seen.add(key)
            unique.append(item)
    
    return unique


def main():
    print("=" * 60)
    print("ComfyUI 工作流学习自动化 v4 (优化版)")
    print("=" * 60)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    # 已有文件
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"\n已有: {len(existing)}")
    
    print("\n1. 刷新页面...")
    reload_page()
    
    print("2. 展开树...")
    expand_tree()
    
    print("3. 扫描工作流...")
    workflows = scan_workflows()
    print(f"   发现 {len(workflows)} 个工作流")
    
    if not workflows:
        print("   没有发现，尝试直接学习已有Y位置...")
        # 使用已知的Y位置
        known = [
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
        workflows = [{"y": y, "filename": f} for y, f in known]
        print(f"   使用已知列表: {len(workflows)} 个")
    
    # 学习
    total = 0
    saved = 0
    
    print(f"\n4. 开始学习 {len(workflows)} 个工作流...")
    
    for item in workflows:
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
    
    print("\n" + "=" * 60)
    print(f"完成! 学习{total}, 新增{saved}")
    print("=" * 60)


if __name__ == "__main__":
    main()
