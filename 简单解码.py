from PIL import Image
from pyzbar.pyzbar import decode
# 加载合并后的图片
merged_image_path = "combined_barcodes_vertical.png"  # 合并后图片的路径
img = Image.open(merged_image_path)
# 对图片进行解码
decoded_objects = decode(img)
# 统计条形码的总数
barcode_count = len(decoded_objects)
if barcode_count == 0:
    print("未能识别到任何条形码，请检查图片质量及条形码间距。")
else:
    print(f"识别到 {barcode_count} 个条形码：")
    # 遍历所有解码的条形码并输出信息
    for obj in decoded_objects:
        barcode_data = obj.data.decode('utf-8')
        barcode_type = obj.type
        print(f"类型: {barcode_type}, 数据: {barcode_data}")
    # 输出总数
    print(f"总共识别到 {barcode_count} 个条形码。")
