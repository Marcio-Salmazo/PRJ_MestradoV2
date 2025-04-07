import os
import json
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog

class Model:

    def __init__(self):

        self.json_file_path = None


    def manage_dirs(self, folder_name):

        # cria o diretório para armazenar os frames (caso não exista previamente)
        os.makedirs(folder_name, exist_ok=True)

    def frame_path_generator(self, fps, current_time, folder_name, video_name, index):

        if fps > 0:
            frame_number = int((current_time / 1000) * fps)
        else:
            frame_number = 'unknown'

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

        os.remove(path)  # Remove o arquivo

    def file_exists(self, path):

        return os.path.exists(path)

    def list_directory(self, path):

        return os.listdir(path)

    def join_path(self, image_path, path):

        return os.path.join(path, image_path)

    def validate_type(self, image_path):

        # Valida se o arquivo da pasta possui a terminação '.png' ou '.jpg'
        # Em outras palavras, é validado se o arquivo é uma imagem. Caso não seja
        # validado, ele será apenas ignorado
        return image_path.lower().endswith(('.png', '.jpg'))

    def check_existence(self, frame):

        folders = ["Indolor", "Pouca dor", "Muita dor", "Incerto"]

        for dirs in folders:

            if not os.path.exists(dirs):
                continue

            for img_file in os.listdir(dirs):

                img_path = os.path.join(dirs, img_file)  # Caminho completo do arquivo

                # Carrega a imagem salva da pasta
                saved_image = cv2.imread(img_path)

                if saved_image is None:
                    print(f"Erro ao carregar {img_path}")
                    continue

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

    def Augmentation_data_structure(self, folder_name, frame_number, x1, x2, y1, y2, video_name):

        dataStructure = {
            "nome do video": video_name,
            "categoria": folder_name,
            "frame": frame_number,
            "coordenadas": {"x1": x1,
                            "x2": x2,
                            "y1": y1,
                            "y2": y2}
        }

        return dataStructure

    def Augmentation_data_save(self, new_data, folder_name):

        json_path = os.path.join("Augmentation", folder_name, f"Augmentation_{folder_name}.json")

        if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
            with open(json_path, "r", encoding="utf-8") as file:
                dados = json.load(file)
        else:
            print("Arquivo não existe ou está vazio, inicializando lista de dados como lista vazia")
            dados = []  # Começa com lista vazia se o arquivo está vazio ou não existe

        if new_data not in dados:

            dados.append(new_data)

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
        else:
            print("Dados duplicados ignorados")
