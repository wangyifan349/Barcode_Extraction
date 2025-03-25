from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QMessageBox, QVBoxLayout, QWidget
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
from PIL import Image as PILImage
import sys
import os

class ImageSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口标题和几何尺寸
        self.setWindowTitle('图像选择工具')
        self.setGeometry(100, 100, 800, 600)
        self.setWindowState(Qt.WindowMaximized)

        # 中央小部件和布局设置
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # 图片显示标签
        self.imageLabel = QLabel(self)
        self.layout.addWidget(self.imageLabel)
        
        # 按钮设置
        self.loadButton = QPushButton('加载图片', self)
        self.loadButton.clicked.connect(self.load_image)
        self.layout.addWidget(self.loadButton)

        self.saveButton = QPushButton('保存选择部分', self)
        self.saveButton.clicked.connect(self.save_selection)
        self.saveButton.setEnabled(False)
        self.layout.addWidget(self.saveButton)

        self.undoButton = QPushButton('撤销选择', self)
        self.undoButton.clicked.connect(self.undo_selection)
        self.undoButton.setEnabled(False)
        self.layout.addWidget(self.undoButton)

        # 状态变量初始化
        self.origin_point = None
        self.current_rect = QRect()
        self.selection_rects = []
        self.originalImage = None
        self.scaled_factor = 1.0

    def load_image(self):
        # 加载图片
        file_name, _ = QFileDialog.getOpenFileName(self, '打开图片文件', '', "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            try:
                self.originalImage = PILImage.open(file_name)
                self.display_image()
                self.saveButton.setEnabled(True)
                self.undoButton.setEnabled(False)
                self.selection_rects.clear()
            except Exception as e:
                QMessageBox.critical(self, '错误', f"加载图片失败: {e}")

    def display_image(self):
        # 显示图像在标签中
        if self.originalImage:
            # 将 PIL 图像转换为 QImage
            qImg = QImage(self.originalImage.tobytes("raw", "RGB"), 
                          self.originalImage.width, 
                          self.originalImage.height, 
                          QImage.Format_RGB888)
            
            # 创建 QPixmap 并缩放以适应标签
            pixmap = QPixmap.fromImage(qImg)
            scaled_pixmap = pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.scaled_factor = pixmap.width() / scaled_pixmap.width()
            self.imageLabel.setPixmap(scaled_pixmap)
            self.imageLabel.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.imageLabel.update()

    def save_selection(self):
        # 保存选择部分
        try:
            for selection_rect in self.selection_rects:
                # 将坐标从缩放的 QPixmap 转换为原始图像的坐标
                x1 = int(selection_rect.left() * self.scaled_factor)
                y1 = int(selection_rect.top() * self.scaled_factor)
                x2 = int(selection_rect.right() * self.scaled_factor)
                y2 = int(selection_rect.bottom() * self.scaled_factor)
                
                cropped_image = self.originalImage.crop((x1, y1, x2, y2))
                output_filename = self.get_unique_filename('selected_part', 'png')
                cropped_image.save(output_filename)
                QMessageBox.information(self, '保存成功', f"选择部分已保存为 {output_filename}")
        except Exception as e:
            QMessageBox.critical(self, '错误', f"保存选择区域失败: {e}")

    def get_unique_filename(self, base_name, extension):
        # 生成唯一的文件名
        index = 1
        while True:
            filename = f"{base_name}_{index}.{extension}"
            if not os.path.exists(filename):
                return filename
            index += 1

    def mousePressEvent(self, event):
        # 鼠标按下事件处理
        if event.button() == Qt.LeftButton and self.imageLabel.pixmap() is not None:
            self.origin_point = self.imageLabel.mapFrom(self, event.pos())
            self.current_rect = QRect(self.origin_point, self.origin_point)
            self.update()

    def mouseMoveEvent(self, event):
        # 鼠标移动事件处理
        if self.current_rect is not None and self.imageLabel.pixmap() is not None:
            end_point = self.imageLabel.mapFrom(self, event.pos())
            self.current_rect.setBottomRight(end_point)
            self.update()

    def mouseReleaseEvent(self, event):
        # 鼠标释放事件处理
        if event.button() == Qt.LeftButton and self.imageLabel.pixmap() is not None:
            end_point = self.imageLabel.mapFrom(self, event.pos())
            self.current_rect.setBottomRight(end_point)
            if self.current_rect.isValid():
                self.selection_rects.append(self.current_rect)
            self.current_rect = QRect()
            self.update()

    def undo_selection(self):
        # 撤销选择
        if self.selection_rects:
            self.selection_rects.pop()
            self.update()

    def paintEvent(self, event):
        # 绘制选择矩形
        super().paintEvent(event)
        if self.imageLabel.pixmap() is not None:
            painter = QPainter(self.imageLabel.pixmap())
            pen = QPen(Qt.red, 2, Qt.SolidLine)
            painter.setPen(pen)

            for selection_rect in self.selection_rects:
                painter.drawRect(selection_rect)
            if self.current_rect and self.current_rect.isValid():
                painter.drawRect(self.current_rect)

            painter.end()
            self.imageLabel.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageSelector()
    window.show()
    sys.exit(app.exec_())
