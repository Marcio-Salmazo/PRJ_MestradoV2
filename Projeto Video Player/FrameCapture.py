from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect
import cv2
import numpy as np

from Model import Model


class FrameCapture(QDialog):

    # Construtor da classe
    def __init__(self, video_name, current_time, fps, frame):

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

        self.hor_layout.addWidget(self.save_ind)
        self.hor_layout.addWidget(self.save_pd)
        self.hor_layout.addWidget(self.save_md)
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

        # Habilita o rastreamento do mouse na imagem
        self.image_label.setMouseTracking(True)
        # Registra a classe como um filtro de eventos, para acompanhar o mouse
        self.image_label.installEventFilter(self)

        # Conecta os botões às funções de captura do frame
        self.save_ind.clicked.connect(lambda: self.capture_frame("Indolor"))
        self.save_pd.clicked.connect(lambda: self.capture_frame("Pouca dor"))
        self.save_md.clicked.connect(lambda: self.capture_frame("Muita dor"))

        # ------------------------------------------------------------------
        # Exibe o frame na QLabel chamando um método específico da classe.
        self.display_frame()
        # ------------------------------------------------------------------

    # A função busca exibir o frame na QLabel criada anteriormente
    def display_frame(self):

        # Verifica se o frame é válido antes de processá-lo
        if self.frame is None or not isinstance(self.frame, np.ndarray):
            print("Erro: frame inválido!")
            return

        # Converte o frame do formato BGR para RGB e obtém suas dimensões (altura, largura e canais)
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame.shape
        bytes_per_line = 3 * width

        # Converte o array numpy para um QImage, a fim de permitir a exibição
        qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Valida se o qimage foi criado corretamente
        if qimage.isNull():
            print("Erro: QImage não foi criado corretamente!")
            return

        # Converte QImage em QPixmap, define-o na QLabel
        self.pixmap = QPixmap.fromImage(qimage)

        # Valida se o pixmap foi criado corretamente
        if self.pixmap.isNull():
            print("Erro: QPixmap não foi criado corretamente!")
            return

        # Define o pixmap na label prévia
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Salvar cópia da imagem original para desenhar o retângulo depois
        self.original_pixmap = self.pixmap.copy()

        print("Imagem original salva com sucesso!")

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

    def end_selection(self, event):
        if event.button() == Qt.LeftButton and self.selection_start:
            self.selection_end = event.pos()

            # Ao final da seleção o retângulo é desenhado
            self.draw_selection()

    def draw_selection(self):

        # Log para grantir que existe um pixmap e coordenadas de desenhos
        print("pixmap: ", self.original_pixmap)
        print("start: ", self.selection_start)
        print("end: ", self.selection_end)

        # Encerra a função caso o pixmap ou as coordenadas não estejam corretamente envenenadas
        if self.original_pixmap is None or self.selection_start is None or self.selection_end is None:
            return

        # Criar uma cópia do Pixmap original
        temp_pixmap = self.original_pixmap.copy()
        # Inicializa QPainter para desenhar na imagem copiada.
        painter = QPainter(temp_pixmap)
        # Define a cor do objeto de desenho como vermelho (Qt.red).
        pen = QPen(Qt.red)
        # Define a largura da linha do retângulo
        pen.setWidth(3)
        # Associa as configurações do objeto de desenho (caneta) para o QPainter
        painter.setPen(pen)

        # Definir o retângulo normalizado (caso o usuário selecione da direita para a esquerda)
        rect = QRect(self.selection_start, self.selection_end).normalized()
        # Finaliza a pintura e exibe a imagem modificada.
        painter.drawRect(rect)
        painter.end()

        # Atualizar a label da imagem com o novo Pixmap com o retângulo desenhado
        self.image_label.setPixmap(temp_pixmap)

    def capture_frame(self, folder_name):

        model = Model()
        model.manage_dirs(folder_name)  # Criação das pastas

        # Valida se há ou não uma área de seleção bem como a existência de um frame antes de prosseguir a captura
        if self.selection_start is None or self.selection_end is None or self.frame is None:
            print("Erro: Nenhuma área selecionada para salvar.")
            return

        # Obtém as coordenadas da seleção
        x1, y1 = self.selection_start.x(), self.selection_start.y()
        x2, y2 = self.selection_end.x(), self.selection_end.y()

        # Garantir que os valores estão na ordem correta (esquerda para direita, cima para baixo)
        # Dessa forma é levado em consideração qualquer orientação
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)

        # Recortar a região selecionada na imagem original
        # Aqui é armazenado a imagem do frame nos pontos x1 -> x2 e y1 -> y2
        selected_area = self.frame[y1:y2, x1:x2]

        # Valida se a área recortada possui um tamanho válido
        if selected_area.size == 0:
            print("Erro: área selecionada inválida!")
            return

        # Gerar o nome do arquivo
        frame_path = model.frame_path_generator(self.fps, self.current_time, folder_name, self.video_name)
        model.check_existence(frame_path)

        # filename = f"{self.video_name}_frame_{self.current_time:.2f}_{label}.png"

        # Salvar a imagem
        cv2.imwrite(frame_path, selected_area)
