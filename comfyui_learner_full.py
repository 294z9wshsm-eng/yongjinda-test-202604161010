#!/usr/bin/env python3
"""
ComfyUI 工作流全自动化学习 v4
简化版 - 用之前验证成功的 p-tree-node 选择器
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


def reset_scroll():
    run_osascript('''tell application "Safari"
        do JavaScript "
        var sidebar = document.querySelector('[class*=sidebar]');
        if(sidebar) sidebar.scrollTop = 0;
        window.scrollTo(0, 0);
        " in front document
    end tell''')


def get_items():
    """获取 p-tree-node 中的 .json 项"""
    script = '''tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        var results = [];
        
        for(var el of all) {
            var text = el.textContent || '';
            var rect = el.getBoundingClientRect();
            if(text.includes('.json') && rect.width > 0 && rect.y > 0 && rect.y < 2000) {
                var filename = text.match(/([^.]+\\.json)/)?.[1] || text.substring(0, 30);
                results.push({y: Math.round(rect.y), filename: filename, text: text.substring(0, 50)});
            }
        }
        
        results.sort(function(a, b) { return a.y - b.y; });
        JSON.stringify(results.slice(0, 25), null, 2);
        " in front document
    end tell'''
    
    success, output = run_osascript(script)
    if success and output:
        try:
            return json.loads(output)
        except:
            return []
    return []


def click_at_y(y, clicks=35):
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


def scroll(offset):
    run_osascript(f'''tell application "Safari"
        do JavaScript "
        var sidebar = document.querySelector('[class*=sidebar]');
        if(sidebar) sidebar.scrollTop += {offset};
        " in front document
    end tell''')


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
    print("ComfyUI 工作流全自动化学习 v4")
    print("=" * 60)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    print("\n初始化...")
    ensure_comfyui()
    reset_scroll()
    
    # 已有文件
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"已有: {len(existing)}")
    
    total = 0
    saved = 0
    
    for rnd in range(8):
        print(f"\n=== 第{rnd+1}轮 ===")
        items = get_items()
        print(f"发现 {len(items)} 项")
        
        if not items:
            scroll(400)
            time.sleep(0.5)
            items = get_items()
        
        if not items:
            continue
        
        for item in items:
            fn = item['filename']
            y = item['y']
            
            if fn in existing:
                continue
            
            print(f"\n[{y}] {fn}")
            click_at_y(y)
            time.sleep(1.2)
            
            wf = get_workflow()
            if wf and len(wf) > 1000:
                nodes = save(wf, fn)
                if nodes:
                    print(f"  ✓ {nodes}节点")
                    saved += 1
                    existing.add(fn)
                else:
                    print(f"  ✗ 保存失败")
            else:
                print(f"  ✗ 获取失败:{len(wf) if wf else 0}")
            
            total += 1
            time.sleep(0.8)
        
        scroll(400)
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"完成! 学习{total}, 新增{saved}")
    print("=" * 60)


if __name__ == "__main__":
    main()
