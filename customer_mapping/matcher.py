#!/usr/bin/env python3
"""
客户需求 → 工作流 匹配系统
根据客户描述自动推荐最合适的工作流和参数
"""

import json
import os
import re

# 工作流映射
WORKFLOW_MAP = {
    # 建筑系列
    "arch_multi": {
        "name": "建筑多角度一致性",
        "file": "nano_pro_arch_multi.json",
        "keywords": ["多角度", "多个视角", "不同角度", "建筑视角"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.65}
    },
    "arch_maopi_style": {
        "name": "建筑毛坯(风格版)",
        "file": "nano_pro_arch_maopi_style.json",
        "keywords": ["毛坯", "新房", "还没装修", "混凝土"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "arch_maopi_text": {
        "name": "建筑毛坯(文字版)",
        "file": "nano_pro_arch_maopi_text.json",
        "keywords": ["文字描述", "描述装修"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "arch_cad": {
        "name": "CAD建筑出图",
        "file": "nano_pro_arch_cad.json",
        "keywords": ["CAD", "施工图", "蓝图", "图纸"],
        "params": {"steps": 30, "cfg": 7.5, "denoise": 0.7}
    },
    "arch_sketch_style": {
        "name": "手绘建筑(风格版)",
        "file": "nano_pro_arch_sketch_style.json",
        "keywords": ["手绘", "草图", "设计师画", "sketch"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.75}
    },
    "arch_sketch_text": {
        "name": "手绘建筑(文字版)",
        "file": "nano_pro_arch_sketch_text.json",
        "keywords": ["手绘", "文字"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.75}
    },
    
    # 室内系列
    "indoor_control": {
        "name": "室内超强控制",
        "file": "nano_pro_indoor_control.json",
        "keywords": ["控制", "还原", "1:1"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.65}
    },
    "indoor_style": {
        "name": "室内毛坯(风格版)",
        "file": "nano_pro_indoor_style.json",
        "keywords": ["毛坯", "室内", "新房装修"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "indoor_text": {
        "name": "室内毛坯(文字版)",
        "file": "nano_pro_indoor_text.json",
        "keywords": ["文字", "描述"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "indoor_multi": {
        "name": "室内多角度一致性",
        "file": "nano_pro_indoor_multi.json",
        "keywords": ["多角度", "多个视角", "室内视角"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.65}
    },
    "indoor_sketch_style": {
        "name": "手绘室内(风格版)",
        "file": "nano_pro_sketch_indoor_style.json",
        "keywords": ["手绘室内", "室内草图"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.75}
    },
    
    # 房间系列
    "kitchen": {
        "name": "厨房设计",
        "file": "nano_pro_kitchen.json",
        "keywords": ["厨房", "开放式厨房", "岛台"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "living": {
        "name": "客厅设计",
        "file": "nano_pro_living.json",
        "keywords": ["客厅", "起居室", "沙发"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "bedroom": {
        "name": "卧室设计",
        "file": "nano_pro_bedroom.json",
        "keywords": ["卧室", "主卧", "次卧", "床"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "study": {
        "name": "书房设计",
        "file": "nano_pro_study.json",
        "keywords": ["书房", "书柜", "办公"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "bathroom": {
        "name": "卫生间设计",
        "file": "nano_pro_bathroom.json",
        "keywords": ["卫生间", "浴室", "厕所", "洗手间"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    
    # 景观系列
    "landscape_maopi_style": {
        "name": "景观毛坯(风格版)",
        "file": "nano_pro_landscape_maopi_style.json",
        "keywords": ["庭院", "花园", "景观", "院子", "绿化"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "landscape_sketch_style": {
        "name": "手绘景观(风格版)",
        "file": "nano_pro_landscape_sketch_style.json",
        "keywords": ["手绘景观", "景观草图"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.75}
    },
    
    # Kontext工具系列
    "k_panorama": {
        "name": "图片转全景",
        "file": "k_panorama.json",
        "keywords": ["全景", "360", "环视"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "k_delete": {
        "name": "删除图片物体",
        "file": "k_delete_object.json",
        "keywords": ["删除", "去掉", "移除", "修掉"],
        "params": {"steps": 20, "cfg": 7.5, "denoise": 0.5}
    },
    "k_light": {
        "name": "调节光影质感",
        "file": "k_light_shadow.json",
        "keywords": ["光影", "光线", "调光", "明暗"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.6}
    },
    "k_daynight": {
        "name": "效果日夜切换",
        "file": "k_day_night.json",
        "keywords": ["日夜", "白天", "晚上", "夜景"],
        "params": {"steps": 25, "cfg": 8.0, "denoise": 0.7}
    },
    "k_material": {
        "name": "模型材质渲染",
        "file": "k_model_material.json",
        "keywords": ["材质", "质感", "纹理", "表面"],
        "params": {"steps": 30, "cfg": 8.5, "denoise": 0.65}
    },
    "k_maopi": {
        "name": "毛坯房直出图",
        "file": "k_maopi_direct.json",
        "keywords": ["毛坯直出", "快速出图"],
        "params": {"steps": 20, "cfg": 7.5, "denoise": 0.8}
    },
}


def match_workflow(customer_desc: str) -> list:
    """
    根据客户描述匹配工作流
    返回: [(工作流ID, 工作流名, 文件, 参数, 匹配度), ...]
    """
    customer_desc = customer_desc.lower()
    results = []
    
    for wf_id, wf_info in WORKFLOW_MAP.items():
        score = 0
        matched_keywords = []
        
        for keyword in wf_info["keywords"]:
            if keyword.lower() in customer_desc:
                score += 10
                matched_keywords.append(keyword)
        
        if score > 0:
            results.append({
                "id": wf_id,
                "name": wf_info["name"],
                "file": wf_info["file"],
                "params": wf_info["params"],
                "score": score,
                "matched": matched_keywords
            })
    
    # 按匹配度排序
    results.sort(key=lambda x: x["score"], reverse=True)
    
    return results[:3]  # 返回前3个最匹配的


def get_workflow_by_scene(scene: str) -> dict:
    """根据场景直接获取工作流"""
    scene_map = {
        "客厅": "living",
        "厨房": "kitchen",
        "卧室": "bedroom",
        "书房": "study",
        "卫生间": "bathroom",
        "庭院": "landscape_maopi_style",
        "花园": "landscape_maopi_style",
        "建筑": "arch_maopi_style",
        "室内": "indoor_style",
    }
    
    wf_id = scene_map.get(scene)
    if wf_id and wf_id in WORKFLOW_MAP:
        return WORKFLOW_MAP[wf_id]
    return None


def format_result(results: list) -> str:
    """格式化匹配结果"""
    if not results:
        return "未找到匹配的工作流，请详细描述您的需求"
    
    output = ["📋 推荐工作流：\n"]
    
    for i, r in enumerate(results, 1):
        output.append(f"{i}. **{r['name']}**")
        output.append(f"   文件: `{r['file']}`")
        output.append(f"   匹配关键词: {', '.join(r['matched'])}")
        output.append(f"   参数: steps={r['params']['steps']}, cfg={r['params']['cfg']}, denoise={r['params']['denoise']}")
        output.append("")
    
    return '\n'.join(output)


# 命令行接口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        desc = ' '.join(sys.argv[1:])
    else:
        desc = input("请描述客户需求: ")
    
    print(f"\n分析需求: {desc}\n")
    
    results = match_workflow(desc)
    print(format_result(results))
