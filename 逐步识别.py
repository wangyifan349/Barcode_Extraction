#!/usr/bin/env python3

from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
import os

def preprocess_image(image, scale_factor, contrast_factor=2.0):
    """
    对图像进行预处理以提高识别率
    :param image: 待处理的PIL图像对象
    :param scale_factor: 图像缩放因子（如2.0表示原图像的2倍）
    :param contrast_factor: 对比度增强因子（默认值为2.0，表示增强到原来的2倍）
    :return: 经过预处理的图像对象
    """
    # 使用对比度增强器提升图像对比度
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(contrast_factor)  # 增强对比度
    
    # 放大图像以提高识别率
    new_size = (int(enhanced_image.width * scale_factor), int(enhanced_image.height * scale_factor))
    enlarged_image = enhanced_image.resize(new_size, Image.LANCZOS)  # 使用LANCZOS算法进行图像缩放
    return enlarged_image

def extract_barcodes_and_qrcodes(image_path, segment_width_percentage=30, overlap_percentage=20, scale_factor=2.0, contrast_factor=2.0, output_file='barcode_qrcode_results.txt'):
    """
    从图像中提取条形码和二维码，确保重叠覆盖前一个片段，避免识别错误，并将结果输出到一个文本文件。
    :param image_path: 输入图像的文件路径
    :param segment_width_percentage: 每个片段宽度的百分比（如30表示图像宽度的30%）
    :param overlap_percentage: 分段之间的重叠部分，以百分比表示（如20表示重叠部分为片段宽度的20%）
    :param scale_factor: 图像缩放因子（如2.0表示原图像的两倍）
    :param contrast_factor: 对比度增强因子（默认值为2.0，增强到原来的2倍）
    :param output_file: 输出文本文件的路径
    """
    # 检查输入图像文件是否存在
    if not os.path.exists(image_path):
        print(f"Image file '{image_path}' does not exist.")
        return
    
    try:
        # 打开图像文件
        original_image = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # 获取图像的宽度和高度
    width, height = original_image.size
    count = 0  # 用于统计识别到的条形码/二维码数量
    detected_results = set()  # 使用集合确保去重

    # 打开文件以写入结果
    with open(output_file, 'w') as output:
        # 计算每个片段和重叠的像素宽度
        segment_width = int(width * (segment_width_percentage / 100.0))  # 计算每个片段的宽度
        overlap_width = int(segment_width * (overlap_percentage / 100.0))  # 计算重叠的宽度

        # 从左到右滑动并识别
        left = 0
        while left < width:
            right = min(left + segment_width, width)  # 右边界不超过图像宽度
            
            # 裁剪当前段落
            chunk = original_image.crop((left, 0, right, height))
            preprocessed_image = preprocess_image(chunk, scale_factor, contrast_factor)  # 预处理图像
            
            # 解码当前图像块中的条形码和二维码
            decoded_objects = decode(preprocessed_image)  
            if decoded_objects:
                output.write(f"Detected {len(decoded_objects)} objects in the chunk from {left} to {right}.\n")
                print(f"Detected {len(decoded_objects)} objects in the chunk from {left} to {right}.")  # 打印结果
            
            # 遍历解码结果
            for obj in decoded_objects:
                barcode_data = obj.data.decode("utf-8")  # 获取条形码或二维码数据
                unique_barcode = (barcode_data, (left + obj.rect.left, obj.rect.top))  # 生成唯一条目
                if unique_barcode not in detected_results:  # 检查重复
                    detected_results.add(unique_barcode)  # 添加到集合中避免重复
                    count += 1
                    barcode_type = obj.type  # 获取条形码或二维码类型
                    rect = obj.rect  # 获取条形码/二维码的框选区域
                    position = {
                        'left': left + rect.left,
                        'top': rect.top,
                        'width': rect.width,
                        'height': rect.height
                    }
                    # 写入识别结果到文件
                    output.write(f"Barcode/Qrcode #{count}:\n")
                    output.write(f"Type: {barcode_type}\n")
                    output.write(f"Data: {barcode_data}\n")
                    output.write(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}\n")
                    output.write('-' * 30 + '\n')
                    # 打印识别结果到终端
                    print(f"Barcode/Qrcode #{count}:")
                    print(f"Type: {barcode_type}")
                    print(f"Data: {barcode_data}")
                    print(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}")
                    print('-' * 30)
            
            left += (segment_width - overlap_width)  # 更新左边界，确保重叠区域
        
        # 输出总计（去重后的总数）
        output.write(f"Total number of barcodes/QRCodes detected: {count}\n")
        # 打印总计到终端
        print(f"Total number of barcodes/QRCodes detected: {count}")

# 调用函数并设置参数
extract_barcodes_and_qrcodes('selected_part_1.png', segment_width_percentage=8, overlap_percentage=60, scale_factor=2.0, contrast_factor=2.0, output_file='barcode_qrcode_results.txt')
