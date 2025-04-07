# Classe responsável pela janela de configuração da atribuição de teclas
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QDialog, QVBoxLayout, QWidget, QPushButton


class KeyMapper(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mapear teclas de atalho")
        self.setGeometry(100, 100, 250, 120)

        # Layout principal do QDialog
        # Em um QDialog, para que os widgets apareçam, é necessário
        # definir um layout principal para a própria janela (self).
        self.dialog_layout = QVBoxLayout(self)

        # Criando um widget dedicado para os controles, com uma altura fixa
        self.main_widget = QWidget()  # Cria uma instância do QWidget
        self.main_widget.setFixedHeight(500)  # Define uma altura fixa para os controles

        # Criando um layout específico para o main_widget
        self.main_layout = QVBoxLayout(self.main_widget)  # Define um layout vertical para os controles
        self.main_layout.setAlignment(Qt.AlignTop)  # Controles alinhados ao topo

        # Adicionando o widget de controles ao layout principal do QDialog
        self.dialog_layout.addWidget(self.main_widget)

        # Valores das teclas mapeadas
        self.keyValues = ["o", " ", "d", "a", "q"]

        # Criando os campos de entrada com seus respectivos rótulos
        # self.input1_layout = QHBoxLayout() -> Layout horizontal para acomodar o label e o campo de entrada lado-a-lado
        # self.input1_label = QLabel("Nome:") -> Label da entrada (indica o que o usuário deve inserir)
        # self.input1 = QLineEdit() -> Campo de entrada
        # self.input1.setMaxLength(1) -> Tamanho máximo do campo de entrada (máximo)
        # self.input1.setAlignment(Qt.AlignCenter) -> Alinhar o texto de entrada no centro
        # self.input1_layout.addWidget(self.input1_label) -> Adiciona a label ao layout horizontal
        # self.input1_layout.addWidget(self.input1) -> Adiciona o campo de entrada ao layout horizontal
        # self.main_layout.addLayout(self.input1_layout) -> Adiciona o layout horizontal ao layout principal

        self.input1_layout = QHBoxLayout()
        self.input1_label = QLabel("Play/Pause:")
        self.input1 = QLineEdit()
        self.input1.setMaxLength(1)
        self.input1.setAlignment(Qt.AlignCenter)
        self.input1_layout.addWidget(self.input1_label)
        self.input1_layout.addWidget(self.input1)
        self.main_layout.addLayout(self.input1_layout)

        self.input2_layout = QHBoxLayout()
        self.input2_label = QLabel("Avançar Frame:")
        self.input2 = QLineEdit()
        self.input2.setMaxLength(1)
        self.input2.setAlignment(Qt.AlignCenter)
        self.input2_layout.addWidget(self.input2_label)
        self.input2_layout.addWidget(self.input2)
        self.main_layout.addLayout(self.input2_layout)

        self.input3_layout = QHBoxLayout()
        self.input3_label = QLabel("Retroceder Frame:")
        self.input3 = QLineEdit()
        self.input3.setMaxLength(1)
        self.input3.setAlignment(Qt.AlignCenter)
        self.input3_layout.addWidget(self.input3_label)
        self.input3_layout.addWidget(self.input3)
        self.main_layout.addLayout(self.input3_layout)

        self.input7_layout = QHBoxLayout()
        self.input7_label = QLabel("Sair do programa:")
        self.input7 = QLineEdit()
        self.input7.setMaxLength(1)
        self.input7.setAlignment(Qt.AlignCenter)
        self.input7_layout.addWidget(self.input7_label)
        self.input7_layout.addWidget(self.input7)
        self.main_layout.addLayout(self.input7_layout)

        self.input8_layout = QHBoxLayout()
        self.input8_label = QLabel("Abrir arquivo de vídeo:")
        self.input8 = QLineEdit()
        self.input8.setMaxLength(1)
        self.input8.setAlignment(Qt.AlignCenter)
        self.input8_layout.addWidget(self.input8_label)
        self.input8_layout.addWidget(self.input8)
        self.main_layout.addLayout(self.input8_layout)

        # Criação dos botões
        self.confirm_button = QPushButton("Confirmar")
        self.close_button = QPushButton("Fechar", self)

        # Adicionando os botões ao layout
        self.main_layout.addWidget(self.confirm_button)
        self.main_layout.addWidget(self.close_button)

        # Conectando os botões às funções
        self.close_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.confirm_action)

    def confirm_action(self):

        # Obtendo os valores inseridos pelo usuário
        self.keyValues = [self.input1.text(),
                          self.input2.text(),
                          self.input3.text(),
                          self.input7.text(),
                          self.input8.text()]

        self.accept()
