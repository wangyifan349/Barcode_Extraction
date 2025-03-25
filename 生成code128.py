import os
import random
import string
import barcode
from barcode.writer import ImageWriter
from PIL import Image
def generate_random_number(length=12):
    """生成指定长度的随机数字字符串"""
    return ''.join(random.choices(string.digits, k=length))
# 生成随机条形码数据的数量
num_barcodes = 4  # 可根据需要修改
# 随机生成条形码数据列表
data_list = [generate_random_number() for _ in range(num_barcodes)]
# 获取当前工作目录
current_directory = os.getcwd()
# 用于保存所有生成的条形码图片路径列表
image_paths = []
# 生成条形码并保存到本地
for data in data_list:
    # 使用 Code128 条形码格式
    code128 = barcode.get('code128', data, writer=ImageWriter())
    # 注意：传入不带扩展名的文件名，barcode 库会自动追加 ".png"
    filename = f"{data}"
    filepath = os.path.join(current_directory, filename)
    saved_filepath = code128.save(filepath)  # 保存条形码图片，返回保存后的完整文件路径
    print(f"条形码 {data} 已保存为: {saved_filepath}")
    image_paths.append(saved_filepath)
# 加载所有图片并合并为一张竖向拼接的大图片
barcode_images = []
# 为确保每个条形码尺寸统一，这里设置每个条形码的目标宽度和高度
barcode_width = 300
barcode_height = 150
for path in image_paths:
    img = Image.open(path)
    img = img.resize((barcode_width, barcode_height))  # 调整大小
    barcode_images.append(img)
# 设置拼接时的间距
padding = 10
# 计算合并后图片的总尺寸
total_width = barcode_width  # 因为竖向拼接，宽度就是单个图片的宽度
total_height = len(barcode_images) * barcode_height + (len(barcode_images) - 1) * padding
# 创建一张空白图片，用于粘贴所有条形码
combined_image = Image.new('RGB', (total_width, total_height), 'white')
# 将所有条形码图片竖向拼接
y_offset = 0
for img in barcode_images:
    combined_image.paste(img, (0, y_offset))
    y_offset += barcode_height + padding
# 保存最终合并的图片
combined_filepath = os.path.join(current_directory, "combined_barcodes_vertical.png")
combined_image.save(combined_filepath)
print(f"所有条形码已竖向合并并保存为: {combined_filepath}")
