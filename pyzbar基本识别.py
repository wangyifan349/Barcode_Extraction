#pip install opencv-python pyzbar python-barcode Pillow
import cv2  # OpenCV库，用于图像处理
from pyzbar import pyzbar  # 用于条码解码
import barcode  # 条形码生成库
from barcode.writer import ImageWriter  # 用于将条码保存为图像
from PIL import Image  # Pillow库，用于处理图像文件
# ---------------------------- 识别条码函数 ----------------------------
def recognize_barcodes(image_path):
    """识别图像中的条形码并显示结果"""
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查路径是否正确！")
        return
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 解码图像中的所有条形码
    barcodes = pyzbar.decode(gray)
    # 检查是否检测到任何条码
    if len(barcodes) == 0:
        print("在图像中没有检测到条形码！")
        return
    # 迭代处理每个条形码
    for barcode in barcodes:
        # 获取条码的边界矩形
        (x, y, w, h) = barcode.rect
        # 绘制条码矩形边界
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # 解码条码数据并转换为字符串
        barcode_data = barcode.data.decode("utf-8")
        barcode_type = barcode.type
        # 准备显示文本
        text = f'{barcode_type}: {barcode_data}'
        # 在图像上绘制识别结果
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        # 显示条码信息
        print(f"发现条形码 - 类型: {barcode_type}, 数据: {barcode_data}")
    # 保存加工后的图像
    output_path = './barcodes_result.jpg'
    cv2.imwrite(output_path, image)
    print(f"识别的条形码信息已经保存到: {output_path}")
    # 显示图像，可以选择性使用
    cv2.imshow("Barcodes", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# ---------------------------- 生成条码函数 ----------------------------
def generate_barcode(data, output_path):
    """生成条形码并保存为图像"""
    # 获取code128类型的条码类
    code128 = barcode.get_barcode_class('code128')
    # 创建条码实例，指定是否添加校验和
    barcode_instance = code128(data, writer=ImageWriter(), add_checksum=False)
    # 保存条码为图像
    barcode_instance.save(output_path)
    print(f"条形码已经保存到: {output_path}")
    # 打开并展示生成的条码图像
    img = Image.open(output_path)
    img.show()
# ---------------------------- 主函数 ----------------------------
def main():
    """主函数，用于用户交互选择功能"""
    while True:
        # 打印用户选择菜单
        print("\n选择要执行的操作:")
        print("1. 识别图像中的条形码")
        print("2. 生成条形码")
        print("3. 退出程序")
        # 获取用户输入
        choice = input("输入选项编号: ")
        # 处理用户选择
        if choice == '1':
            # 识别条码
            image_path = input("输入图像路径: ")
            recognize_barcodes(image_path)
        elif choice == '2':
            # 生成条码
            data = input("输入条形码数据: ")
            output_path = input("输入保存生成条形码的路径(包含文件名): ")
            generate_barcode(data, output_path)
        elif choice == '3':
            # 退出程序
            print("退出程序。")
            break
        else:
            # 无效选择
            print("无效选项，请重试。")
# ---------------------------- 程序入口 ----------------------------
main()

