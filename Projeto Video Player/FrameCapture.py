from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect
import cv2
import numpy as np


class FrameCapture(QDialog):
    def __init__(self, video_name, current_time, fps, frame):
        super().__init__()

        self.setWindowTitle("Capturar frame")
        self.setGeometry(150, 150, 800, 600)

        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        self.layout.addWidget(self.scroll_area)

        self.hor_layout = QHBoxLayout()
        self.image_label = QLabel()
        self.frame = frame
        self.display_frame()
        self.scroll_layout.addWidget(self.image_label)

        self.save_ind = QPushButton("Salvar frame como 'Indolor'")
        self.save_pd = QPushButton("Salvar frame como 'Pouca dor'")
        self.save_md = QPushButton("Salvar frame como 'Muita dor'")

        self.hor_layout.addWidget(self.save_ind)
        self.hor_layout.addWidget(self.save_pd)
        self.hor_layout.addWidget(self.save_md)
        self.layout.addLayout(self.hor_layout)

        self.close_btn = QPushButton("Concluir")
        self.layout.addWidget(self.close_btn)
        self.close_btn.clicked.connect(self.close)

        self.video_name = video_name
        self.current_time = current_time
        self.fps = fps

        self.selecting = False
        self.selection_rect = QRect()
        self.original_pixmap = None
        self.pixmap = None

        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)
        self.save_ind.clicked.connect(lambda: self.capture_frame("Indolor"))
        self.save_pd.clicked.connect(lambda: self.capture_frame("Pouca dor"))
        self.save_md.clicked.connect(lambda: self.capture_frame("Muita dor"))

    def display_frame(self):
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        self.pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.original_pixmap = self.pixmap.copy()

    def eventFilter(self, obj, event):

        if obj == self.image_label:
            if event.type() == event.MouseButtonPress:
                self.start_selection(event)
            elif event.type() == event.MouseMove:
                self.update_selection(event)
            elif event.type() == event.MouseButtonRelease:
                self.end_selection(event)
        return super().eventFilter(obj, event)

    def start_selection(self, event):
        if event.button() == Qt.LeftButton:
            print("Iniciando seleção na posição:", event.pos())  # Debug
            self.selecting = True
            self.selection_rect.setTopLeft(event.pos())
            self.selection_rect.setBottomRight(event.pos())

    def update_selection(self, event):
        if self.selecting:
            self.selection_rect.setBottomRight(event.pos())
            self.repaint_selection()

    def end_selection(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            print("Encerrando seleção na posição:", event.pos())  # Debug
            self.selecting = False
            self.repaint_selection()

    def repaint_selection(self):

        if self.original_pixmap is None:
            return
        print("Redesenhando seleção:", self.selection_rect)  # Depuração
        temp_pixmap = self.original_pixmap.copy()
        painter = QPainter(temp_pixmap)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(self.selection_rect)
        painter.end()
        self.image_label.setPixmap(temp_pixmap)

    def capture_frame(self, folder_name):
        print(f"Frame salvo na pasta {folder_name}")