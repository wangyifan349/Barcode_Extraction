from PIL import Image, ImageEnhance  # 用于图像处理和增强
from pyzbar.pyzbar import decode  # 用于解码条形码和二维码
# ---------------------------- 图像预处理函数 ----------------------------
def preprocess_image(image, scale_factor):
    """对图像进行灰度和对比度增强，并按比例放大"""
    # 转换为灰度
    grayscale_image = image.convert('L')
    # 增强对比度
    enhancer = ImageEnhance.Contrast(grayscale_image)
    enhanced_image = enhancer.enhance(2.0)  # 增强对比度
    # 计算新的图像尺寸
    new_size = (int(enhanced_image.width * scale_factor), int(enhanced_image.height * scale_factor))
    # 缩放图像到新的尺寸
    enlarged_image = enhanced_image.resize(new_size, Image.LANCZOS)
    return enlarged_image
# ---------------------------- 图像裁剪函数 ----------------------------
def crop_image(image, left, top, right, bottom):
    """裁剪出图像中的一个块"""
    # 定义裁剪区域
    box = (left, top, right, bottom)
    # 裁剪并返回图像
    return image.crop(box)
# ---------------------------- 条码和二维码识别函数 ----------------------------
def extract_barcodes_and_qrcodes(image_path, horizontal_chunks=8, vertical_steps=5, scale_factors=(1.5, 2.0, 3.0)):
    """提取条形码和二维码，逐块处理并增强预处理"""
    # 打开图像文件并获取图像尺寸
    original_image = Image.open(image_path)
    width, height = original_image.size
    count = 0
    detected_results = []  # 存储检测结果
    # 计算每块的宽度和高度
    chunk_width = width // horizontal_chunks
    step_height = height // vertical_steps
    print(f"Chunk width: {chunk_width}, Step height: {step_height}")
    # 逐行逐块处理图像
    for top in range(0, height, step_height):
        for left in range(0, width, chunk_width):
            # 确保不越界
            right = min(left + chunk_width, width)
            bottom = min(top + step_height, height)
            # 对每种放大倍率进行处理
            for scale_factor in scale_factors:
                # 预处理图像
                preprocessed_image = preprocess_image(original_image, scale_factor)
                # 计算裁剪区域的放大尺寸
                pre_left = int(left * scale_factor)
                pre_top = int(top * scale_factor)
                pre_right = int(right * scale_factor)
                pre_bottom = int(bottom * scale_factor)
                # 裁剪图像
                chunk = crop_image(preprocessed_image, pre_left, pre_top, pre_right, pre_bottom)
                # 解析该片段中的所有条码
                decoded_objects = decode(chunk)
                # 处理解码的条码结果
                for obj in decoded_objects:
                    barcode_data = obj.data.decode("utf-8")
                    unique_barcode = (barcode_data, (pre_left + obj.rect.left, pre_top + obj.rect.top))
                    # 存储唯一检测到的条形码
                    if unique_barcode not in detected_results:
                        count += 1
                        barcode_type = obj.type
                        rect = obj.rect
                        position = {
                            'left': pre_left + rect.left,
                            'top': pre_top + rect.top,
                            'width': rect.width,
                            'height': rect.height
                        }
                        detected_results.append(unique_barcode)
                        # 输出条形码信息
                        print(f"Barcode/Qrcode #{count}:")
                        print(f"Type: {barcode_type}")
                        print(f"Data: {barcode_data}")
                        print(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}")
                        print('-' * 30)
    # 输出统计报告
    print(f"\nTotal barcodes detected: {count}")
    return count, detected_results
# ---------------------------- 主程序执行 ----------------------------
# 使用示例，执行条码和二维码提取
total_count, results = extract_barcodes_and_qrcodes('l.jpg', horizontal_chunks=8, vertical_steps=5, scale_factors=(1.5, 2.0, 3.0))
# 输出检测结果整理和展示
print("\nSummary of detected barcodes:")
for idx, (data, position) in enumerate(results, start=1):
    print(f"{idx} - Data: {data}, Position: {position}")
