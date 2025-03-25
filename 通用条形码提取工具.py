import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QLabel, QPushButton, QFileDialog, 
                             QSpinBox, QVBoxLayout, QWidget, QFormLayout, QDoubleSpinBox, 
                             QTabWidget, QHBoxLayout, QMainWindow)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PIL import Image, ImageEnhance
from pyzbar.pyzbar import decode
from PyQt5.QtGui import QPixmap, QFont
from datetime import datetime  # 用于记录当前时间

# 定义扫描条形码线程
class BarcodeScannerThread(QThread):
    result_signal = pyqtSignal(list)  # 定义信号，用于发出结果

    def __init__(self, image_path, horizontal_chunks, vertical_steps, scale_factors):
        super().__init__()
        self.image_path = image_path  # 图像路径
        self.horizontal_chunks = horizontal_chunks  # 水平切块数量
        self.vertical_steps = vertical_steps  # 垂直扫描步骤
        self.scale_factors = scale_factors  # 图像缩放因子

    def preprocess_image(self, image, scale_factor):
        # 图像预处理：将图像转换为灰度图，增强对比度，并按缩放因子调整大小
        grayscale_image = image.convert('L')  # 转为灰度图
        enhancer = ImageEnhance.Contrast(grayscale_image)  # 增强对比度
        enhanced_image = enhancer.enhance(2.0)  # 增强对比度
        new_size = (int(enhanced_image.width * scale_factor), 
                    int(enhanced_image.height * scale_factor))  # 调整大小
        enlarged_image = enhanced_image.resize(new_size, Image.LANCZOS)  # 按新的尺寸缩放图像
        print(f"Processed image with scale factor {scale_factor}")  # 输出处理信息
        return enlarged_image

    def crop_image(self, image, left, top, right, bottom):
        # 根据给定的坐标裁剪图像
        return image.crop((left, top, right, bottom))

    def run(self):
        # 运行线程，执行条形码扫描
        if not self.image_path:
            print("No image path found.")  # 如果没有图像路径则输出信息
            self.result_signal.emit([])  # 返回空结果
            return

        try:
            original_image = Image.open(self.image_path)  # 打开图像文件
            width, height = original_image.size
            detected_results = []  # 存储扫描到的结果
            chunk_width = width // self.horizontal_chunks  # 水平切块的宽度
            step_height = height // self.vertical_steps  # 垂直扫描步长
            print(f"Processing image of size {width}x{height}")  # 输出图像的尺寸

            # 按步长扫描图像
            for top in range(0, height, step_height):  
                for i in range(self.horizontal_chunks):  # 切分水平区域
                    left = i * chunk_width
                    right = left + chunk_width if (i < self.horizontal_chunks - 1) else width
                    bottom = top + step_height if (top + step_height < height) else height

                    print(f"Scanning region: left={left}, top={top}, right={right}, bottom={bottom}")  # 输出每个扫描区域

                    # 根据缩放因子处理图像
                    for scale_factor in self.scale_factors:
                        preprocessed_image = self.preprocess_image(original_image, scale_factor)
                        pre_left = int(left * scale_factor)
                        pre_top = int(top * scale_factor)
                        pre_right = int(right * scale_factor)
                        pre_bottom = int(bottom * scale_factor)

                        # 裁剪图像
                        chunk = self.crop_image(preprocessed_image, pre_left, pre_top, pre_right, pre_bottom)
                        # 扫描条形码
                        decoded_objects = decode(chunk)

                        # 处理解码结果
                        for obj in decoded_objects:
                            barcode_data = obj.data.decode("utf-8")  # 解码条形码数据
                            barcode_type = obj.type  # 获取条形码类型
                            rect = obj.rect  # 获取条形码的位置
                            position = {
                                'left': pre_left + rect.left,
                                'top': pre_top + rect.top,
                                'width': rect.width,
                                'height': rect.height
                            }
                            detected_results.append({
                                'type': barcode_type,
                                'data': barcode_data,
                                'position': position
                            })
                            print(f"Detected {barcode_type} with data: {barcode_data}")  # 输出检测到的信息
                            print(f"Barcode position: {position}")  # 输出条形码位置

            # 返回扫描结果
            self.result_signal.emit(detected_results)

        except Exception as e:
            print(f"Error processing image: {e}")  # 输出异常信息
            self.result_signal.emit([])  # 返回空结果以示失败

