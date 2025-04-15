import os
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog


class Model:

    def __init__(self):

        # Inicialização do caminho dos arquivos JSON para augmentation
        self.json_file_path = None

    def manage_dirs(self, folder_name):

        # cria o diretório para armazenar os frames (caso não exista previamente)
        os.makedirs(folder_name, exist_ok=True)

    def frame_path_generator(self, fps, current_time, folder_name, video_name, index):

        # Função responsável por gerar o caminho dos frames à serem salvos
        # levando em consideração o numero do frame, o nome de sua classe, o nome do vídeo
        # correspondente ao frame e qual o frame retirado da imagem principal

        # Cálculo do numero do frame no vídeo (baseado no fps e no tempo de vídeo atual)
        if fps > 0:
            frame_number = int((current_time / 1000) * fps)
        else:
            frame_number = 'unknown'

        # Retorno da string do caminho
        return os.path.join(folder_name, f"frame_{frame_number}_{video_name}_{index}.png")

    def open_video(self, parent=None):

        # QFileDialog.getOpenFileName() abre uma janela de seleção de aquivos, retornando dois valores:
        # 1 - O caminho do arquivo selecionado (exemplo: "C:/Videos/filme.mp4").
        # 2 - Um valor extra que contém o filtro de arquivos aplicado

        # Parâmetros utilizados
        # self - Referência à janela principal
        # "Abrir Vídeo" - Título da janela de seleção de arquivos.
        # "" - Diretório inicial (se vazio, abre no último local acessado).
        # "Arquivos de Vídeo (*.mp4 *.avi *.mkv)" - Filtro para exibir apenas arquivos de vídeo.

        # INTERFACE
        file_name, _ = QFileDialog.getOpenFileName(parent, "Abrir Vídeo", "", "Arquivos de Vídeo (*.mp4 *.avi *.mkv "
                                                                              "*.mov)")

        return file_name

    def remove_file(self, path):

        # Remove o arquivo designado pelo caminho 'path'
        os.remove(path)

    def file_exists(self, path):

        # Verifica se o caminho especificado em path existe ou não
        return os.path.exists(path)

    def list_directory(self, path):

        # Retorna todos os itens contido no caminho
        # especificado pelo caminho 'path'
        return os.listdir(path)

    def join_path(self, image_path, path):

        # Retorna o caminho completo do frame, unindo o caminho
        # especificado ao nome do frame
        return os.path.join(path, image_path)

    def validate_type(self, image_path):

        # Valida se o arquivo da pasta possui a terminação '.png' ou '.jpg'
        # Em outras palavras, é validado se o arquivo é uma imagem. Caso não seja
        # validado, ele será apenas ignorado
        return image_path.lower().endswith(('.png', '.jpg'))

    def check_existence(self, frame):

        # Função responsável por verificar se um frame a ser salvo já existe
        # dentro de alguma das pastas de classificação definida por 'folders'
        folders = ["Indolor", "Pouca dor", "Muita dor", "Incerto"]

        # Loop para percorrer cada uma das pastas existentes
        for dirs in folders:

            # Pula uma das pastas caso ela não tenha sido criado
            if not os.path.exists(dirs):
                continue

            # Loop para percorrer cada um dos frame presentes na pasta selecionada
            for img_file in os.listdir(dirs):

                # Caminho completo do arquivo
                img_path = os.path.join(dirs, img_file)

                # Carrega a imagem salva da pasta
                saved_image = cv2.imread(img_path)

                # Continua a execução caso a imagem avaliada não exista
                if saved_image is None:
                    print(f"Erro ao carregar {img_path}")
                    continue

                # Valida se a imagem a ser salva já existe (tendo sido salva préviamente)
                # Em caso afirmativo, o frame salvo previamente é excluído
                if saved_image.shape == frame.shape and np.array_equal(saved_image, frame):
                    print(f"Imagem duplicada encontrada e removida: {img_path}")
                    os.remove(img_path)  # Remove a imagem duplicada
                    return True

    # ------------------------------------------------------------------------------------------------------------------
    #    FUNÇÕES REFERENTES AO TRATAMENTO DE DADOS DE AUGMENTATION
    # ------------------------------------------------------------------------------------------------------------------

    def Augmentation_folder_structure(self):

        # A função organiza a estrutura de subpastas
        # cada uma conterá um arquivo com os dados dos frames
        # à serem salvos para o aumento de dados
        aug = 'Augmentation'
        os.makedirs(aug, exist_ok=True)

        subfolders = ["Indolor", "Pouca dor", "Muita dor", "Incerto"]
        for sub in subfolders:
            sub_path = os.path.join(aug, sub)
            os.makedirs(sub_path, exist_ok=True)

            '''
            obs: A forma como o os.path.join opera é unindo o 
            caminho pré-formado do primeiro argumento com o nome
            da pasta ou arquivo do segundo parâmetro, completando
            o caminho até determinado documento
            '''
            json_file_name = f"Augmentation_{sub}.json"
            self.json_file_path = os.path.join(sub_path, json_file_name)

            '''
            obs2: A função with open(txt_file_name, "w") as file
            cria o arquivo txt definido pelo caminho gerado em 
            txt_file_path e permite realizar alguma operação inicial
            de acordo com o segundo parâmetro, sendo
                'w' - write
                'r' - read   
            como nada deve ser escrito por enquanto, utiliza-se o pass
            para sair da função 
            '''
            with open(self.json_file_path, "w") as file:
                pass

    def Augmentation_data_structure(self, frame_number, x1, x2, y1, y2, video_name, frame_path):

        # Função responsável por gerar a estrutura em JSON a ser salva
        dataStructure = {
            "nome do video": video_name,
            "frame": frame_number,
            "coordenadas": {"x1": x1,
                            "x2": x2,
                            "y1": y1,
                            "y2": y2},
            "caminho": frame_path
        }

        return dataStructure

    def Augmentation_data_save(self, new_data, folder_name):

        # Função responsável por salvar um novo registro ao arquivo JSON definido
        # por meio do caminho especificado em 'json_path'
        json_path = os.path.join("Augmentation", folder_name, f"Augmentation_{folder_name}.json")

        # Abre o arquivo designado por 'json_path' caso ele existe e caso ele
        # tenha registros gravados. Caso contrário, o registro é inicializado como uma lista vazia
        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
            with open(json_path, "r", encoding="utf-8") as file:
                dados = json.load(file)
        else:
            # print("Arquivo não existe ou está vazio, inicializando lista de dados como lista vazia")
            dados = []  # Começa com lista vazia se o arquivo está vazio ou não existe

        # Valida se o registro a ser salvo já existe, ou não. Em caso afirmativo, os dados são ignorados
        # em caso negativo, os registros são salvos
        if new_data not in dados:

            dados.append(new_data)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        else:
            print("Dados duplicados ignorados")

    def Augmentation_data_checker(self, new_data):

        # Função responsável por validar se um registro a ser salvo já existe
        # em alguns dos outros arquivos JSON existentes em diferentes classes,
        # as quais são definidas pela variável 'folders'
        folders = ["Indolor", "Pouca dor", "Muita dor", "Incerto"]

        # Loop para percorrer cada uma das classes (pastas)
        for dirs in folders:

            # Caso alguma não exista, o código deve continuar normalmente
            if not os.path.exists(dirs):
                continue

            # Obtem o caminho completo do arquivo JSON a ser analisado
            json_path = os.path.join("Augmentation", dirs, f"Augmentation_{dirs}.json")

            # Abre o arquivo designado por 'json_path' caso ele exista e caso ele
            # tenha registros gravados. Caso contrário, o registro é inicializado como uma lista vazia
            if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                with open(json_path, "r", encoding="utf-8") as file:
                    dados = json.load(file)
            else:
                dados = []

            # Cria uma cópia do novo registro new_data sem o campo 'caminho'. Ele precisa ser ignorado
            # uma vez que o caminho depende da pasta (classe) que ele está inserido
            # Foi utilizado um dicionário por compreensão (dict comprehension)
            # para copiar todas as chaves e valores de new_data, exceto "caminho".
            # k -> chave e v -> valor
            new_registro_filtered = {k: v for k, v in new_data.items() if k != "caminho"}

            # Lista de registros a manter (os que não são considerados duplicatas)
            # Aqui é criada uma lista vazia que será preenchida apenas com os registros válidos, ou seja,
            # aqueles que não são iguais a new_data (ignorando o campo "caminho").
            novos_dados = []

            # Para cada registro no JSON (dados), criamos uma versão registro_filtered, sem o campo "caminho",
            # da mesma forma que foi feita com new_data_filtered.
            for registro in dados:

                # Um registro é analisado, removendo o campo caminho. Caso este registro
                # seja igual a new_data_filtered, o registro é ignorado, se não, ele é
                # adicionado à lista novos_dados
                registro_filtered = {k: v for k, v in registro.items() if k != "caminho"}
                if registro_filtered == new_registro_filtered:

                    # Nada é feito, o registro é ignorado
                    continue

                novos_dados.append(registro)

            # Salva de volta o JSON
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(novos_dados, file, indent=4, ensure_ascii=False)

    def Augmentation_data_delete(self, image_path):

        # Função responsável por excluir registros do JSON, caso ele
        # contenha o caminho de um frame que foi excluido em SaveMenu,
        # levando em consideração cada uma das classes definidas pela variável 'folders'
        folders = ["Indolor", "Pouca dor", "Muita dor", "Incerto"]

        # Loop para percorrer cada uma das classes (pastas)
        for dirs in folders:

            # Caso alguma não exista, o código deve continuar normalmente
            if not os.path.exists(dirs):
                continue

            # Obtem o caminho completo do arquivo JSON a ser analisado
            json_path = os.path.join("Augmentation", dirs, f"Augmentation_{dirs}.json")

            # Abre o arquivo designado por 'json_path' caso ele exista e caso ele
            # tenha registros gravados. Caso contrário, o registro é inicializado como uma lista vazia
            if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
                with open(json_path, "r", encoding="utf-8") as file:
                    dados = json.load(file)
            else:
                print("Arquivo não existe ou está vazio, inicializando lista de dados como lista vazia")
                dados = []  # Começa com lista vazia se o arquivo está vazio ou não existe

            # Filtra todos os registros que NÃO possuem o caminho a ser removido
            filtered_data = [registro for registro in dados if registro.get("caminho") != image_path]

            # Salva os dados atualizados de volta no arquivo
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(filtered_data, f, indent=4, ensure_ascii=False)
