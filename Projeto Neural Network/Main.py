from CNNModel import CNNModel
from Trainer import Trainer
from DataLoader import DataLoader
import tkinter as tk
from tkinter import filedialog


"""
O tkinter é utilizado para exibir janela do explorer a fim de selecionar a pasta contendo o Dataset.
    * root = tk.Tk() - instância do tkinter
    * root.withdraw() -  Oculta a janela principal (para exibir apenas o pop-up) 
    * filedialog.askdirectory(title="") - Abre a janela de seleção de pastas e retorna o caminho escolhido
"""
root = tk.Tk()
root.withdraw()
path = filedialog.askdirectory(title="Selecione a pasta contendo o Dataset")

"""
Cria uma intância do DataLoader para definir os dados para treinamento e validação
por meio dos atributos train_generator e val_generator estipulados no momento da
instância da classe
"""
data_loader = DataLoader(path)
train_data = data_loader.train_generator
val_data = data_loader.val_generator

"""
A instância da classe CNNModel retorna a estrutura do modelo por meio do
atributo .model (o qual é definido por meio do método build_model() da classe)
"""
cnn = CNNModel(num_classes=len(train_data.class_indices))
model = cnn.model
print(model)

"""
O modelo é compilado e os dados de treinamento são exibidos
"""
# --------
# --------
fileName = 'eyes_250ep_train70'
# --------
# --------
trainer = Trainer(model, train_data, val_data, epochs=250)
trainer.compile_and_train(fileName)

"""
Os pesos do modelo são salvos:
"""
model.save_weights(fileName+'.weights.h5')
