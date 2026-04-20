#!/usr/bin/env python3
"""
ComfyUI 全自动工作流学习器
"""

import subprocess
import time
import json
import os

COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"


def run_osascript(script):
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip()


def get_json_count():
    s = '''tell application "Safari"
        do JavaScript "var c=0;document.querySelectorAll('li').forEach(function(li){var r=li.getBoundingClientRect();if(li.textContent.includes('.json')&&r.width>0&&r.y>0)c++});c;" in front document
    end tell'''
    success, output = run_osascript(s)
    try:
        return int(float(output)) if output else 0
    except:
        return 0


def reload_page():
    s = '''tell application "Safari"
        do JavaScript "window.location.reload();" in front document
    end tell'''
    run_osascript(s)


def expand_tree():
    s = '''tell application "Safari"
        do JavaScript "
        var all = document.querySelectorAll('.p-tree-node');
        for(var el of all) {
            var t = el.textContent || '';
            if(t.includes('超强NanoPro系列31') && t.length < 100) {
                var r = el.getBoundingClientRect();
                console.log('y='+r.y);
                for(var i=0;i<100;i++) el.dispatchEvent(new MouseEvent('mousedown',{view:window,bubbles:true,cancelable:true,button:0,clientX:r.x+20,clientY:r.y+r.height/2}));
            }
        }
        " in front document
    end tell'''
    run_osascript(s)


def click_y(y, n):
    code = 'var all=document.querySelectorAll(".p-tree-node");for(var el of all){var t=el.textContent||"";var r=el.getBoundingClientRect();if(Math.abs(r.y-'+str(y)+')<5&&t.includes(".json")){for(var i=0;i<'+str(n)+';i++)el.dispatchEvent(new MouseEvent("mousedown",{view:window,bubbles:true,cancelable:true,button:0,clientX:r.x+r.width/2,clientY:r.y+r.height/2}));break;}}'
    s = 'tell application "Safari" to do JavaScript "'+code+'" in front document'
    run_osascript(s)


def get_workflow():
    s = '''tell application "Safari"
        do JavaScript "
        var w=localStorage.getItem('workflow');
        var ta=document.createElement('textarea');
        ta.value=w;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        'done';
        " in front document
    end tell'''
    run_osascript(s)
    r = subprocess.run(["pbpaste"], capture_output=True, text=True)
    return r.stdout


def save_wf(js, fn):
    try:
        d = json.loads(js)
        nodes = d.get('nodes', [])
        if nodes < 10: return False
        p = os.path.join(COMFYUI_DIR, fn)
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        return len(nodes)
    except: return False


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
    print("="*50)
    print("ComfyUI全自动学习器")
    print("="*50)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"\n已有: {len(existing)}")
    
    for attempt in range(10):
        print(f"\n=== 尝试 {attempt+1}/10 ===")
        c = get_json_count()
        print(f"  .json项: {c}")
        
        if c > 10:
            print("  ✓ 树已展开!")
            break
        
        print("  刷新+展开...")
        reload_page()
        time.sleep(8)
        expand_tree()
        time.sleep(2)
        
        c = get_json_count()
        print(f"  展开后: {c}")
    
    print(f"\n=== 学习 ===")
    learned = 0
    for y, fn in KNOWN:
        if fn in existing: continue
        print(f"  [{y}] {fn}")
        click_y(y, 60)
        time.sleep(1.2)
        wf = get_workflow()
        if wf and len(wf) > 1000:
            n = save_wf(wf, fn)
            if n:
                print(f"    ✓ {n}节点")
                learned += 1
                existing.add(fn)
            else: print(f"    ✗")
        else: print(f"    ✗")
    
    print(f"\n=== 完成 ===")
    print(f"新增: {learned}")
    print(f"总计: {len(existing)}")


if __name__ == "__main__": main()
