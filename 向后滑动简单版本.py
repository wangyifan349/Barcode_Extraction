from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
from collections import defaultdict
def enhance_image(image):
    # 增强对比度
    enhancer = ImageEnhance.Contrast(image)
    # 将对比度增强到原来的两倍
    enhanced_image = enhancer.enhance(2.0)
    # 放大图像
    # 将图像的尺寸放大为原来的两倍，使用 LANCZOS 过滤器进行高质量重采样
    enlarged_image = enhanced_image.resize((enhanced_image.width * 2, enhanced_image.height * 2), Image.LANCZOS)
    return enlarged_image
def process_image(image_path):
    # 打开图像并转换为灰度
    image = Image.open(image_path).convert('L')
    width, height = image.size

    # 设置滑动窗口的参数
    slide_width = int(width * 0.1)
    overlap_width = int(slide_width * 0.1)
    # 初始化起始位置
    start_x = 0
    # 用于存储解码结果及其出现次数
    decoded_results = defaultdict(lambda: {'count': 0, 'type': None})
    all_data_list = []
    while start_x < width:
        # 截取当前窗口的图像
        end_x = min(start_x + slide_width, width)
        cropped_image = image.crop((start_x, 0, end_x, height))
        # 调用增强函数
        enlarged_image = enhance_image(cropped_image)
        # 解码条形码或二维码
        decoded_objects = decode(enlarged_image)
        for obj in decoded_objects:
            data = obj.data.decode('utf-8')
            code_type = obj.type
            decoded_results[data]['count'] += 1
            decoded_results[data]['type'] = code_type
            all_data_list.append(data)
        # 更新起始位置，考虑重叠部分
        start_x += slide_width - overlap_width
    # 将结果按数量降序排序并打印
    sorted_results = sorted(decoded_results.items(), key=lambda item: item[1]['count'], reverse=True)
    for data, info in sorted_results:
        print(f"Data: {data}, Type: {info['type']}, Count: {info['count']}")
    # 去重后的数据列表和总数量
    unique_data_list = list(decoded_results.keys())
    total_count = len(all_data_list)

    print("\nUnique Data List:", unique_data_list)
    print("Total Count of Data:", total_count)

if __name__ == '__main__':
    process_image('selected_part_1.png')
