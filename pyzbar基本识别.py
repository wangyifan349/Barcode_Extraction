import cv2
from pyzbar import pyzbar
# 设置图像的路径，请将路径替换为实际图像路径
image_path = './184324059458.png'
image = cv2.imread(image_path)
if image is None:
    print("无法加载图像，请检查路径是否正确！")
else:
    # 可选：将图像转换为灰度图有时可以提高识别成功率
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 识别图像中的所有条形码
    barcodes = pyzbar.decode(gray)
    if barcodes:
        for barcode in barcodes:
            # 提取条形码的边界框坐标并绘制矩形
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            # 解码的信息通常为字节数据，需要转换成字符串
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            # 将解码信息写在图像上
            text = f'{barcode_type}: {barcode_data}'
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 0, 255), 2)
            print(f"发现条形码 - 类型: {barcode_type}, 数据: {barcode_data}")
        # 保存加工后的图像到本地
        output_path = './barcodes_result.jpg'
        cv2.imwrite(output_path, image)
        print(f"识别的条形码信息已经保存到: {output_path}")
        # 如果需要显示图像，可取消下面几行代码的注释
        cv2.imshow("Barcodes", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("在图像中没有检测到条形码！")
