from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode

def preprocess_image(image, scale_factor):
    """对图像进行预处理以提高识别率"""
    grayscale_image = image.convert('L')
    enhancer = ImageEnhance.Contrast(grayscale_image)
    enhanced_image = enhancer.enhance(2.0)
    new_size = (int(enhanced_image.width * scale_factor), int(enhanced_image.height * scale_factor))
    enlarged_image = enhanced_image.resize(new_size, Image.LANCZOS)
    return enlarged_image

def crop_image(image, left, top, right, bottom):
    """裁剪图像并返回裁剪后的图像块"""
    box = (left, top, right, bottom)
    return image.crop(box)

def extract_barcodes_and_qrcodes(image_path, horizontal_chunks=8, vertical_steps=5, scale_factors=(2.0, 4.0)):
    # 打开原始图像
    original_image = Image.open(image_path)
    width, height = original_image.size
    count = 0
    detected_results = []
    chunk_width = width // horizontal_chunks
    step_height = height // vertical_steps
    print(f"Chunk width: {chunk_width}, Step height: {step_height}")

    # 逐行提取条形码
    for top in range(0, height, step_height):
        for i in range(horizontal_chunks):
            left = i * chunk_width
            right = left + chunk_width if (i < horizontal_chunks - 1) else width
            bottom = top + step_height if (top + step_height < height) else height
            # 在每个垂直位置，测试不同的放大倍数
            for scale_factor in scale_factors:
                # 每个缩放比例重新预处理
                preprocessed_image = preprocess_image(original_image, scale_factor)
                pre_left = int(left * scale_factor)
                pre_top = int(top * scale_factor)
                pre_right = int(right * scale_factor)
                pre_bottom = int(bottom * scale_factor)
                chunk = crop_image(preprocessed_image, pre_left, pre_top, pre_right, pre_bottom)
                decoded_objects = decode(chunk)
                for obj in decoded_objects:
                    barcode_data = obj.data.decode("utf-8")
                    unique_barcode = (barcode_data, (pre_left + obj.rect.left, pre_top + obj.rect.top))
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
                        print(f"Barcode/Qrcode #{count}:")
                        print(f"Type: {barcode_type}")
                        print(f"Data: {barcode_data}")
                        print(f"Position: Left={position['left']}, Top={position['top']}, Width={position['width']}, Height={position['height']}")
                        print('-' * 30)

# 使用示例
extract_barcodes_and_qrcodes('l.jpg', horizontal_chunks=8, vertical_steps=5, scale_factors=(2.0, 4.0))

"""
1. 预处理图像：
   - 将图像转换为灰度以提高对比度。
   - 增强图像对比度以改善检测效果。
   - 根据给定的缩放因子放大图像。
2. 图像裁剪：
   - 将图像水平分割成若干块，根据参数 `horizontal_chunks`。
   - 将图像垂直分为多个步骤，根据参数 `vertical_steps`。
   - 利用这些分割参数裁剪出各个图像块。
3. 解码条形码和二维码：
   - 对裁剪出的每个图像块应用多种缩放因子（参数 `scale_factors`）。
   - 对每个块使用 `pyzbar.decode` 方法尝试识别条形码和二维码。
   - 提取并存储识别结果，包括数据内容、类型和位置。
4. 结果记录和输出：
   - 存储检测到的条形码和二维码及其位置在 `detected_results` 列表中。
   - 打印每个检测到的条形码或二维码的信息，确保每个条目唯一。
5. 示例调用：
   - 使用例子调用主函数 `extract_barcodes_and_qrcodes` 来处理图像文件
   `'l.jpg'`，设置水平分块为8，垂直步长为5，和缩放因子为 2.0 和 4.0。
"""
