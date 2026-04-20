#!/usr/bin/env python3
"""
ComfyUI 工作流学习自动化 - Playwright版本
更可靠的浏览器自动化方案
"""

import subprocess
import time
import json
import os
import sys

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "--user", "playwright"])
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright

COMFYUI_URL = "https://03d2e6723fd14a7d9d9d86107dafa83f88.gz15.chenyu.cn"
COMFYUI_DIR = "/Users/mac/ComfyUI-Workflows"


def learn_with_playwright():
    """使用 Playwright 学习工作流"""
    
    os.makedirs(COMFYUI_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        # 启动 Chromium（headless=False可以看到浏览器）
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print(f"打开 {COMFYUI_URL}")
        page.goto(COMFYUI_URL)
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        
        # 点击侧边栏项目
        def click_tree_item(text_contains, click_count=30):
            """点击包含特定文字的树节点"""
            for _ in range(click_count):
                try:
                    # 找到所有 li 元素
                    items = page.query_selector_all('.p-tree-node')
                    for item in items:
                        text = item.text_content() or ''
                        if text_contains in text:
                            # 获取元素位置并点击
                            box = item.bounding_box()
                            if box:
                                page.mouse.click(
                                    box['x'] + box['width'] / 2,
                                    box['y'] + box['height'] / 2
                                )
                                return True
                except Exception as e:
                    print(f"  点击尝试失败: {e}")
                time.sleep(0.05)
            return False
        
        def get_workflow():
            """获取当前工作流"""
            try:
                workflow = page.evaluate("""
                    localStorage.getItem('workflow')
                """)
                return workflow
            except:
                return None
        
        # 工作流列表
        workflows = [
            # (关键词, 文件名)
            ("室内场景 渲染工作流（1:1还原）", "nano_pro_indoor_1to1.json"),
            ("毛坯室内生图 （参考风格版）", "nano_pro_indoor_style.json"),
            ("毛坯室内生图（文字描述版）", "nano_pro_indoor_text.json"),
            ("室内场景 渲染工作流（增加细节）", "nano_pro_indoor_detail.json"),
            ("室内多角度一致性", "nano_pro_indoor_multi.json"),
            ("手绘室内出图（参考风格版）", "nano_pro_sketch_indoor_style.json"),
            ("手绘室内出图（文字描述版）", "nano_pro_sketch_indoor_text.json"),
            ("提取室内软装配饰", "nano_pro_extract_soft.json"),
            ("提取室内硬装材料", "nano_pro_extract_hard.json"),
            ("室外场景 渲染工作流（1:1还原）", "nano_pro_outdoor_1to1.json"),
            ("室外场景 渲染工作流（增加细节）", "nano_pro_outdoor_detail.json"),
        ]
        
        success = 0
        for keyword, filename in workflows:
            print(f"\n学习: {filename}")
            
            # 点击
            if click_tree_item(keyword):
                print(f"  ✓ 点击成功")
                time.sleep(1.5)
                
                # 获取标题
                title = page.title()
                print(f"  标题: {title}")
                
                # 获取工作流
                workflow_json = get_workflow()
                if workflow_json and len(workflow_json) > 1000:
                    try:
                        data = json.loads(workflow_json)
                        nodes = data.get('nodes', [])
                        filepath = os.path.join(COMFYUI_DIR, filename)
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"  ✓ 保存成功 ({len(nodes)}节点)")
                        success += 1
                    except Exception as e:
                        print(f"  ✗ 保存失败: {e}")
                else:
                    print(f"  ✗ 获取失败")
            else:
                print(f"  ✗ 点击失败")
            
            time.sleep(2)
        
        browser.close()
        
        print("\n" + "=" * 60)
        print(f"完成! 成功 {success}/{len(workflows)} 个")
        print("=" * 60)


def main():
    print("=" * 60)
    print("ComfyUI 工作流学习自动化 - Playwright版本")
    print("=" * 60)
    
    input("准备好后按 Enter 开始...")
    learn_with_playwright()


if __name__ == "__main__":
    main()
