#!/usr/bin/env python3
"""
ComfyUI工作流学习 - Playwright版
使用Playwright控制真实Chromium浏览器
"""

import subprocess
import time
import json
import os
import re

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([__import__('sys').executable, "-m", "pip", "install", "--user", "playwright"])
    from playwright.sync_api import sync_playwright

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"


def main():
    print("=" * 50)
    print("ComfyUI工作流学习 - Playwright版")
    print("=" * 50)
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    existing = {f for f in os.listdir(COMFYUI_DIR) if f.endswith('.json')}
    print(f"\n已有: {len(existing)}")
    
    with sync_playwright() as p:
        # 启动Chromium
        print("\n启动Chromium...")
        browser = p.chromium.launch(headless=False)  # 非headless可以看到
        context = browser.new_context()
        page = context.new_page()
        
        # 打开ComfyUI
        print(f"打开 {COMFYUI_URL}")
        page.goto(COMFYUI_URL)
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        def get_tree_items():
            """获取树节点"""
            try:
                items = page.evaluate("""
                    () => {
                        const all = document.querySelectorAll('.p-tree-node');
                        const results = [];
                        for(const el of all) {
                            const text = el.textContent || '';
                            const rect = el.getBoundingClientRect();
                            if(text.includes('.json') && rect.width > 0 && rect.y > 0) {
                                results.push({
                                    y: Math.round(rect.y),
                                    text: text.substring(0, 60)
                                });
                            }
                        }
                        return results;
                    }
                """)
                return items if items else []
            except Exception as e:
                print(f"  Error: {e}")
                return []
        
        def click_tree_item(y_pos, clicks=50):
            """点击树节点"""
            try:
                page.evaluate(f"""
                    () => {{
                        const all = document.querySelectorAll('.p-tree-node');
                        for(const el of all) {{
                            const text = el.textContent || '';
                            const rect = el.getBoundingClientRect();
                            if(Math.abs(rect.y - {y_pos}) < 5 && text.includes('.json')) {{
                                for(let i = 0; i < {clicks}; i++) {{
                                    el.dispatchEvent(new MouseEvent('mousedown', {{
                                        view: window, bubbles: true, cancelable: true, button: 0,
                                        clientX: rect.x + rect.width/2, clientY: rect.y + rect.height/2
                                    }}));
                                }}
                                break;
                            }}
                        }}
                    }}
                """)
            except Exception as e:
                print(f"  Click error: {e}")
        
        def expand_main_folder():
            """展开主文件夹"""
            try:
                page.evaluate("""
                    () => {
                        const all = document.querySelectorAll('.p-tree-node');
                        for(const el of all) {
                            const text = el.textContent || '';
                            if(text.includes('超强NanoPro系列31') && text.length < 100) {
                                const rect = el.getBoundingClientRect();
                                console.log('Found at y=' + rect.y);
                                for(let i = 0; i < 100; i++) {
                                    el.dispatchEvent(new MouseEvent('mousedown', {
                                        view: window, bubbles: true, cancelable: true, button: 0,
                                        clientX: rect.x + 25, clientY: rect.y + rect.height/2
                                    }));
                                }
                                break;
                            }
                        }
                    }
                """)
            except Exception as e:
                print(f"  Expand error: {e}")
        
        def get_workflow():
            """获取当前工作流"""
            try:
                return page.evaluate("""
                    () => localStorage.getItem('workflow')
                """)
            except:
                return None
        
        def save_workflow(wf_json, filename):
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
        
        # 刷新页面
        print("\n刷新页面...")
        page.reload()
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(3)
        
        # 尝试展开
        for attempt in range(5):
            print(f"\n=== 尝试 {attempt+1}/5 ===")
            
            items = get_tree_items()
            print(f"  发现 {len(items)} 个工作流")
            
            if len(items) > 10:
                print("  ✓ 树已展开!")
                break
            
            print("  展开主文件夹...")
            expand_main_folder()
            time.sleep(2)
        
        # 学习所有可见工作流
        print(f"\n=== 学习可见工作流 ===")
        learned = 0
        
        items = get_tree_items()
        for item in items:
            y = item['y']
            text = item['text']
            
            match = re.search(r'([^.]+\.json)', text)
            if not match:
                continue
            filename = match.group(1)
            
            if filename in existing:
                continue
            
            print(f"\n  [{y}] {filename}")
            click_tree_item(y, 60)
            time.sleep(1.2)
            
            wf = get_workflow()
            if wf and len(wf) > 1000:
                nodes = save_workflow(wf, filename)
                if nodes:
                    print(f"    ✓ {nodes}节点")
                    learned += 1
                    existing.add(filename)
                else:
                    print(f"    ✗ 保存失败")
            else:
                print(f"    ✗ 获取失败")
        
        # 也尝试已知位置
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
        
        print(f"\n=== 补充已知位置 ===")
        for y, fn in KNOWN:
            if fn in existing:
                continue
            print(f"\n  [{y}] {fn}")
            click_tree_item(y, 60)
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
        
        browser.close()
        
        print(f"\n=== 完成 ===")
        print(f"新增: {learned}")
        print(f"总计: {len(existing)}")


if __name__ == "__main__":
    main()
