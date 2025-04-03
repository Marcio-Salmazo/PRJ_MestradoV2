from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
import cv2
import numpy as np

from Model import Model


class FrameCapture(QDialog):

    def __init__(self, video_name, current_time, fps, frame, extension):
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
        self.scroll_layout.addWidget(self.image_label)

        self.save_ind = QPushButton("Salvar frame como 'Indolor'")
        self.save_pd = QPushButton("Salvar frame como 'Pouca dor'")
        self.save_md = QPushButton("Salvar frame como 'Muita dor'")
        self.save_inc = QPushButton("Salvar frame como 'Incerto'")

        self.hor_layout.addWidget(self.save_ind)
        self.hor_layout.addWidget(self.save_pd)
        self.hor_layout.addWidget(self.save_md)
        self.hor_layout.addWidget(self.save_inc)
        self.layout.addLayout(self.hor_layout)

        self.close_btn = QPushButton("Concluir")
        self.layout.addWidget(self.close_btn)
        self.close_btn.clicked.connect(self.close)

        self.video_name = video_name
        self.current_time = current_time
        self.fps = fps

        self.selection_start = None
        self.selection_end = None
        self.original_pixmap = None
        self.pixmap = None
        self.frameResized = None
        self.selecting = False

        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)

        self.save_ind.clicked.connect(lambda: self.capture_frame("Indolor"))
        self.save_pd.clicked.connect(lambda: self.capture_frame("Pouca dor"))
        self.save_md.clicked.connect(lambda: self.capture_frame("Muita dor"))
        self.save_inc.clicked.connect(lambda: self.capture_frame("Incerto"))

        self.extension = extension
        self.scale_factor = None
        self.display_frame()

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.frameIndex = 0

    def display_frame(self):
        if self.frame is None or not isinstance(self.frame, np.ndarray):
            print("Erro: frame inválido!")
            return

        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        if self.extension and '.mov' in self.extension:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        T_height, T_width, T_channel = frame.shape
        self.scale_factor = 0.7

        self.frameResized = cv2.resize(frame, (int(T_width * self.scale_factor), int(T_height * self.scale_factor)),
                                       interpolation=cv2.INTER_AREA)
        height, width, channel = self.frameResized.shape

        bytes_per_line = 3 * width
        qimage = QImage(self.frameResized.data, width, height, bytes_per_line, QImage.Format_RGB888)

        if qimage.isNull():
            print("Erro: QImage não foi criado corretamente!")
            return

        self.pixmap = QPixmap.fromImage(qimage)
        if self.pixmap.isNull():
            print("Erro: QPixmap não foi criado corretamente!")
            return

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
            self.selection_start = event.pos()
            self.selection_end = event.pos()
            self.selecting = True

    def update_selection(self, event):
        if self.selecting:
            self.selection_end = event.pos()
            self.draw_selection()

    def end_selection(self, event):
        if event.button() == Qt.LeftButton:
            self.selecting = False
            self.draw_selection()

    def draw_selection(self):
        if self.original_pixmap is None or self.selection_start is None or self.selection_end is None:
            return

        temp_pixmap = self.original_pixmap.copy()
        painter = QPainter(temp_pixmap)
        pen = QPen(Qt.red)
        pen.setWidth(3)
        painter.setPen(pen)

        self.x1 = self.selection_start.x() - 30
        self.y1 = self.selection_start.y()
        self.x2 = self.selection_end.x()
        self.y2 = self.selection_end.y()

        self.x1, self.x2 = min(self.x1, self.x2), max(self.x1, self.x2)
        self.y1, self.y2 = min(self.y1, self.y2), max(self.y1, self.y2)

        side_length = min(self.x2 - self.x1, self.y2 - self.y1)
        self.x2 = self.x1 + side_length
        self.y2 = self.y1 + side_length

        self.selection_end = QPoint(self.x2, self.y2)
        rect = QRect(self.x1, self.y1, side_length, side_length)
        painter.drawRect(rect)
        painter.end()

        self.image_label.setPixmap(temp_pixmap)

    def capture_frame(self, folder_name):

        model = Model()
        model.manage_dirs(folder_name)  # Criação das pastas

        # Valida se há ou não uma área de seleção bem como a existência de um frame antes de prosseguir a captura
        if self.selection_start is None or self.selection_end is None or self.frameResized is None:
            print("Erro: Nenhuma área selecionada para salvar.")
            return

        # Recortar a região selecionada na imagem original
        color_correction = cv2.cvtColor(self.frameResized, cv2.COLOR_BGR2RGB)
        selected_area = color_correction[self.y1:self.y2, self.x1:self.x2]

        # Valida se a área recortada possui um tamanho válido
        if selected_area.size == 0:
            print("Erro: área selecionada inválida!")
            return

        # ------------------------------------------------------
        flag = model.check_existence(selected_area)

        if not flag:
            self.frameIndex += 1
        # ------------------------------------------------------

        # Gerar o nome do arquivo
        frame_path = model.frame_path_generator(self.fps,
                                                self.current_time,
                                                folder_name,
                                                self.video_name,
                                                self.frameIndex)

        # Salvar a imagem e exibir mensagem ao usuário
        success = cv2.imwrite(frame_path, selected_area)

        if success:
            QMessageBox.information(self, "Sucesso", f"Frame salvo em: {frame_path}")
        else:
            QMessageBox.critical(self, "Erro", "Falha ao salvar o frame.")