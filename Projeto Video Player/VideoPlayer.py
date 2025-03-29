import os
import sys
import ctypes
import time
import cv2

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QFont
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QMainWindow, QPushButton, QSlider, QWidget, QVBoxLayout, \
    QHBoxLayout, QLabel, QShortcut, QApplication

from KeyMapper import KeyMapper
from Model import Model
from SaveMenu import SaveMenu
from FrameCapture import FrameCapture


# PyQt5.QtWidgets contém os elemenos da interface gráfica, como botões, janelas e sliders
# QApplication - Responsável por gerenciar toda a aplicação PyQt
# QMainWindow - Representa a janela principal de um aplicativo PyQt. Permite adicionar menus,
#   barras de ferramentas e widgets centrais.
# QPushButton - Cria um botão interativo. Pode ser clicado para executar ações quando conectado a um slot (função).
# QFileDialog - Exibe uma caixa de diálogo para abrir ou salvar arquivos.
# QSlider - Cria uma barra deslizante para selecionar valores numéricos
# QWidget - Classe base de qualquer componente de interface. Pode ser usado como um container genérico.
# QVBoxLayout - Gerencia o layout na vertical (empilha os widgets um abaixo do outro).
# QHBoxLayout - Gerencia o layout na horizontal (coloca widgets lado a lado).
# QLabel - Exibe texto ou imagens estáticas.
# QShortcut - Cria atalhos de teclado para ações específicas
# QDialog -
# QLineEdit -
# QScrollArea -
# QGridLayout -
# O módulo QtCore contém funcionalidades não gráficas, como controle de tempo, eventos e manipulação de dados.
# Qt - Enumerações e constantes do Qt, como: Qt.AlignTop → Alinha um widget no topo.
# QTimer - Cria eventos recorrentes, como atualização de tempo ou animações.
# O módulo QtGui lida com elementos gráficos, como fontes, cores e atalhos de teclado.
# QKeySequence - Representa atalhos de teclado, como "Ctrl+S" ou "Alt+F4"
# QFont - Define e personaliza fontes de texto.
# QPixmap -
# O módulo QtMultimediaWidgets permite manipular mídia dentro da GUI.
# QVideoWidget - Cria uma área de exibiçãi de vídeo embutido dentro da interface.
# Ele exibe vídeos, mas não contém um player próprio.


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class VideoPlayer(QMainWindow):

    def __init__(self):

        # Herda os métodos da classe pai (QMainWindow)
        super().__init__()

        self.map_window = None
        self.setWindowTitle("Video Player com VLC")  # Define o título da janela do player
        self.setGeometry(100, 100, 900, 500)  # Define a geometria da janela

        # Criando um widget central, ele será responsável por aagrupar o conteúdo da janela
        self.central_widget = QWidget(self)  # Cria uma instância do QWidget
        self.setCentralWidget(self.central_widget)  # Define a instância criada como o central

        # Criando layout horizontal principal do widget central
        self.main_layout = QHBoxLayout()  # Cria uma instância do layout
        self.central_widget.setLayout(self.main_layout)  # Associa o layout ao widget central

        # Cria um novo widget dedicado para o player de vídeo
        self.video_widget = QVideoWidget()  # Cria uma instância do QVideoWidget
        # Associa o widget ao layout central
        # stretch = 1 aumenta o vídeo para ocupar o espaço do vídeo
        self.main_layout.addWidget(self.video_widget, stretch=1)

        # Criando um widget dedicado para os controles, com uma altura fixa
        self.controls_widget = QWidget()  # Cria uma instância do QWidget
        self.controls_widget.setFixedHeight(500)  # Define uma altura fixa para os controles
        self.controls_widget.setFixedWidth(300)  # Define uma largura fixa para os controles

        self.control_layout = QVBoxLayout(self.controls_widget)  # Define um layout vertical para os controles
        self.control_layout.setAlignment(Qt.AlignTop)  # Controles alinhados ao topo

        # Associa o widget ao layout central (na orientação horizontal)
        self.main_layout.addWidget(self.controls_widget)

        # Layout horizontal para alguns do botões de controle
        # o qual sera adicionado posteriormente ao control_layout
        # seguindo a ordem de disposição dos botões
        self.hor_layout = QHBoxLayout()
        self.hor_layout2 = QHBoxLayout()

        # -------------------------------------------------------------------------------------------------------------

        # Criação da Janela do Vídeo, sendo ela uma intância
        # da classe VideoWindow() criada préviamente, além de
        # associar o VLC à janela criada.

        if getattr(sys, 'frozen', False):
            BASE_DIR = sys._MEIPASS  # Diretório temporário do PyInstaller
            sys.stdout = open(os.devnull, 'w')  # Oculta a saída no terminal
            sys.stderr = open(os.devnull, 'w')  # Oculta os erros
        else:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        # Adiciona a pasta do VLC ao PATH
        os.environ["PATH"] += os.pathsep + BASE_DIR

        # Define manualmente o caminho dos plugins do VLC
        vlc_plugin_path = os.path.join(BASE_DIR, "plugins")
        os.environ["VLC_PLUGIN_PATH"] = vlc_plugin_path

        # Caminhos das DLLs
        libvlc_path = os.path.join(BASE_DIR, "libvlc.dll")
        libvlccore_path = os.path.join(BASE_DIR, "libvlccore.dll")

        # Carrega as DLLs do VLC manualmente
        ctypes.CDLL(libvlccore_path)
        ctypes.CDLL(libvlc_path)

        # Agora podemos importar o módulo vlc
        import vlc

        # Testa se o VLC foi carregado corretamente
        print("Versão do VLC:", vlc.libvlc_get_version())

        self.instance = vlc.Instance(f"--plugin-path={BASE_DIR}")  # cria uma instância do framework do VLC
        self.media_player = self.instance.media_player_new()  # cria um novo player de vídeo a partir da instância
        self.media_player.set_hwnd(int(self.video_widget.winId()))  # Vincula o player do VLC à janela criada

        # -------------------------------------------------------------------------------------------------------------

        # Definição elementos de controle (botões e slider)

        self.slider = QSlider(Qt.Horizontal)  # slider
        self.open_button = QPushButton("Abrir Vídeo")  # botão para abrir vídeo
        self.next_frame_btn = QPushButton("Avançar frame")  # botão para Avançar frame
        self.prev_frame_btn = QPushButton("Retroceder frame")  # botão para Retroceder frame
        self.play_button = QPushButton("Play/Pause")  # botão para dar play ou pause
        self.exit_button = QPushButton("Fechar programa")  # botão para sair do programa

        '''
        self.save_ind = QPushButton(
            "Salvar frame como 'Indolor'")  # botão responsável por salvar o frame na pasta 'indolor'
        self.save_pd = QPushButton(
            "Salvar frame como 'Pouca dor'")  # botão responsável por salvar o frame na pasta 'pouca dor'
        self.save_md = QPushButton(
            "Salvar frame como 'Muita dor'")  # botão responsável por salvar o frame na pasta 'muita dor'
        '''

        self.change_keys = QPushButton(
            "Escolher novas teclas de atalho")  # botão responsável por modificar as teclas de atalho
        self.save_menu = QPushButton(
            "Menu de salvamento do vídeo atual")  # botão responsável por abrir o menu de salvamento

        # Definindo slider para o ajuste da velocidade do vídeo

        self.speed_slider = QSlider(Qt.Horizontal)  # slider para a velocidade de reprodução do vídeo
        self.speed_label = QLabel("Velocidade: 1x")  # Exibe a velocidade atual como uma label

        # Configurando slider de velocidade
        self.speed_slider.setMinimum(0)  # Definição do menor índice 0 = 0.25x
        self.speed_slider.setMaximum(4)  # Definição do maior índice 4 = 4x
        self.speed_slider.setTickInterval(1)  # Definindo a taxa de incremento de 1 em 1
        self.speed_slider.setTickPosition(QSlider.TicksBelow)  # Define a posição do ponteiro do slider
        self.speed_slider.setValue(2)  # Definindo o valor (posição) inicial do slider em 1x

        # ------------
        self.capture_frame_btn = QPushButton("Capturar frame")
        # ------------

        # -------------------------------------------------------------------------------------------------------------

        # Inserindo os elementos criados na janela de controles
        # observação: A ordem importa para a visualização

        self.control_layout.addWidget(self.play_button)

        # O layout horizontal deve ser inserido em ordem junto com seus widgets
        self.control_layout.addLayout(self.hor_layout)
        self.hor_layout.addWidget(self.prev_frame_btn)
        self.hor_layout.addWidget(self.next_frame_btn)

        self.time_label = QLabel("00:00 / 00:00")  # Instância de um label (formato "00:00 / 00:00")
        self.control_layout.addWidget(self.time_label)  # Inserção do label como elemento da janela de controles
        self.control_layout.addWidget(self.slider)

        self.speed_label = QLabel("Velocidade: 1x")  # Exibe a velocidade atual
        self.control_layout.addWidget(self.speed_label)
        self.control_layout.addWidget(self.speed_slider)

        # -----------
        self.control_layout.addWidget(self.capture_frame_btn)
        # -----------

        self.control_layout.addWidget(self.open_button)

        # Inserção de labels para as teclas de atalho

        # Inserção de labels para as teclas de atalho
        self.keys_label = QLabel()
        font = QFont("Arial", 10)  # Nome, tamanho, peso (opcional)
        self.keys_label.setFont(font)

        # Define a label como rich text para permitir a inclusão de comandos HTML
        self.keys_label.setTextFormat(Qt.RichText)

        # Valor das teclas de atalho
        self.keys = ["o", " ", "d", "a", "q"]

        self.keys_label.setText(
            "<br>"
            "Teclas de atalho para os controles<br>"
            "<br>"
            f"Abrir um arquivo de vídeo: <b>{self.keys[0]}</b><br>"
            f"Play/Pause: <b>{self.keys[1]}</b><br>"
            f"Avançar frame: <b>{self.keys[2]}</b><br>"
            f"Retroceder frame: <b>{self.keys[3]}</b><br>"
            f"Sair do programa: <b>{self.keys[4]}</b><br>"
            "<br>"
        )
        self.control_layout.addWidget(self.keys_label)

        self.control_layout.addWidget(self.save_menu)
        self.control_layout.addWidget(self.change_keys)
        self.control_layout.addWidget(self.exit_button)

        # -------------------------------------------------------------------------------------------------------------

        # Associa as funções de controle aos botões criados

        self.open_button.clicked.connect(self.open_file)
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.slider.sliderMoved.connect(self.set_position)
        self.exit_button.clicked.connect(self.exit_program)
        self.next_frame_btn.clicked.connect(self.next_frame)
        self.prev_frame_btn.clicked.connect(self.prev_frame)
        self.speed_slider.valueChanged.connect(self.change_speed)
        self.change_keys.clicked.connect(self.key_mapping)

        # -----------------
        self.capture_frame_btn.clicked.connect(self.frame_capture)
        # -----------------

        self.save_menu.clicked.connect(self.open_save_menu)

        # Timer responsável por atualizar a barra de progresso

        self.timer = QTimer(self)  # Cria uma instância do temporizador
        self.timer.setInterval(500)  # Define um intervalo de tempo de 500ms
        self.timer.timeout.connect(self.update_slider)  # O slider é atualizado a cada 500ms, utilizando a fução update

        # -------------------------------------------------------------------------------------------------------------

        # Associando teclas de atalho a cada uma das funções dos botões

        self.open_button_shortcut = QShortcut(QKeySequence(self.keys[0]), self)
        self.open_button_shortcut.activated.connect(self.open_file)

        self.play_button_shortcut = QShortcut(QKeySequence(self.keys[1]), self)
        self.play_button_shortcut.activated.connect(self.toggle_play_pause)

        self.next_frame_shortcut = QShortcut(QKeySequence(self.keys[2]), self)
        self.next_frame_shortcut.activated.connect(self.next_frame)

        self.prev_frame_shortcut = QShortcut(QKeySequence(self.keys[3]), self)
        self.prev_frame_shortcut.activated.connect(self.prev_frame)

        self.exit_shortcut = QShortcut(QKeySequence(self.keys[4]), self)
        self.exit_shortcut.activated.connect(self.exit_program)

        # Variável de nome do arquivo de vídeo
        # e do caminho da imagem carregada

        self.video_name = ""
        self.file_name = None
        self.extension = None

        # self.event_manager = self.media_player.event_manager()
        # self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.reload_video)
        self.timer.timeout.connect(self.check_time_before_end)

    # -------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------
    # -------------------------------------------------------------------------------------------------------------

    def open_file(self):

        model = Model()
        self.file_name = model.open_video(parent=self)

        if self.file_name:
            self.start_video(self.file_name)
            self.video_name = os.path.basename(self.file_name)
            self.extension = self.video_name[-4:]
            print(self.extension)
            self.video_name = self.video_name[:-4]

    def start_video(self, file_name):

        media = self.instance.media_new(file_name)  # Cria um objeto de mídia a parir da instância do  VLC
        self.media_player.set_media(media)  # O objeto de mídia (media) é atribuído ao player de vídeo
        self.media_player.audio_set_mute(True)  # Tira o audio do vídeo
        self.media_player.play()  # O vlc inicia a reprodução do vídeo carregado
        self.timer.start()  # Inicia o timer da barra de progresso

        # Iniciar o timer de atualização do slider
        self.update_slider()
        self.timer.timeout.connect(self.update_slider)
        self.timer.start(1000)  # Atualiza a cada segundo

    def check_time_before_end(self):
        """Verifica o tempo restante e chama uma função 1 segundo antes do vídeo encerrar."""
        if self.media_player is not None:
            duration = self.media_player.get_length()  # Duração total do vídeo
            current_time = self.media_player.get_time()  # Tempo atual do vídeo

            # Verifica se falta 1 segundo para o fim do vídeo
            if duration - current_time <= 500:  # 1000 ms = 1 segundo
                self.timer.stop()  # Para o timer
                self.reload_video()  # Chama a função desejada

    def reload_video(self):

        self.start_video(self.file_name)

    def toggle_play_pause(self):

        # Valida se o vídeo está reproduzindo
        # Em caso positivo, o vídeo é pausado. Em caso negativo o vídeo é reproduzido

        if self.media_player.is_playing():
            self.media_player.pause()

        else:
            self.media_player.play()

    def next_frame(self):

        # Pausa o vídeo, caso ele já não esteja pausado
        if self.media_player.is_playing():
            self.media_player.pause()

        # Utiliza um comando do próprio vlc para avançar o frame
        self.media_player.next_frame()

    def prev_frame(self):

        # Pausa o vídeo, caso ele já não esteja pausado
        if self.media_player.is_playing():
            self.media_player.pause()

        # OBS: o vlc não possui uma função pronta para retroceder, por isso, é necessário
        # retroceder manualmente retrocedendo o tempo do vídeo referente à um frame
        fps = self.media_player.get_fps()  # Obtém FPS do vídeo
        if fps > 0:
            frame_time = int(1000 / fps)  # Tempo de um frame em ms
            current_time = self.media_player.get_time()  # Tempo atual em ms
            new_time = max(0, current_time - frame_time)  # Garante que não vá abaixo de 0
            self.media_player.set_time(new_time)  # Define o novo tempo

    # --------------------------------------
    def frame_capture(self):

        # Pausa o vídeo, caso ele já não esteja pausado
        if self.media_player.is_playing():
            self.media_player.pause()

        # O VLC não tem uma função pronta para retornar o numero do frame atual, contudo é possível obter este valor
        # por meio do valor de tempo do frame atual e pela taxa de quadros do vídeo (FPS), com isso temos a equação:
        # frame atual = tempo atual (ms)/1000 * taxa de quadros

        current_time = self.media_player.get_time()  # tempo do frame atual
        fps = self.media_player.get_fps()  # taxa de quadros do vídeo
        frame = self.get_frame()

        capture = FrameCapture(self.video_name, current_time, fps, frame, self.extension)
        capture.exec_()

    def get_frame(self):

        width = self.media_player.video_get_width()
        height = self.media_player.video_get_height()

        if width == 0 or height == 0:
            print("Erro: Nenhum vídeo carregado ou reprodução ainda não começou.")
            return None

        # Define o caminho do snapshot temporário
        snapshot_path = "temp_frame.png"

        # Captura um snapshot do frame atual
        self.media_player.video_take_snapshot(0, snapshot_path, width, height)
        time.sleep(0.2)  # Pequeno delay para garantir que o snapshot foi salvo

        if os.path.exists(snapshot_path):
            frame = cv2.imread(snapshot_path)  # Carrega a imagem com OpenCV
            os.remove(snapshot_path)  # Remove o arquivo temporário

            # Corrige a rotação (gira 90° no sentido horário)
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            return frame
        else:
            print("Erro ao capturar o frame.")
            return None

    def change_speed(self):

        speed_values = [0.25, 0.5, 1.0, 2.0, 4.0]  # Lista de valores de reprodução

        index = self.speed_slider.value()  # Obtém o índice da velocidade
        speed = speed_values[index]  # Obtém a taxa correspondente
        self.media_player.set_rate(speed)  # Define a nova taxa de reprodução
        self.speed_label.setText(f"Velocidade: {'%0.2f' % speed}x")  # Atualiza o rótulo

    def set_position(self, value):

        if self.media_player is not None:
            # observação: value está vindo diretamente do QSlider sempre que o usuário interage com ele.
            # Quando o usuário move o slider, o Qt emite sliderMoved(int) automaticamente, passando o valor
            # do slider para set_position.
            # O connect() pode se conectar a funções que aceitam os argumentos esperados pelo sinal.
            # No caso do sliderMoved, ele emite um único inteiro (o valor do slider), e a função
            # set_position(self, value) está esperando exatamente um argumento além de self.

            duration = self.media_player.get_length()  # Obtém a duração total do vídeo
            # Obtem a duração do vídeo de acordo com a posição do slider
            new_time = int((value / self.slider.maximum()) * duration)
            # Define o tempo de vídeo de acordo com o tempo obtido pela posição do slider
            self.media_player.set_time(new_time)

    def update_slider(self):

        if self.media_player is not None:

            duration = self.media_player.get_length()  # Duração total do vídeo em ms
            current_time = self.media_player.get_time()  # Tempo atual do vídeo em ms

            if duration > 0:  # Garante que a duração do vídeo é válida

                # Define um novo valor para o slider, levando em consideração o tempo de vídeo e o limite do slider
                slider_value = int((current_time / duration) * self.slider.maximum())
                self.slider.setValue(slider_value)

            # Atualiza o rótulo do tempo na interface
            current_sec = current_time // 1000
            duration_sec = duration // 1000
            self.time_label.setText(
                f"{current_sec // 60:02}:{current_sec % 60:02} / {duration_sec // 60:02}:{duration_sec % 60:02}")

    def open_save_menu(self):

        menu = SaveMenu(self.video_name)
        menu.exec_()

    def key_mapping(self):

        if not hasattr(self, "map_window") or self.map_window is None:
            self.map_window = KeyMapper()  # Criar um atributo da classe principal

        self.map_window.setModal(True)  # Bloqueia a interação na principal
        self.map_window.exec_()  # Executar como diálogo modal

        self.keys = self.map_window.keyValues

        # Recriando os atalhos
        self.open_button_shortcut.setKey(QKeySequence(self.keys[4]))
        self.play_button_shortcut.setKey(QKeySequence(self.keys[0]))
        self.next_frame_shortcut.setKey(QKeySequence(self.keys[1]))
        self.prev_frame_shortcut.setKey(QKeySequence(self.keys[2]))
        self.exit_shortcut.setKey(QKeySequence(self.keys[3]))

        # Atualizando a exibição das teclas de atalho na label
        self.keys_label.setText(
            "<br>"
            "Teclas de atalho para os controles<br>"
            "<br>"
            f"Abrir um arquivo de vídeo: <b>{self.keys[4]}</b><br>"
            f"Play/Pause: <b>{self.keys[0]}</b><br>"
            f"Avançar frame: <b>{self.keys[1]}</b><br>"
            f"Retroceder frame: <b>{self.keys[2]}</b><br>"
            f"Sair do programa: <b>{self.keys[3]}</b><br>"
            "<br>"
        )

    def exit_program(self):
        if self.media_player:
            self.media_player.stop()
            self.media_player.release()
            del self.media_player  # Remove a instância corretamente

        self.close()  # Fecha a janela principal
        QApplication.quit()  # Finaliza o loop da aplicação corretamente