# 定义UI界面
class BarcodeScannerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barcode and QR Code Scanner")  # 设置窗口标题
        self.setGeometry(100, 100, 1000, 700)  # 设置窗口位置和大小

        self.tabs = QTabWidget()  # 设置Tab组件
        self.setCentralWidget(self.tabs)

        self.setup_ui()  # 设置UI

    def setup_ui(self):
        # 设置UI组件
        main_tab = QWidget()
        layout = QVBoxLayout(main_tab)

        # 选择图像的标签
        self.image_label = QLabel("Select an image to start scanning.")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFont(QFont("Arial", 14))
        layout.addWidget(self.image_label)

        # 设置参数输入表单
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignLeft)

        # 水平切块数量输入框
        self.horizontal_chunks_spinbox = QSpinBox()
        self.horizontal_chunks_spinbox.setRange(1, 20)
        self.horizontal_chunks_spinbox.setValue(8)
        form_layout.addRow("Horizontal Chunks:", self.horizontal_chunks_spinbox)

        # 垂直扫描步长输入框
        self.vertical_steps_spinbox = QSpinBox()
        self.vertical_steps_spinbox.setRange(1, 20)
        self.vertical_steps_spinbox.setValue(5)
        form_layout.addRow("Vertical Steps:", self.vertical_steps_spinbox)

        # 缩放因子1输入框
        self.scale_factor_box_1 = QDoubleSpinBox()
        self.scale_factor_box_1.setRange(1.0, 5.0)
        self.scale_factor_box_1.setSingleStep(0.5)
        self.scale_factor_box_1.setValue(2.0)
        form_layout.addRow("Scale Factor 1:", self.scale_factor_box_1)

        # 缩放因子2输入框
        self.scale_factor_box_2 = QDoubleSpinBox()
        self.scale_factor_box_2.setRange(1.0, 5.0)
        self.scale_factor_box_2.setSingleStep(0.5)
        self.scale_factor_box_2.setValue(4.0)
        form_layout.addRow("Scale Factor 2:", self.scale_factor_box_2)

        layout.addLayout(form_layout)

        # 按钮区布局
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Image")
        self.load_button.setFont(QFont("Arial", 12))
        self.load_button.clicked.connect(self.load_image)  # 连接加载图像的功能
        button_layout.addWidget(self.load_button)

        self.scan_button = QPushButton("Scan for Codes")
        self.scan_button.setFont(QFont("Arial", 12))
        self.scan_button.clicked.connect(self.scan_codes)  # 连接扫描条形码的功能
        button_layout.addWidget(self.scan_button)

        self.export_button = QPushButton("Export Results")  # 新增导出按钮
        self.export_button.setFont(QFont("Arial", 12))
        self.export_button.clicked.connect(self.export_results)  # 导出结果的回调
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # 主标签页
        self.tabs.addTab(main_tab, "Main")

        # 整理解释页面
        explanation_tab = QWidget()
        explanation_layout = QVBoxLayout(explanation_tab)
        explanation_label = QLabel(
            "Parameter Explanations:\n"
            "1. Horizontal Chunks: Number of horizontal sections to divide the image.\n"
            "2. Vertical Steps: Number of vertical sections to scan through the image.\n"
            "3. Scale Factor: Factors by which the image is scaled to improve detection."
        )
        explanation_label.setFont(QFont("Arial", 12))
        explanation_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        explanation_layout.addWidget(explanation_label)
        self.tabs.addTab(explanation_tab, "Explanation")

        # 输出结果页面
        self.output_tab = QWidget()
        output_layout = QVBoxLayout(self.output_tab)
        self.output_label = QLabel("No results yet.")
        self.output_label.setFont(QFont("Arial", 14))
        output_layout.addWidget(self.output_label)
        self.tabs.addTab(self.output_tab, "Output")

        self.image_path = None  # 用于存储图像路径
        self.results = None  # 用于存储扫描结果

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f4f4f4;
            }

            QLabel {
                color: #333;
            }

            QPushButton {
                background-color: #5a9;
                color: #fff;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }

            QPushButton:hover {
                background-color: #48a;
            }

            QSpinBox, QDoubleSpinBox {
                max-width: 100px;
            }
        """)

    def load_image(self):
        # 加载图像文件
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        
        if file_path:
            try:
                self.image_path = file_path  # 更新图像路径
                self.image_label.setPixmap(QPixmap(file_path).scaled(600, 400, Qt.KeepAspectRatio))
                self.image_label.setText("")  # 清空提示文本
                print(f"Loaded image: {file_path}")  # 输出加载的信息
            except Exception as e:
                print(f"Error loading image: {e}")  # 输出加载失败的异常信息
                self.image_label.setText(f"Failed to load image: {e}")

    def scan_codes(self):
        # 扫描图像中的条形码或二维码
        if not self.image_path:
            self.output_label.setText("Please load an image first.")  # 如果没有加载图像，提示用户
            print("Image not loaded. Please load an image first.")  # 输出提示信息
            return

        horizontal_chunks = self.horizontal_chunks_spinbox.value()  # 获取用户输入的切块数量
        vertical_steps = self.vertical_steps_spinbox.value()  # 获取用户输入的垂直步骤
        scale_factors = [self.scale_factor_box_1.value(), self.scale_factor_box_2.value()]  # 获取缩放因子

        print(f"Scanning with horizontal_chunks={horizontal_chunks}, vertical_steps={vertical_steps}, scale_factors={scale_factors}")  # 输出扫描参数信息

        # 创建并启动扫描线程
        self.scanner_thread = BarcodeScannerThread(self.image_path, horizontal_chunks, vertical_steps, scale_factors)
        self.scanner_thread.result_signal.connect(self.display_results)  # 连接显示结果的信号
        self.scanner_thread.start()  # 启动线程进行扫描

    def display_results(self, results):
        # 显示扫描结果
        if not results:
            self.output_label.setText("No barcodes found.")  # 如果没有找到结果，提示用户
            print("No barcodes found.")  # 输出未找到条形码的信息
        else:
            self.results = results  # 存储结果
            result_text = ""  # 初始化结果文本
            for r in results:  # 遍历结果
                result_text += f"Type: {r['type']}, Data: {r['data']}, Position: {r['position']}\n"  # 构造结果文本
                print(f"Detected result: Type: {r['type']}, Data: {r['data']}, Position: {r['position']}")  # 输出检测到的详细结果
            self.output_label.setText(result_text)  # 更新输出标签文本

    def export_results(self):
        # 导出扫描结果到文件
        if self.results:
            # 获取文件名根基用户选择的图片的名字
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]  # 取图片文件名（不带后缀）
            json_file_name = f"{base_name}_results.json"  # 设置JSON文件名
            txt_file_name = f"{base_name}_results.txt"  # 设置TXT文件名

            # 保存JSON文件
            json_file_path, _ = QFileDialog.getSaveFileName(
                self, "Save JSON Results", json_file_name, "JSON Files (*.json)")
                
            # 如果用户选择了路径则执行
            if json_file_path:
                try:
                    with open(json_file_path, 'a') as json_file:  # 用'a'模式打开以附加写入
                        json.dump(self.results, json_file, indent=4)  # 写入JSON数据
                        json_file.write("\n")  # 添加换行符
                    print(f"Results exported to {json_file_path}")  # 输出导出成功的信息
                except Exception as e:
                    print(f"Error exporting results to JSON: {e}")  # 输出异常信息
                    self.output_label.setText(f"Error exporting results to JSON: {e}")

            # 保存TXT文件
            txt_file_path, _ = QFileDialog.getSaveFileName(
                self, "Save TXT Results", txt_file_name, "Text Files (*.txt)")
                
            # 如果用户选择了路径则执行
            if txt_file_path:
                try:
                    with open(txt_file_path, 'a') as txt_file:  # 用'a'模式打开以附加写入
                        for result in self.results:  # 遍历所有结果
                            write_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
                            txt_file.write(f"[{write_time}] Type: {result['type']}, Data: {result['data']}, Position: {result['position']}\n")  # 添加时间戳和结果
                    print(f"Results exported to {txt_file_path}")  # 输出导出成功的信息
                except Exception as e:
                    print(f"Error exporting results to TXT: {e}")  # 输出异常信息
                    self.output_label.setText(f"Error exporting results to TXT: {e}")

        else:
            print("No results to export.")  # 输出没有结果的提示
            self.output_label.setText("No results to export.")  # 提示没有可导出结果

# 启动应用程序
if __name__ == "__main__":
    app = QApplication(sys.argv)
    scanner_ui = BarcodeScannerUI()  # 创建UI实例
    scanner_ui.show()  # 显示主窗口
    sys.exit(app.exec_())  # 运行应用程序
