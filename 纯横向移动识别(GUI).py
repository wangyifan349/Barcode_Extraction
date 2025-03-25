import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
                             QFileDialog, QSlider, QLineEdit, QFormLayout, QTabWidget, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import cv2
from pyzbar import pyzbar
import os
import traceback

# --------------------------- 图像处理函数 ---------------------------

def enhance_image(image, alpha=1.5, beta=50, scale_factor=2.0):
    try:
        print("Enhancing image...")
        enhanced_image = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        height, width = enhanced_image.shape[:2]
        enlarged_image = cv2.resize(enhanced_image, (int(width * scale_factor), int(height * scale_factor)), interpolation=cv2.INTER_LINEAR)
        print("Image enhanced successfully.")
        return enlarged_image
    except Exception as e:
        print("Error in enhance_image:", e)
        traceback.print_exc()
        return image

def decode_barcode(image):
    try:
        print("Decoding barcode...")
        barcodes = pyzbar.decode(image)
        print(f"Found {len(barcodes)} barcodes.")
        return barcodes
    except Exception as e:
        print("Error in decode_barcode:", e)
        traceback.print_exc()
        return []

def process_image(image_path, slice_width=10, overlap_percent=0.2, alpha=1.5, beta=50, scale_factor=2.0):
    try:
        print(f"Processing image: {image_path}")
        if not os.path.exists(image_path):
            print(f"File does not exist: {image_path}")
            return []
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to load image: {image_path}")
            return []
        image = enhance_image(image, alpha=alpha, beta=beta, scale_factor=scale_factor)
        height, width = image.shape[:2]
        decoded_results = set()
        step_size = int(slice_width * (1 - overlap_percent))
        for x in range(0, width, step_size):
            x_end = min(x + slice_width, width)
            slice_img = image[0:height, x:x_end]
            barcodes = decode_barcode(slice_img)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                decoded_results.add((barcode_data, barcode_type))
        print(f"Decoding complete. Found {len(decoded_results)} unique barcodes.")
        return list(decoded_results)
    except Exception as e:
        print("Error in process_image:", e)
        traceback.print_exc()
        return []

# --------------------------- 条形码扫描线程 ---------------------------

class BarcodeScannerThread(QThread):
    resultReady = pyqtSignal(list)

    def __init__(self, imagePath, slice_width, overlap_percent, alpha, beta, scale_factor):
        super().__init__()
        self.imagePath = imagePath
        self.slice_width = slice_width
        self.overlap_percent = overlap_percent
        self.alpha = alpha
        self.beta = beta
        self.scale_factor = scale_factor

    def run(self):
        print("Thread started for barcode scanning.")
        results = process_image(self.imagePath, self.slice_width, self.overlap_percent, self.alpha, self.beta, self.scale_factor)
        self.resultReady.emit(results)

# --------------------------- 主应用程序类 ---------------------------

class BarcodeScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        print("Initializing UI...")
        self.setWindowTitle('条形码扫描器')
        self.setGeometry(100, 100, 800, 600)

        # 创建选项卡
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.info_tab = QWidget()
        self.tabs.addTab(self.main_tab, "扫描器")
        self.tabs.addTab(self.info_tab, "信息")

        # 设置选项卡
        self.setup_main_tab()
        self.setup_info_tab()

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        print("UI initialized.")

    def setup_main_tab(self):
        print("Setting up main tab...")
        # 主选项卡布局
        layout = QVBoxLayout()
        
        # 图像显示标签
        self.image_label = QLabel('未加载图像')
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # 参数设置
        form_layout = QFormLayout()
        self.alpha_slider = QSlider(Qt.Horizontal)
        self.alpha_slider.setMinimum(10)
        self.alpha_slider.setMaximum(30)
        self.alpha_slider.setValue(15)
        form_layout.addRow('Alpha (对比度):', self.alpha_slider)

        self.beta_slider = QSlider(Qt.Horizontal)
        self.beta_slider.setMinimum(0)
        self.beta_slider.setMaximum(100)
        self.beta_slider.setValue(50)
        form_layout.addRow('Beta (亮度):', self.beta_slider)

        self.scale_factor_slider = QSlider(Qt.Horizontal)
        self.scale_factor_slider.setMinimum(10)
        self.scale_factor_slider.setMaximum(30)
        self.scale_factor_slider.setValue(20)
        form_layout.addRow('缩放因子:', self.scale_factor_slider)

        self.slice_width_input = QLineEdit('10')
        form_layout.addRow('切片宽度:', self.slice_width_input)

        self.overlap_percent_input = QLineEdit('0.2')
        form_layout.addRow('重叠比例:', self.overlap_percent_input)

        layout.addLayout(form_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.load_button = QPushButton('加载图像')
        self.load_button.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_button)

        self.scan_button = QPushButton('扫描条形码')
        self.scan_button.clicked.connect(self.scan_barcode)
        button_layout.addWidget(self.scan_button)

        layout.addLayout(button_layout)

        # 结果显示标签
        self.results_label = QLabel('结果将在这里显示。')
        layout.addWidget(self.results_label)

        self.main_tab.setLayout(layout)
        print("Main tab set up.")

    def setup_info_tab(self):
        print("Setting up info tab...")
        # 信息选项卡布局
        layout = QVBoxLayout()
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setText(
            "此应用程序允许您从图像中扫描条形码。\n\n"
            "关键参数:\n"
            "- Alpha (对比度): 调整图像的对比度。\n"
            "- Beta (亮度): 调整图像的亮度。\n"
            "- 缩放因子: 缩放图像以便更好地检测条形码。\n"
            "- 切片宽度: 条形码扫描时的图像切片宽度。\n"
            "- 重叠比例: 切片之间的重叠百分比。\n\n"
            "使用方法:\n"
            "1. 使用“加载图像”按钮加载图像。\n"
            "2. 调整参数以增强图像。\n"
            "3. 点击“扫描条形码”按钮处理图像并解码条形码。"
        )
        layout.addWidget(info_text)
        self.info_tab.setLayout(layout)
        print("Info tab set up.")

    def load_image(self):
        print("Loading image...")
        # 加载图像文件
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "打开图像文件", "", "Images (*.png *.xpm *.jpg);;All Files (*)", options=options)
        if file_name:
            if not os.path.exists(file_name):
                self.results_label.setText('文件不存在。')
                print(f"File does not exist: {file_name}")
                return
            self.image_path = file_name
            pixmap = QPixmap(file_name)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))
            print(f"Image loaded: {file_name}")
        else:
            self.results_label.setText('未选择图像文件。')
            print("No image file selected.")

    def scan_barcode(self):
        print("Scanning barcode...")
        # 扫描条形码
        if hasattr(self, 'image_path'):
            alpha = self.alpha_slider.value() / 10.0
            beta = self.beta_slider.value()
            scale_factor = self.scale_factor_slider.value() / 10.0
            slice_width = int(self.slice_width_input.text())
            overlap_percent = float(self.overlap_percent_input.text())

            # 使用线程处理图像以避免界面卡顿
            self.thread = BarcodeScannerThread(self.image_path, slice_width, overlap_percent, alpha, beta, scale_factor)
            self.thread.resultReady.connect(self.display_results)
            self.thread.start()
            self.results_label.setText('正在处理...')
            print("Barcode scanning thread started.")
        else:
            self.results_label.setText('未加载图像。')
            print("Image not loaded.")

    def display_results(self, results):
        print("Displaying results...")
        # 显示结果
        if results:
            result_text = '\n'.join([f"数据: {data}, 类型: {barcode_type}" for data, barcode_type in results])
            self.export_results(results)
            print("Results displayed.")
        else:
            result_text = '未找到条形码。'
            print("No barcode found.")
        self.results_label.setText(result_text)

    def export_results(self, results):
        print("Exporting results...")
        # 导出结果到文本文件
        try:
            with open('barcode_results.txt', 'a') as file:
                for data, barcode_type in results:
                    file.write(f"数据: {data}, 类型: {barcode_type}\n")
                file.write("\n")  # 添加一个空行分隔不同的扫描结果
            print("Results exported to barcode_results.txt.")
        except Exception as e:
            print("Error in export_results:", e)
            traceback.print_exc()

if __name__ == '__main__':
    try:
        print("Starting application...")
        app = QApplication(sys.argv)
        ex = BarcodeScannerApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("Error in main application:", e)
        traceback.print_exc()
