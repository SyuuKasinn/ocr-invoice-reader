"""
工具函数模块
"""
import os
import json
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


def is_image_file(filename: str, supported_formats: List[str]) -> bool:
    """检查文件是否为支持的图片格式"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in supported_formats


def get_image_files(directory: str, supported_formats: List[str]) -> List[str]:
    """获取目录中所有支持的图片文件"""
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if is_image_file(file, supported_formats):
                image_files.append(os.path.join(root, file))
    return sorted(image_files)


def preprocess_image(image_path: str, mode: str = 'standard') -> np.ndarray:
    """
    图像预处理：提高OCR识别率

    Args:
        image_path: 图片路径
        mode: 预处理模式 ('standard', 'handwriting', 'aggressive')

    Returns:
        处理后的图像
    """
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")

    # 转为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if mode == 'handwriting':
        # 手写文字专用预处理
        # 1. 增强对比度（CLAHE - 对比度受限自适应直方图均衡化）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 2. 轻度去噪（保留手写笔画细节）
        denoised = cv2.bilateralFilter(enhanced, 5, 50, 50)

        # 3. 锐化（增强边缘）
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(denoised, -1, kernel)

        # 4. 自适应二值化（更适合手写）
        binary = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 15, 3
        )

        # 5. 轻微形态学处理（连接断裂的笔画）
        kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_morph)

        return binary

    elif mode == 'aggressive':
        # 激进模式：处理质量很差的图片
        # 增强对比度
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 强去噪
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 15, 7, 21)

        # 二值化
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 21, 5
        )

        return binary

    else:
        # 标准预处理
        # 去噪
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

        # 自适应二值化
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        return binary


def enhance_image_for_handwriting(image_path: str, output_path: str = None) -> str:
    """
    专门为手写文字增强图片

    Args:
        image_path: 原始图片路径
        output_path: 输出路径（可选）

    Returns:
        增强后的图片路径
    """
    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_enhanced{ext}"

    enhanced = preprocess_image(image_path, mode='handwriting')
    cv2.imwrite(output_path, enhanced)

    return output_path


def create_multiple_versions(image_path: str) -> List[str]:
    """
    创建图片的多个增强版本，用于多次识别

    Args:
        image_path: 原始图片路径

    Returns:
        增强版本的路径列表
    """
    versions = []
    base, ext = os.path.splitext(image_path)

    # 版本1: 标准预处理
    ver1_path = f"{base}_v1{ext}"
    img1 = preprocess_image(image_path, mode='standard')
    cv2.imwrite(ver1_path, img1)
    versions.append(ver1_path)

    # 版本2: 手写优化
    ver2_path = f"{base}_v2{ext}"
    img2 = preprocess_image(image_path, mode='handwriting')
    cv2.imwrite(ver2_path, img2)
    versions.append(ver2_path)

    # 版本3: 激进模式
    ver3_path = f"{base}_v3{ext}"
    img3 = preprocess_image(image_path, mode='aggressive')
    cv2.imwrite(ver3_path, img3)
    versions.append(ver3_path)

    return versions


def cleanup_temp_files(file_paths: List[str]):
    """清理临时文件"""
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass


def save_json(data: Dict[str, Any], output_path: str):
    """保存为JSON格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"结果已保存到: {output_path}")


