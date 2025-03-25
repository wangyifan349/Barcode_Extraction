import cv2
from pyzbar import pyzbar
import numpy as np

def enhance_image(image, alpha=1.5, beta=50, scale_factor=2.0):
    """
    增强图像的对比度和亮度，并放大图像。
    :param image: 输入图像
    :param alpha: 对比度控制 (1.0-3.0)
    :param beta: 亮度控制 (0-100)
    :param scale_factor: 缩放因子
    :return: 增强后的图像
    """
    # 调整对比度和亮度
    enhanced_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    # 获取图像的尺寸
    height, width = enhanced_image.shape[:2]
    # 放大图像
    enlarged_image = cv2.resize(
        enhanced_image, 
        (int(width * scale_factor), int(height * scale_factor)), 
        interpolation=cv2.INTER_LINEAR
    )
    return enlarged_image
def decode_barcode(image):
    """
    使用 pyzbar 库解码条形码。
    :param image: 输入图像
    :return: 解码后的条形码对象列表
    """
    barcodes = pyzbar.decode(image)
    return barcodes
def process_image(image_path, slice_width=10, overlap_percent=0.2, alpha=1.5, beta=50, scale_factor=2.0):
    """
    处理图像，逐个切片解码条形码，并统计结果。
    :param image_path: 图像文件路径
    :param slice_width: 切片宽度
    :param overlap_percent: 切片重叠比例 (0-1)
    :param alpha: 对比度控制
    :param beta: 亮度控制
    :param scale_factor: 缩放因子
    :return: 解码结果的列表，包含数据和类型
    """
    # 读取图像
    image = cv2.imread(image_path)
    # 增强图像
    image = enhance_image(image, alpha=alpha, beta=beta, scale_factor=scale_factor)
    # 获取图像的高度和宽度
    height, width = image.shape[:2]
    # 初始化一个集合来存储解码结果，避免重复
    decoded_results = set()
    # 计算重叠步长
    step_size = int(slice_width * (1 - overlap_percent))
    # 从左到右逐个切片并尝试解码
    for x in range(0, width, step_size):
        # 定义切片的右边界
        x_end = min(x + slice_width, width)
        # 提取图像的切片
        slice_img = image[0:height, x:x_end]
        # 解码切片
        barcodes = decode_barcode(slice_img)
        # 如果解码成功，将结果添加到集合中
        for barcode in barcodes:
            barcode_data = barcode.data.decode('utf-8')
            barcode_type = barcode.type
            decoded_results.add((barcode_data, barcode_type))
    return list(decoded_results)
# 示例调用
image_path = '1742882753632.jpg'
results = process_image(
    image_path, 
    slice_width=10, 
    overlap_percent=0.2, 
    alpha=1.5, 
    beta=50, 
    scale_factor=2.0
)
# 打印解码结果
for data, barcode_type in results:
    print(f"Data: {data}, Type: {barcode_type}")

"""
参数说明：
- image_path: 图像文件路径，字符串类型。
- slice_width: 切片宽度，整数类型，默认为10。
- overlap_percent: 切片重叠比例，浮点数，范围为0到1，默认为0.2。
- alpha: 对比度控制，浮点数，范围为1.0到3.0，默认为1.5。
- beta: 亮度控制，整数类型，范围为0到100，默认为50。
- scale_factor: 缩放因子，浮点数，默认为2.0。
"""
