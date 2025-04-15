from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QWidget, QPushButton, QLabel, QGridLayout

from Model import Model


class SaveMenu(QDialog):

    # Construtor da classe
    def __init__(self, video_name):

        # Realiza a chamada dos métodos da classe pai (QDialog)
        super().__init__()

        self.setWindowTitle("Menu de salvamento")  # Define o título da janela
        self.setGeometry(150, 150, 800, 600)  # Define as dimensões da janela criada

        # Layout principal do QDialog
        # Em um QDialog, para que os widgets apareçam, é necessário
        # definir um layout principal para a própria janela (self).
        self.layout = QVBoxLayout(self)

        # Define um dicionário para definir a categoria de cada pasta, bem como o caminho
        # Dicionário -> "Categoria" : "Caminho"
        # Nesse caso, os valores são iguais por que as pastas estão no mesmo diretório do arquivo .py
        # com isso, não precisa especificar o caminho
        self.folders = {
            "Indolor": "Indolor",
            "Pouca dor": "Pouca dor",
            "Muita dor": "Muita dor"
        }

        # Criar uma área de rolagem para exibir imagens, independente do tamanho da janela
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

        # ---------------------------------------------------------------------------------------------------------------------------

        self.close_btn = QPushButton("Fechar")  # Cria um botão para fechar a janela
        self.layout.addWidget(self.close_btn)  # Adiciona o botão ao layout principal da janela
        self.close_btn.clicked.connect(self.close)  # Atribui a função de fechar a janela ao botão

        # ---------------------------------------------------------------------------------------------------------------------------

        # Recebe o nome do vídeo atual
        self.videoName = video_name
        # Chamada de função responsáverl por carregar imagens das pastas
        self.load_images()

    # A função a seguir serve para quando é necessário atualizar um layout removendo os
    # elementos antigos antes de adicionar novos.
    def clear_layout(self, layout):

        # layout.count() retorna o número de widgets ou sublayouts dentro do layout.
        # O while garante que os elementos continuem sendo removidos até que não reste nenhum.
        while layout.count():

            # Remove o primeiro item do layout e o retorna
            # É importante ressaltar que Remove o QLayout pode
            # conter tanto widgets (QWidget) quanto
            # sublayouts (QLayout), é necessário verificar o que foi removido.
            item = layout.takeAt(0)

            # Verifica se o item é um widget
            if item.widget():
                # Remove o widget da memória de forma segura.
                # O deleteLater() é usado no PyQt para evitar
                # problemas de acesso a objetos deletados prematuramente.
                item.widget().deleteLater()

            # Verifica se o item é layout
            elif item.layout():

                # A propria função é chamada recursivamente de forma a limpar todos
                # os widgets contidos nele
                self.clear_layout(item.layout())
                item.layout().deleteLater()  # Remove o layout da memória após limpá-lo.

    def load_images(self):

        # Limpa os widgets existentes no layout antes de recarregar novas imagens.
        # Evitando que a interface acumule elementos repetidos
        self.clear_layout(self.scroll_layout)
        model = Model()

        # Percorre cada um dos itens do dicionário das pastas (retornando a categoria e o caminho)
        # possibilitando a realização do processo de carregamento de imagens para cada uma das pastas
        for category, path in self.folders.items():

            # Se a pasta não existir no caminho definido em 'path'
            # o algoritmo pula a pasta e continua a execução

            if not model.file_exists(path):
                continue

            # Adiciona um layout como título para cada categoria
            # o label recebe o nome da categoria obtido pela
            # variável 'category' proveniente do dicionário

            category_label = QLabel(f"<b>{category}</b>")
            self.scroll_layout.addWidget(category_label)

            # Criar um layout de grade para organizar as imagens
            # A grid é definida para cada uma das pastas

            grid_layout = QGridLayout()
            row, col = 0, 0  # Inicia a posição da primeira imagem na linha 0, coluna 0.

            # O loop percorre todos os itens em uma determinada pasta
            # definida por 'path'
            for img_file in model.list_directory(path):

                # Valida quais arquivos são referentes ao vídeo atual
                if self.videoName in img_file:

                    # Obtém o caminho completo do arquivo (unindo path com o nome do arquivo de imagem)
                    img_path = model.join_path(img_file, path)

                    if not model.validate_type(img_file):
                        continue

                    # Criar um QLabel para exibir a imagem
                    # Para isso é utilizado um pixmap, o qual é
                    # designado para exibir imagens de modo otimizado
                    # sem ter foco na manipulação da imagem

                    pixmap = QPixmap(img_path).scaled(100, 100)  # Instância do pixmap da imagem atual
                    img_label = QLabel()  # Instância de uma label que contém o pixmap
                    img_label.setPixmap(pixmap)  # Associa o pixmap ao label da imagem

                    # Criar um botão para excluir a imagem
                    delete_button = QPushButton("Excluir")

                    # Ao ser pressionado o botão chama a função delete_image
                    # Lambda permite a chamada de uma função com parâmetros

                    # Observação:
                    # O evento clicked do botão envia automaticamente um argumento booleano (checked)
                    # O checked não é usado, mas precisa estar no lambda para evitar erros, uma vez que
                    # alguns widgets no PyQt podem funcionar como botões de alternância (toggle buttons),
                    # enviando True quando ativados e False quando desativados. Mesmo que o nosso botão não
                    # use isso, o PyQt exige que esse argumento seja tratado.
                    delete_button.clicked.connect(lambda checked, p=img_path: self.delete_image(p))

                    # Label para exibir o nome de cada frame
                    frame_name = QLabel()
                    frame_name.setText(f"{img_file}")

                    # Adicionar a imagem do frame e o botão de deleção
                    # ao layout da grid, definindo a linha e a coluna
                    # da grid onde será a inserção
                    grid_layout.addWidget(frame_name, row, col)
                    grid_layout.addWidget(img_label, row + 1, col)
                    # A inclusão do botão vem na linha inferior de onde a imagem está alocada
                    grid_layout.addWidget(delete_button, row + 2, col)

                    # Aqui é feito o controle da disposição das imagens
                    # A coluna é incrementada após a inserção da primeira imagem
                    col += 1
                    # Caso já tenham 5 colunas de imagens (0,1,2,3,4)
                    # a proxima imagem é inserida na próxima linha da grid
                    # resetando o valor da coluna
                    if col > 4:
                        col = 0
                        row += 3

            # Após a definição e organização da grid, o seu layout
            # é inserido ao scroll de rolagem
            self.scroll_layout.addLayout(grid_layout)

    def delete_image(self, img_path):

        model = Model()
        try:
            model.remove_file(img_path)  # Remove o arquivo
            self.load_images()  # Recarrega a interface após a exclusão

        except Exception as e:  # Em caso de erro
            print(f"Erro ao excluir {img_path}: {e}")

        # Função para deletar os dados JSON de um frame excluido
        model.Augmentation_data_delete(img_path)