def save_txt(data: Dict[str, Any], output_path: str):
    """保存为TXT格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"识别时间: {data.get('timestamp', '')}\n")
        f.write(f"图片路径: {data.get('image_path', '')}\n")
        f.write("=" * 50 + "\n\n")

        for item in data.get('results', []):
            text = item.get('text', '')
            confidence = item.get('confidence', 0)
            f.write(f"{text} (置信度: {confidence:.2f})\n")

        f.write("\n" + "=" * 50 + "\n")
        f.write(f"识别文本总数: {len(data.get('results', []))}\n")
        f.write(f"\n完整文本:\n{data.get('full_text', '')}\n")

    print(f"结果已保存到: {output_path}")


def save_excel(data: Dict[str, Any], output_path: str):
    """保存为Excel格式"""
    results = data.get('results', [])

    df_data = []
    for idx, item in enumerate(results, 1):
        df_data.append({
            '序号': idx,
            '识别文字': item.get('text', ''),
            '置信度': round(item.get('confidence', 0), 4),
            '位置_左上X': item.get('box', [[0,0]])[0][0],
            '位置_左上Y': item.get('box', [[0,0]])[0][1],
            '位置_右下X': item.get('box', [[0,0]])[2][0] if len(item.get('box', [])) > 2 else 0,
            '位置_右下Y': item.get('box', [[0,0]])[2][1] if len(item.get('box', [])) > 2 else 0,
        })

    df = pd.DataFrame(df_data)

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='OCR识别结果', index=False)

        # 添加摘要信息
        summary_df = pd.DataFrame({
            '项目': ['图片路径', '识别时间', '文本总数', '平均置信度'],
            '值': [
                data.get('image_path', ''),
                data.get('timestamp', ''),
                len(results),
                round(sum(r.get('confidence', 0) for r in results) / len(results) if results else 0, 4)
            ]
        })
        summary_df.to_excel(writer, sheet_name='摘要信息', index=False)

        # 完整文本
        full_text_df = pd.DataFrame({'完整识别文本': [data.get('full_text', '')]})
        full_text_df.to_excel(writer, sheet_name='完整文本', index=False)

    print(f"结果已保存到: {output_path}")


def draw_ocr_results(image_path: str, results: List[Dict], output_path: str):
    """在图片上绘制OCR识别结果 - 文档OCR优化版"""
    # 使用numpy读取图片以支持非ASCII路径
    try:
        img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except:
        img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")

    # 去重：基于位置和文本内容
    def is_duplicate(box1, text1, box2, text2):
        """判断两个检测结果是否重复"""
        # 计算IoU (Intersection over Union)
        def get_box_area(box):
            x_coords = [p[0] for p in box]
            y_coords = [p[1] for p in box]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            return width * height

        def get_intersection(box1, box2):
            x1_min, x1_max = min(p[0] for p in box1), max(p[0] for p in box1)
            y1_min, y1_max = min(p[1] for p in box1), max(p[1] for p in box1)
            x2_min, x2_max = min(p[0] for p in box2), max(p[0] for p in box2)
            y2_min, y2_max = min(p[1] for p in box2), max(p[1] for p in box2)

            x_overlap = max(0, min(x1_max, x2_max) - max(x1_min, x2_min))
            y_overlap = max(0, min(y1_max, y2_max) - max(y1_min, y2_min))
            return x_overlap * y_overlap

        area1 = get_box_area(box1)
        area2 = get_box_area(box2)
        intersection = get_intersection(box1, box2)

        if area1 == 0 or area2 == 0:
            return False

        iou = intersection / min(area1, area2)

        # 如果IoU > 0.7 且文本相似，则认为是重复
        if iou > 0.7:
            # 简单的文本相似度判断
            if text1 == text2 or text1 in text2 or text2 in text1:
                return True
        return False

    # 去重处理
    unique_results = []
    for i, item in enumerate(results):
        is_dup = False
        for existing in unique_results:
            if is_duplicate(item['box'], item['text'], existing['box'], existing['text']):
                # 保留置信度更高的
                if item['confidence'] > existing['confidence']:
                    unique_results.remove(existing)
                    break
                else:
                    is_dup = True
                    break
        if not is_dup:
            unique_results.append(item)

    print(f"  去重：{len(results)} → {len(unique_results)} 个检测结果")

    # 转换为PIL图像以支持Unicode
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    # 加载字体
    try:
        font_path = "C:/Windows/Fonts/msyh.ttc"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/simhei.ttf"
        font = ImageFont.truetype(font_path, 14)
        font_small = ImageFont.truetype(font_path, 11)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 根据置信度定义颜色（文档OCR优化）
    def get_color_by_confidence(confidence):
        if confidence > 0.9:
            return (0, 200, 83)     # 清新绿色
        elif confidence > 0.7:
            return (255, 152, 0)    # 活力橙色
        else:
            return (244, 67, 54)    # 警示红色

    # 绘制检测结果
    for item in unique_results:
        box = item.get('box', [])
        text = item.get('text', '')
        confidence = item.get('confidence', 0)

        if len(box) >= 4:
            # 转换box坐标为整数
            pts = [(int(p[0]), int(p[1])) for p in box]

            # 获取颜色
            color = get_color_by_confidence(confidence)

            # 绘制边框（加粗）
            draw.line(pts + [pts[0]], fill=color, width=2)

            # 准备标签文本（显示内容+置信度）
            text_display = text[:15] + "..." if len(text) > 15 else text
            label = f"{text_display} {confidence:.2f}"

            # 获取标签尺寸
            bbox = draw.textbbox((0, 0), label, font=font_small)
            label_width = bbox[2] - bbox[0]
            label_height = bbox[3] - bbox[1]

            # 标签位置：边框左上角上方
            x, y = pts[0]
            label_x = x
            label_y = y - label_height - 8

            # 如果超出上边界，放在边框下方
            if label_y < 0:
                label_y = y + 5

            # 绘制标签背景（半透明）
            padding = 4
            bg_coords = [
                label_x - padding,
                label_y - padding,
                label_x + label_width + padding,
                label_y + label_height + padding
            ]

            # 创建半透明背景
            bg_overlay = Image.new('RGBA', img_pil.size, (255, 255, 255, 0))
            bg_draw = ImageDraw.Draw(bg_overlay)
            bg_draw.rectangle(bg_coords, fill=color + (180,))  # 180 alpha for transparency

            # 合并背景
            img_pil = Image.alpha_composite(img_pil.convert('RGBA'), bg_overlay).convert('RGB')
            draw = ImageDraw.Draw(img_pil)

            # 绘制白色文字
            draw.text((label_x, label_y), label, font=font_small, fill=(255, 255, 255))

    # 转换回OpenCV格式
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    # 使用numpy保存图片以支持非ASCII路径
    try:
        _, encoded_img = cv2.imencode('.jpg', img)
        encoded_img.tofile(output_path)
    except:
        cv2.imwrite(output_path, img)

    print(f"可视化结果已保存到: {output_path}")


def format_timestamp() -> str:
    """格式化当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
