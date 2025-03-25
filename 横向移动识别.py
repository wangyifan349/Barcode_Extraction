#!/usr/bin/env python3
from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
import os
import cv2
import numpy as np
# ----------------------------------------
def preprocess_image(image, scale_factor, contrast_factor=2.0):
    # 转换为灰度图
    gray_image = image.convert('L')
    
    # 应用阈值化处理，将图像转为黑白
    threshold_image = gray_image.point(lambda p: p > 150 and 255)
    # 增强对比度
    contrast_enhancer = ImageEnhance.Contrast(threshold_image)
    enhanced_image = contrast_enhancer.enhance(contrast_factor)
    # 放大图像以提高识别率
    new_size = (int(enhanced_image.width * scale_factor), int(enhanced_image.height * scale_factor))
    enlarged_image = enhanced_image.resize(new_size, Image.LANCZOS)
    return enlarged_image
# ----------------------------------------
def extract_barcodes_and_qrcodes(image_path, segment_width_percentage=30, overlap_percentage=20, scale_factor=2.0, contrast_factor=2.0, output_file='barcode_qrcode_results.txt'):
    # 检查图像文件是否存在
    if not os.path.exists(image_path):
        print(f"Image file '{image_path}' does not exist.")
        return
    try:
        # 打开图像
        original_image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return
    # 获取图像宽度和高度
    width, height = original_image.size
    count = 0
    detected_results = set()
    # 打开输出文件
    with open(output_file, 'w') as output:
        # 计算每个段的宽度和重叠宽度
        segment_width = int(width * (segment_width_percentage / 100.0))
        overlap_width = int(segment_width * (overlap_percentage / 100.0))
        left = 0
        while left < width:
            # 确定当前段的右边界
            right = min(left + segment_width, width)
            # 裁剪当前段
            chunk = original_image.crop((left, 0, right, height))
            # 预处理图像
            preprocessed_image = preprocess_image(chunk, scale_factor, contrast_factor)
            # 将PIL图像转换为OpenCV格式
            open_cv_image = cv2.cvtColor(np.array(preprocessed_image), cv2.COLOR_RGB2BGR)
            # 解码当前段中的条形码/二维码
            decoded_objects = decode(preprocessed_image)
            if decoded_objects:
                output.write(f"Detected {len(decoded_objects)} objects in the chunk from {left} to {right}.\n")
                print(f"Detected {len(decoded_objects)} objects in the chunk from {left} to {right}.")
            # 遍历解码结果
            for obj in decoded_objects:
                barcode_data = obj.data.decode("utf-8")
                unique_barcode = (barcode_data, (left + obj.rect.left, obj.rect.top))
                # 检查是否已经检测到该条形码/二维码
                if unique_barcode not in detected_results:
                    detected_results.add(unique_barcode)
                    count += 1
                    barcode_type = obj.type
                    rect = obj.rect
                    position = {
                        'left': left + rect.left,
                        'top': rect.top,
                        'width': rect.width,
                        'height': rect.height
                    }
                    # 在条形码/二维码周围绘制矩形
                    cv2.rectangle(open_cv_image, (rect.left, rect.top), 
                                  (rect.left + rect.width, rect.top + rect.height), 
                                  (0, 255, 0), 2)
                    # 在图像上标记条形码/二维码数据和类型
                    cv2.putText(open_cv_image, f'{barcode_type}: {barcode_data}', 
                                (rect.left, rect.top - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.5, (0, 255, 0), 2)
                    # 将结果写入输出文件
                    output.write(f"Barcode/Qrcode #{count}:\n")
                    output.write(f"Type: {barcode_type}\n")
                    output.write(f"Data: {barcode_data}\n")
                    output.write(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}\n")
                    output.write('-' * 30 + '\n')
                    print(f"Barcode/Qrcode #{count}:")
                    print(f"Type: {barcode_type}")
                    print(f"Data: {barcode_data}")
                    print(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}")
                    print('-' * 30)
            # 显示处理后的图像
            # cv2.imshow('Processed Segment', open_cv_image)
            # cv2.waitKey(0)  # 等待按键以继续
            # cv2.destroyAllWindows()
            # 移动到下一个段（包括重叠部分）
            left += (segment_width - overlap_width)
        # 写入检测到的总数
        output.write(f"Total number of barcodes/QRCodes detected: {count}\n")
        print(f"Total number of barcodes/QRCodes detected: {count}")
# ----------------------------------------
# 调用函数并设置参数
extract_barcodes_and_qrcodes('selected_part_1.png', segment_width_percentage=30, overlap_percentage=20, scale_factor=2, contrast_factor=2, output_file='barcode_qrcode_results.txt')
