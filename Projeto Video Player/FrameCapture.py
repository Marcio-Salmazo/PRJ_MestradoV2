import os

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
import cv2
import numpy as np

from Model import Model


class FrameCapture(QDialog):

    # Construtor da classe
    def __init__(self, video_name, current_time, fps, frame, extension):
        super().__init__()

        self.setWindowTitle("Capturar frame")  # Define o título da janela
        self.setGeometry(150, 150, 800, 600)  # Define as dimensões da janela
        self.layout = QVBoxLayout(self)  # Define o layout principal da janela

        self.scroll_area = QScrollArea(self)  # Define uma área de scroll (rolagem)
        self.scroll_widget = QWidget()  # Define um widget central para a área de rolagem
        self.scroll_layout = QVBoxLayout(self.scroll_widget)  # Define um layout principal para o widget de scroll
        self.scroll_area.setWidgetResizable(True)  # Permite que a área de rolagem seja redimensionável
        self.scroll_area.setWidget(self.scroll_widget)  # Associa o widget central criado à área de rolagem
        self.layout.addWidget(self.scroll_area)  # Atribui a área de rolagem ao layout principal da JANELA

        self.hor_layout = QHBoxLayout()  # Criação de um layout horizontal para a disposição dos botões
        self.image_label = QLabel()  # Define um label para inserir a imagem do frame a ser capturado
        self.frame = frame  # Recebe o frame a ser capturado
        self.scroll_layout.addWidget(self.image_label)  # Atribui o label da imagem à área de rolagem

        #  Criação dos botões de classificação
        self.save_ind = QPushButton("Salvar frame como 'Indolor'")
        self.save_pd = QPushButton("Salvar frame como 'Pouca dor'")
        self.save_md = QPushButton("Salvar frame como 'Muita dor'")
        self.save_inc = QPushButton("Salvar frame como 'Incerto'")

        #  Inserção dos botões ao layout horizontal
        self.hor_layout.addWidget(self.save_ind)
        self.hor_layout.addWidget(self.save_pd)
        self.hor_layout.addWidget(self.save_md)
        self.hor_layout.addWidget(self.save_inc)
        self.layout.addLayout(self.hor_layout)

        #  Criação, atribuição e função do botão de fechar a janela
        self.close_btn = QPushButton("Concluir")
        self.layout.addWidget(self.close_btn)
        self.close_btn.clicked.connect(self.close)

        # Inicialização da variáveis globais proveniente dos parâmetros do contrutor
        self.video_name = video_name
        self.current_time = current_time
        self.fps = fps
        self.extension = extension

        # Variáveis referentes aos eventos de seleção
        self.selection_start = None
        self.selection_end = None
        self.original_pixmap = None
        self.pixmap = None
        self.frameResized = None
        self.selecting = False
        self.image_label.setMouseTracking(True)
        self.image_label.installEventFilter(self)

        #  Atribuição das funcionalidades aos botões de salvamento
        self.save_ind.clicked.connect(lambda: self.capture_frame("Indolor"))
        self.save_pd.clicked.connect(lambda: self.capture_frame("Pouca dor"))
        self.save_md.clicked.connect(lambda: self.capture_frame("Muita dor"))
        self.save_inc.clicked.connect(lambda: self.capture_frame("Incerto"))

        # Variáveis globais referentes à manipulação dos frames
        self.scale_factor = None
        self.display_frame()

        self.x1 = None
        self.x2 = None
        self.y1 = None
        self.y2 = None
        self.frameIndex = 0

    #  Função responsável por exibir o frame na área de scroll
    def display_frame(self):

        # Validação se o frame a ser exibido é ou não válido para a exibição
        # Valida se o frame é vazio ou se ele é uma instância do frame
        if self.frame is None or not isinstance(self.frame, np.ndarray):
            print("Erro: frame inválido!")
            return

        # Correção de cores do frame, convertendo de BGR para RGB
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        # Realiza uma rotação da imagem em 90 graus caso sua extensão seja .mov
        # Por algum motivo, tal extensão realiza uma rotação indesejada
        if self.extension and '.mov' in self.extension:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Recebe as informações de forma da imagem e define um valor de escala a fim de
        # reduzir o tamanho da imagem para a exibição na área de rolagem
        T_height, T_width, T_channel = frame.shape
        self.scale_factor = 0.7

        # Redimensiona a imagem de acordo com o fator de escala préviamente definido
        # Após o tratamento do frame, uma qImage é gerado a partir do frame tratado
        # A qImage É uma classe do Qt que representa imagens em memória, ou seja, ela armazena os dados brutos
        # de uma imagem, como largura, altura, formato (RGB, ARGB, etc.) e os pixels.
        self.frameResized = cv2.resize(frame, (int(T_width * self.scale_factor), int(T_height * self.scale_factor)),
                                       interpolation=cv2.INTER_AREA)
        height, width, channel = self.frameResized.shape
        bytes_per_line = 3 * width
        qimage = QImage(self.frameResized.data, width, height, bytes_per_line, QImage.Format_RGB888)

        # Validação se a qImage gerada é (ou não) válida
        if qimage.isNull():
            print("Erro: QImage não foi criado corretamente!")
            return

        # Cria um pixmap a partir da qImage gerada
        # qPixmap é uma classe otimizada para exibição gráfica de imagens em componentes da interface
        # (como QLabel, QPushButton, etc.). Sua principal aplicação é a exibição de imagens em widgets,
        # sendo mais leve e rápido para desenhar na tela.
        self.pixmap = QPixmap.fromImage(qimage)
        if self.pixmap.isNull():
            print("Erro: QPixmap não foi criado corretamente!")
            return

        # Atribui o pixmap criado ao label gerado préviamente para a exibição do frame
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.original_pixmap = self.pixmap.copy()

    # Essa função faz parte de uma classe em PyQt que está monitorando eventos do mouse sobre um componente,
    # neste caso, o componente é uma imagem exibida em um QLabel. A função eventFilter é usada para interceptar
    # eventos(como clique, movimento, etc.) antes que eles cheguem ao widget(neste caso, image_label).
    def eventFilter(self, obj, event):
        if obj == self.image_label:

            # Se o botão esquerdo for pressionado, start_selection é chamado
            if event.type() == event.MouseButtonPress:
                self.start_selection(event)
            # Se o mouse for movimentado, update_selection é chamado
            elif event.type() == event.MouseMove:
                self.update_selection(event)
            # Se o botão esquerdo for solto, end_selection é chamado
            elif event.type() == event.MouseButtonRelease:
                self.end_selection(event)
        return super().eventFilter(obj, event)

    def start_selection(self, event):
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()  # Obtém as coordenadas de onde o botão esquerdo foi pressionado
            self.selection_end = event.pos()  # Inicializa as coordenada finais da seleção
            self.selecting = True  # Flag que indica se a seleção está sendo feita

    def update_selection(self, event):
        if self.selecting:  # Executa os comandos enquanto a flag de seleção estiver verdadeira
            self.selection_end = event.pos()  # Atualiza as coordenada finais da seleção
            self.draw_selection()  # Chama 'draw selection' para exibir a área de seleção em tempo real

    def end_selection(self, event):
        if event.button() == Qt.LeftButton:  # Valida se o botão esquerdo do mouse foi solto
            self.selecting = False  # Flag que indica se a seleção terminou
            self.draw_selection()  # Chama 'draw selection' para exibir a área de seleção

    # Função responsável por exibir a seleção em cima do pixmap
    def draw_selection(self):

        # Valida as condições necessárias para prosseguir com o desenho de seleção
        if self.original_pixmap is None or self.selection_start is None or self.selection_end is None:
            print("Pixmap ou área de seleção inválidos")
            return

        # Cópia do pixmap, a fim de evitar modificações na instãncia original
        temp_pixmap = self.original_pixmap.copy()
        # Cria um objeto QPainter, que é a ferramenta do PyQt usada para desenhar sobre widgets ou imagens.
        painter = QPainter(temp_pixmap)
        # Cria um objeto QPen, que define o "pincel" com o qual a seleção será desenhada.
        pen = QPen(Qt.red)
        # Define a espessura da linha como 3 pixels
        pen.setWidth(3)
        # Atribui a caneta (pen) ao objeto painter.
        painter.setPen(pen)

        # Atribui as coordenadas x e y, de acordo com o retorno das funções selection_start e selection_end
        # x1 obtém um offset (-30) a fim de manter a precisão da seleção em razão do fator de escala
        self.x1 = self.selection_start.x() - 30
        self.y1 = self.selection_start.y()
        self.x2 = self.selection_end.x()
        self.y2 = self.selection_end.y()

        # As coordenadas são re-organizadas a fim de levar em consideração seleções invertidas
        self.x1, self.x2 = min(self.x1, self.x2), max(self.x1, self.x2)
        self.y1, self.y2 = min(self.y1, self.y2), max(self.y1, self.y2)

        # Mantém a seleção quadrada, independente da posição do mouse
        side_length = min(self.x2 - self.x1, self.y2 - self.y1)
        self.x2 = self.x1 + side_length
        self.y2 = self.y1 + side_length

        # Cria um objeto QPoint, que representa um ponto (x, y) no espaço 2D da interface gráfica.
        # Esse QPoint é salvo como self.selection_end para armazenar a posição final da seleção
        self.selection_end = QPoint(self.x2, self.y2)
        # Cria um retângulo (QRect), que é o que será desenhado na tela
        # side_length representa a largura e altura do retângulo. Usar o mesmo valor para ambos
        # significa que um quadrado será desenhado.
        rect = QRect(self.x1, self.y1, side_length, side_length)
        # Ao chamar drawRect(rect), o PyQt desenha esse retângulo sobre o QPixmap,
        # QImage ou widget que está sendo manipulado.
        painter.drawRect(rect)
        # Encerra o processo de desenho.
        painter.end()

        # Atualiza a imagem do label na área de rolagem pela nova imagem desenhada
        self.image_label.setPixmap(temp_pixmap)

    # Função responsável por capturar e salvar a área de seleção definida na imagem
    # bem como salvar dados para o processo de augmentation futuro
    def capture_frame(self, folder_name):

        # Cria uma instância da classe Model, a fim de utilizar
        # suas funções. Neste primeiro momento a pasta da categoria
        # selecionada na janela será criada para alocar os frames
        model = Model()
        model.manage_dirs(folder_name)  # Criação das pastas

        # Verificar se a pasta "Augmentation" existe na pasta raiz. Em caso negativo, a função
        # model.Augmentation_folder_structure() é chamada para criar a estrutura de pastas voltadas
        # para o processo de Augmentation. (LEVAR ESTE TRECHO PARA O MODEL)
        if not os.path.exists("Augmentation"):
            model.Augmentation_folder_structure()
        else:
            print("Estrutura de pastas já criada")

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

        # Cria uma flag para avaliar se a área do frame selecionada na imagem já foi previamente salva
        # em algumas das possíveis categorias. Caso alguma imagem duplicada seja encontrada, ela é removida
        # salvando apenas o frame atual na categoria atual selecionada
        flag = model.check_existence(selected_area)
        # Caso o frame não seja encontrado e duplicadom, o index é incrementado
        # O frameIndex, define o valor do subframe (trecho da imagem) recortado
        # ex: frame1_recorte1, frame1_recorte2, frame1_recorte3, etc.
        if not flag:
            self.frameIndex += 1

        # Gerar o caminho do frame a ser salvo, levando em consideração o numero do frme,
        # nome da pasta, nome do vídeo e índice do recorte
        frame_path = model.frame_path_generator(self.fps,
                                                self.current_time,
                                                folder_name,
                                                self.video_name,
                                                self.frameIndex)

        # Salvar a imagem e exibir mensagem ao usuário
        success = cv2.imwrite(frame_path, selected_area)

        # Valida se o salvamento foi realizado com sucesso
        if success:

            # Calcula o valor do frame, baseado no tempo atual e na taxa de quadros
            frame_number = int((self.current_time / 1000) * self.fps)

            # O 'for' busca obter os 10 frames anteriores e posteriores
            # ao frame atual, afim de salvar seus dados para o processo
            # de Augmentation futuro
            for i in range(-10, 11):

                if frame_number + i >= 1 and i != 0:
                    # Retorna a estrutura dos dados em formato JSON
                    aug_data = model.Augmentation_data_structure(frame_number + i,
                                                                 self.x1,
                                                                 self.x2,
                                                                 self.y1,
                                                                 self.y2,
                                                                 self.video_name,
                                                                 frame_path)

                    # Valida se o novo registro já existe ou não em alguma das outras pastas
                    # O registro é excluido em caso de ser duplicado
                    model.Augmentation_data_checker(aug_data)

                    # Salva a estrutura JSON no arquivo gerado na pasta Augmentation
                    model.Augmentation_data_save(aug_data, folder_name)

            # Mensagem de confirmação da operação
            QMessageBox.information(self, "Sucesso", f"Frame salvo em: {frame_path}")
