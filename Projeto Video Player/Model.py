import os

import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog


class Model:

    def __init__(self):

        var = 0
        # self.fps = None
        # self.current_time = None
        # self.folder_name = None
        # self.video_name = None

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
        
        #INTERFACE
        file_name, _ = QFileDialog.getOpenFileName(parent, "Abrir Vídeo", "", "Arquivos de Vídeo (*.mp4 *.avi *.mkv)")

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

        folders = ["Indolor", "Pouca dor", "Muita dor"]

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

