#!/usr/bin/env python3
"""
ComfyUI工作流学习 - Chrome版本
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


def open_chrome():
    """打开Chrome并导航到ComfyUI"""
    run_osascript('tell application "Google Chrome" to activate')
    time.sleep(0.5)
    
    # 检查当前标签页
    script = 'tell application "Google Chrome" to return URL of active tab of window 1'
    success, url = run_osascript(script)
    
    if "chenyu.cn" not in url:
        print(f"打开ComfyUI...")
        run_osascript(f'tell application "Google Chrome" to open location "{COMFYUI_URL}"')
        time.sleep(5)
    else:
        print(f"已在ComfyUI页面")


def get_tree_count():
    """获取树节点数量"""
    script = '''tell application "Google Chrome"
        execute JavaScript "document.querySelectorAll('.p-tree-node').length" in active tab of window 1
    end tell'''
    success, output = run_osascript(script)
    try:
        return int(float(output.strip())) if output.strip() else 0
    except:
        return 0


def get_json_items():
    """获取所有.json工作流项"""
    script = '''tell application "Google Chrome"
        execute JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        var results = [];
        for(var el of all) {
            var text = el.textContent || '';
            var rect = el.getBoundingClientRect();
            if(text.includes('.json') && rect.width > 0 && rect.y > 0) {
                results.push({
                    y: Math.round(rect.y),
                    text: text.substring(0, 50)
                });
            }
        }
        results.sort(function(a, b){ return a.y - b.y; });
        JSON.stringify(results);
        " in active tab of window 1
    end tell'''
    success, output = run_osascript(script)
    if success and output:
        try:
            return json.loads(output.strip())
        except:
            return []
    return []


def reload_page():
    """刷新页面"""
    run_osascript('tell application "Google Chrome" to reload active tab of window 1')
    time.sleep(6)


def expand_tree():
    """展开主文件夹"""
    script = '''tell application "Google Chrome"
        execute JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        for(var el of all) {
            var text = el.textContent || '';
            if(text.includes('超强NanoPro系列31') && text.length < 100) {
                var rect = el.getBoundingClientRect();
                console.log('Found at y=' + rect.y);
                for(var i=0; i<100; i++) {
                    el.dispatchEvent(new MouseEvent('mousedown', {
                        view: window, bubbles: true, cancelable: true, button: 0,
                        clientX: rect.x + 25, clientY: rect.y + rect.height/2
                    }));
                }
                break;
            }
        }
        " in active tab of window 1
    end tell'''
    run_osascript(script)
    time.sleep(2)


def click_at_y(y, clicks=50):
    """点击指定Y位置"""
    js = f'''
    var all = document.querySelectorAll('.p-tree-node');
    for(var el of all) {{
        var text = el.textContent || '';
        var rect = el.getBoundingClientRect();
        if(Math.abs(rect.y - {y}) < 5 && text.includes('.json')) {{
            for(var i=0; i<{clicks}; i++) {{
                el.dispatchEvent(new MouseEvent('mousedown', {{
                    view: window, bubbles: true, cancelable: true, button: 0,
                    clientX: rect.x + rect.width/2, clientY: rect.y + rect.height/2
                }}));
            }}
            break;
        }}
    }}
    '''
    script = f'''tell application "Google Chrome"
        execute JavaScript "{js}" in active tab of window 1
    end tell'''
    run_osascript(script)


def get_workflow():
    """获取当前工作流"""
    script = '''tell application "Google Chrome"
        execute JavaScript "
        var w = localStorage.getItem('workflow');
        var ta = document.createElement('textarea');
        ta.value = w;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        'done';
        " in active tab of window 1
    end tell'''
    run_osascript(script)
    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return result.stdout


def save_workflow(wf_json, filename):
    """保存工作流"""
    try:
        data = json.loads(wf_json)
        nodes = data.get('nodes', [])
        if nodes < 10:
            return False
        path = os.path.join(COMFYUI_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return len(nodes)
    except:
        return False


# 已知Y位置
KNOWN = [
    (322,"nano_pro_arch_multi.json"),
    (391,"nano_pro_arch_maopi_style.json"),
    (439,"nano_pro_arch_maopi_text.json"),
    (487,"nano_pro_arch_cad.json"),
    (535,"nano_pro_arch_sketch_style.json"),
    (583,"nano_pro_arch_sketch_text.json"),
    (665,"nano_pro_landscape_maopi_style.json"),
    (713,"nano_pro_landscape_maopi_text.json"),
    (761,"nano_pro_landscape_sketch_style.json"),
    (809,"nano_pro_landscape_sketch_text.json"),
    (905,"nano_pro_kitchen.json"),
    (953,"nano_pro_living.json"),
    (1001,"nano_pro_study.json"),
    (1049,"nano_pro_bathroom.json"),
    (1097,"nano_pro_bedroom.json"),
    (1193,"nano_pro_cad_home.json"),
]


def main():
    print("=" * 50)
    print("ComfyUI工作流学习 - Chrome版")
    print("=" * 50)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"\n已有: {len(existing)}")
    
    # 打开Chrome
    print("\n打开Chrome...")
    open_chrome()
    
    # 尝试展开
    for attempt in range(5):
        print(f"\n=== 尝试 {attempt+1}/5 ===")
        
        count = get_tree_count()
        print(f"  树节点: {count}")
        
        if count > 10:
            print("  ✓ 树已展开!")
            break
        
        print("  刷新+展开...")
        reload_page()
        expand_tree()
        
        count = get_tree_count()
        print(f"  展开后: {count}")
    
    # 获取工作流列表
    items = get_json_items()
    print(f"\n发现 {len(items)} 个工作流")
    
    # 学习
    learned = 0
    for item in items:
        y = item['y']
        text = item['text']
        # 提取文件名
        import re
        match = re.search(r'([^.]+\.json)', text)
        if not match:
            continue
        filename = match.group(1)
        
        if filename in existing:
            continue
        
        print(f"\n  [{y}] {filename}")
        click_at_y(y, 60)
        time.sleep(1.2)
        
        wf = get_workflow()
        if wf and len(wf) > 1000:
            nodes = save_workflow(wf, filename)
            if nodes:
                print(f"    ✓ {nodes}节点")
                learned += 1
                existing.add(filename)
            else:
                print(f"    ✗")
        else:
            print(f"    ✗")
    
    # 也尝试已知位置
    print(f"\n=== 补充已知位置 ===")
    for y, fn in KNOWN:
        if fn in existing:
            continue
        print(f"\n  [{y}] {fn}")
        click_at_y(y, 60)
        time.sleep(1.2)
        
        wf = get_workflow()
        if wf and len(wf) > 1000:
            nodes = save_workflow(wf, fn)
            if nodes:
                print(f"    ✓ {nodes}节点")
                learned += 1
                existing.add(fn)
            else:
                print(f"    ✗")
        else:
            print(f"    ✗")
    
    print(f"\n=== 完成 ===")
    print(f"新增: {learned}")
    print(f"总计: {len(existing)}")


if __name__ == "__main__":
    main()
