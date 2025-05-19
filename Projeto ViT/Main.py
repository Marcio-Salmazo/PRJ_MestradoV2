import DataLoader
import ModelCreator

img_size = 255  # Tamanho das imagens quadradas (H ou W)
batch_size = 16  # Define a quantidade de imagens carregadas por vez

loader = DataLoader.DataLoader(img_size, batch_size)  # Instância da classe DataLoader
path = loader.load_path()  # Busca do caminho até o datapath
trainGen, ValGen = loader.process_data(path)  # Recebe os subsets de treino e validação

# Definição dos parâmetros para o ViT
input_shape = (img_size, img_size, 3)
patch_size = 16
num_patches = (img_size // patch_size) ** 2
projection_dim = 64
transformer_layers = 8
num_heads = 4
mlp_units = 128
num_classes = trainGen.num_classes

# Chamada do modelo
model = ModelCreator.ModelCreator(input_shape, patch_size, num_patches, projection_dim,
                                  transformer_layers, num_heads, mlp_units, num_classes)

model.vit_classifier(trainGen, ValGen, 2)
