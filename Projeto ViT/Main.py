import DataLoader
import ModelCreator

img_size = 256  # Tamanho das imagens quadradas (H ou W)
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
model_to_train = model.vit_classifier()
model.vit_compile_train(model_to_train, trainGen, ValGen, 20)

# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------
# ----------------------------------- AREA DE TESTES ------------------------------------
# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------

# TESTE PARA INTEGRIDADE DOS DADOS

'''
# Teste 1: Assegurar que não há sobreposição entre os dados de treino e validação

train_filenames = trainGen.filenames # Obtém os nomes dos arquivos para treino
val_filenames = ValGen.filenames # Obtém os nomes dos arquivos para validação

# retorna a interseção de elementos no grupo
overlap = set(train_filenames).intersection(set(val_filenames))

# Essa linha lança um erro (AssertionError) se houver qualquer imagem presente simultaneamente nos dois conjuntos.
# assert ... é uma instrução que testa uma condição; se a condição for falsa, o Python gera um erro com a mensagem especificada.
assert len(overlap) == 0, f"Atenção: {len(overlap)} imagens estão presentes tanto no treino quanto na validação."

# Resutado - OK

# ---------------------------------------------------------------------------------------

# Teste 2: Verificar o balanceamento

from collections import Counter

# Conta quantas imagens por classe no treino e validação
train_classes = trainGen.classes
val_classes = ValGen.classes
print("Treino:", Counter(train_classes))
print("Validação:", Counter(val_classes))

# Resutado - OK

# ---------------------------------------------------------------------------------------

# Teste 3: Verificar o total de imagens e a proporção da divisão

total_imgs = len(trainGen.filenames) + len(ValGen.filenames)
train_pct = len(trainGen.filenames) / total_imgs
val_pct = len(ValGen.filenames) / total_imgs
print(f"Proporção treino: {train_pct:.2%}, validação: {val_pct:.2%}")

# Resutado - OK

# ---------------------------------------------------------------------------------------

# Teste 4: Verificar se as imagens estão sendo carregadas no tamanho correto

# Essa linha pega o próximo batch (lote) de imagens e rótulos do train_generator.
# batch_x: contém as imagens, geralmente com shape (batch_size, height, width, channels)
# batch_y: contém os rótulos (labels) correspondentes, em formato one-hot, com shape (batch_size, num_classes).
batch_x, batch_y = next(trainGen)

# Retorna o formato do batch carregado
print(f"Tamanho do batch: {batch_x.shape}")
# Garante que o a altura e largura da imagem sejam os mesmos das especificações
# Verifica apenas os itens 1 e 2 da tupla de retorno ([1:3])
assert batch_x.shape[1:3] == (img_size, img_size), "As imagens não estão sendo redimensionadas corretamente."

# Resutado - OK

# ---------------------------------------------------------------------------------------

# Teste 5: Carregar 5 imagens aleatória para garantir que ela não esteja corrompida

import matplotlib.pyplot as plt

for i in range(5):
    image = batch_x[i]
    plt.imshow(image)
    plt.title(f"Classe: {batch_y[i].argmax()}")
    plt.axis('off')
    plt.show()

# Resutado - OK

# ---------------------------------------------------------------------------------------
# Os testes iniciais não indicaram problemas quanto ao carregamento dos dados
# ---------------------------------------------------------------------------------------

# TESTE PARA A EXTRAÇÃO DOS DADOS

# Teste 1: Extração de patches com uma imagem aleatória

from PatchExtractor import PatchExtractor
import tensorflow as tf

# Simula um batch de entrada com apenas uma imagem.
# contendo a mesma dimensão da base de dados
dummy_img = tf.random.uniform((1, 224, 224, 3))
# Define o tamanho dos patches
patch_size = 16
# Chama a classe PatchExtractor e obtém os patches da imagem dummy
extractor = PatchExtractor(patch_size)
patches = extractor(dummy_img)
# Exibe o shaape dos patches gerados
print("Shape dos patches:", patches.shape)  # Esperado: (1, 196, 768)
# Verifica a quantidade de patches gerado
assert patches.shape[1] == (224 // patch_size) ** 2, "Número de patches incorreto."
# Verifica a dimensão dos patches gerados
assert patches.shape[2] == patch_size * patch_size * 3, "Dimensão de cada patch incorreta."

# Resutado - OK
# OBS: A chamada de PatchExtractor em ModelCreator ocorre de maneira distinta, sendo:
#
# inputs = layers.Input(shape=self.input_shape)
# patches = PatchExtractor(self.patch_size)(inputs)
#
# layers.Input(shape=...) define a entrada simbólica do modelo no Keras (é um placeholder).
# A camada personalizada PatchExtractor(self.patch_size) é aplicada diretamente ao tensor inputs, 
# como se fosse uma função, graças à herança de tf.keras.layers.Layer.
# Esse comportamento é correto e esperado no Keras — ele cria um grafo 
# computacional simbólico que será avaliado durante o fit().

# “O modelo espera receber uma imagem com essa forma. 
# Ele ainda não sabe qual será a imagem real, mas sabe como ela será.”
# Essa filosofia permite que o modelo inteiro seja montado antes do treinamento.

# ---------------------------------------------------------------------------------------

# Teste 2: Verificar se os patches recebem o embedding corretamente e se o positional encoding é aplicado.

from PatchEncoder import PatchEncoder

num_patches = (224 // patch_size) ** 2 # Calcula a quantidade de patches extraídos
projection_dim = 512 # Define a dimensão do embedding

# Instancia a camada personalizada PatchEncoder
# num_patches é necessário para gerar a codificação posicional (com Embedding).
# projection_dim define o tamanho do vetor resultante para cada patch.
encoder = PatchEncoder(num_patches, projection_dim)
# Aplica o encoder sobre os patches.
# O encoder:
#   Aplica uma Dense para transformar cada vetor de patch em dimensão 512.
#   Soma a codificação posicional correspondente a cada índice de patch.
encoded = encoder(patches)

# Exibe o formato dos patches
print("Shape dos patches codificados:", encoded.shape)  # Esperado: (1, 196, 512)
# Confirma que a dimensão de saída está correta.
assert encoded.shape[-1] == projection_dim, "Embedding dimensional incorreto."

# ---------------------------------------------------------------------------------------
# Os testes iniciais não indicaram problemas quanto tratamento dos dados
# ---------------------------------------------------------------------------------------
'''
