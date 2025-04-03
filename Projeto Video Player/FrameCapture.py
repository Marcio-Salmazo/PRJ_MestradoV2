from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
import cv2
import numpy as np

from Model import Model


class FrameCapture(QDialog):

    # Construtor da classe
    def __init__(self, video_name, current_time, fps, frame, extension):

        # Realiza a chamada dos métodos da classe pai (QDialog)
        super().__init__()

        self.setWindowTitle("Capturar frame")  # Define o título da janela
        self.setGeometry(150, 150, 800, 600)  # Define as dimensões da janela criada

        # Layout principal do QDialog
        # Em um QDialog, para que os widgets apareçam, é necessário
        # definir um layout principal para a própria janela (self).
        self.layout = QVBoxLayout(self)

        # Criar uma área de rolagem para exibir o frame, independente do tamanho da janela
        # Instância da área de rolagem (associada à propria instância da janela - self)
        self.scroll_area = QScrollArea(self)
        # O QScrollArea sozinho não exibe widgets diretamente. Ele precisa de um widget interno
        self.scroll_widget = QWidget()
        # Criação de um layout vertical (QVBoxLayout) para organizar os elementos dentro do scroll_widget
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        # Permite que o conteúdo interno (self.scroll_widget) seja redimensionado para caber na QScrollArea
        self.scroll_area.setWidgetResizable(True)
        # Associando o widget que contém nosso layout de imagens à área de rolagem
        self.scroll_area.setWidget(self.scroll_widget)
        # Adicionar a área de rolagem ao layout principal
        self.layout.addWidget(self.scroll_area)

        # Criação de um layout horizontal para acomodar os botões
        self.hor_layout = QHBoxLayout()
        # Cria um QLabel para exibir a imagem.
        self.image_label = QLabel()
        # Armazena o frame recebido no construtor.
        self.frame = frame

        # Adiciona a QLabel da imagem ao layout da área de rolagem.
        self.scroll_layout.addWidget(self.image_label)

        # Cria três botões para salvar o frame com diferentes classificações de dor.
        # Os botões são adicionados ao QHBoxLayout(), organizando-os horizontalmente.
        self.save_ind = QPushButton("Salvar frame como 'Indolor'")
        self.save_pd = QPushButton("Salvar frame como 'Pouca dor'")
        self.save_md = QPushButton("Salvar frame como 'Muita dor'")
        self.save_inc = QPushButton("Salvar frame como 'Incerto'")

        self.hor_layout.addWidget(self.save_ind)
        self.hor_layout.addWidget(self.save_pd)
        self.hor_layout.addWidget(self.save_md)
        self.hor_layout.addWidget(self.save_inc)
        self.layout.addLayout(self.hor_layout)

        # Cria um botão chamado "Concluir", que fecha a janela ao ser clicado.
        self.close_btn = QPushButton("Concluir")
        self.layout.addWidget(self.close_btn)
        self.close_btn.clicked.connect(self.close)

        # Armazena as informações do vídeo (proveniente dos parâmetros)
        self.video_name = video_name
        self.current_time = current_time
        self.fps = fps

        # Inicialização de variáveis para a seleção de um trecho da imagem
        self.selection_start = None
        self.selection_end = None
        self.original_pixmap = None
        self.pixmap = None
        self.frameResized = None

        # Habilita o rastreamento do mouse na imagem
        self.image_label.setMouseTracking(True)
        # Registra a classe como um filtro de eventos, para acompanhar o mouse
        self.image_label.installEventFilter(self)

        # Conecta os botões às funções de captura do frame
        self.save_ind.clicked.connect(lambda: self.capture_frame("Indolor"))
        self.save_pd.clicked.connect(lambda: self.capture_frame("Pouca dor"))
        self.save_md.clicked.connect(lambda: self.capture_frame("Muita dor"))
        self.save_inc.clicked.connect(lambda: self.capture_frame("Incerto"))

        # ------------------------------------------------------------------
        # Exibe o frame na QLabel chamando um método específico da classe.
        self.extension = extension
        self.scale_factor = None
        self.display_frame()
        # ------------------------------------------------------------------
        # Coordenadas
        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None

        self.frameIndex = 0

    # A função busca exibir o frame na QLabel criada anteriormente
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

        # Captura os cliques e movimentos do mouse na área da imagem definida por obj
        if obj == self.image_label:
            # Se o botão esquerdo for pressionado, define a coordenada de início por meio do método start_selection()
            if event.type() == event.MouseButtonPress:
                self.start_selection(event)
            # Se o botão esquerdo for solto, define a coordenada de fim por meio do método end_selection()
            elif event.type() == event.MouseButtonRelease:
                self.end_selection(event)

        return super().eventFilter(obj, event)

    '''
    Os métodos start_selection e end_selection armazenam a posição do mouse de acordo com
    o local da imagem. Ambas as funções utilizam o event.pos() para obter o valor exato das
    coordenadas do ponteiro do mouse
    '''

    def start_selection(self, event):
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            print(self.selection_start)

    def end_selection(self, event):
        if event.button() == Qt.LeftButton and self.selection_start:
            self.selection_end = event.pos()
            print(self.selection_end)

            # Ao final da seleção o retângulo é desenhado
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
        self.x2 = self.selection_end.x() - 30
        self.y2 = self.selection_end.y()

        '''
        x1, y1 = self.selection_start.x() - 30, self.selection_start.y()
        x2, y2 = self.selection_end.x() - 30, self.selection_end.y()
        '''

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
