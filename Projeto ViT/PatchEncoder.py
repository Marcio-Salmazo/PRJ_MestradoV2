import tensorflow as tf
from tensorflow.keras import layers


# A classe é responsável por Projetar cada patch em um vetor d-dimensional (embedding),
# bem como Adicionar a codificação posicional a cada patch, para preservar a ordem
# espacial da imagem (já que transformers não a consideram por padrão).

# Importante salientar que a classe herda devtf.keras.layers.Layer, com isso,
# ela podese comporte como qualquer outra camada (ex: Dense, Conv2D, etc).
# Ela vai transformar a sequência de patches extraídos da imagem.
class PatchEncoder(layers.Layer):

    # Contrutor da classe
    # obs: número total de patches por imagem (ex: 14×14 = 196)
    # obs2: dimensão do vetor em que cada patch será projetado (embedding size)
    def __init__(self, num_patches, projection_dim):
        # Inicializa corretamente a superclasse Layer, garantindo que a camada
        # funcione dentro do ecossistema Keras (com suporte a treinamento, salvamento, etc).
        super(PatchEncoder, self).__init__()

        # Armazena o número de patches como atributo da instância para uso posterior.
        self.num_patches = num_patches

        # Define uma camada Dense (fully connected) que será aplicada a cada patch individualmente.
        # Ela vai transformar o vetor bruto do patch (por exemplo, 768 valores de pixels) em um vetor
        # d-dimensional (ex: 512), que representa melhor o conteúdo do patch.
        self.projection = layers.Dense(units=projection_dim)

        # Cria uma tabela de embeddings (como em NLP), onde cada posição (de 0 a num_patches - 1)
        # tem um vetor associado. Essa camada vai gerar os vetores de codificação posicional, logo,
        # ao patch 0 associamos o vetor pos_encoding[0], ao patch 1 o pos_encoding[1], etc.
        self.position_embedding = layers.Embedding(
            input_dim=num_patches, output_dim=projection_dim
        )

    # O metodo call define o que a camada faz quando ela é chamada durante o modelo
    # É necessário compreender que a classe está sendo usada como se fosse uma função chamável.
    # Em Python, isso é chamado de overloading do operador (), e é habilitado por meio do
    # No Keras, __call__ é implementado na superclasse Layer, e ele chama internamente
    # o call(...) que foi definido abaixo define.

    # obs: Toda camada personalizada que herda de tf.keras.layers.Layer deve:
    #   1 - Definir a lógica de computação no call(...)
    #   2 - Usar o __init__ apenas para armazenar hiperparâmetros e instanciar subcamadas

    # obs2: Aqui, patches é um tensor de shape: (batch_size, num_patches, patch_dims)
    def call(self, patches):
        # Gera um tensor com os índices dos patches:[0, 1, 2, ..., num_patches-1]
        # servindo para buscar os embeddings de posição na linha seguinte.
        positions = tf.range(start=0, limit=self.num_patches, delta=1)

        # Essa linha é o coração da camada, responsável por gerar o vetor final que
        # representa o patch com conteúdo + posição.
        #
        # Operação desta linha:
        #
        # Em self.projection(patches) cada vetor de patch (ex: 768) é transformado em um vetor
        # projection_dim (ex: 512). Como resultado temos shape: (batch_size, num_patches, projection_dim).
        #
        # Em self.position_embedding(positions) um vetor de posição para cada índice é produzido
        # (0 a 195, por exemplo). shape: (num_patches, projection_dim)
        #
        # A soma entre a projeção do conteúdo de cada patch ea codificação de sua posição
        # gera o vetor final que representa o patch com conteúdo + posição.
        encoded = self.projection(patches) + self.position_embedding(positions)

        # Retorna a sequência de vetores com conteúdo e posição embutida
        return encoded
