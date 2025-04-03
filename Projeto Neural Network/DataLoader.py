from keras.src.legacy.preprocessing.image import ImageDataGenerator


class DataLoader:

    def __init__(self, dataset_path, img_size=(128, 128), batch_size=32, val_split=0.3):
        """
        Classe responsável pelo carregamento do dataset.
        parametro dataset_path: Caminho para a pasta que contém as imagens organizadas por classe.
        parametro img_size: Dimensão das imagens (padrão: 128x128).
        parametro batch_size: Tamanho do batch para treinamento.
        parametro val_split: Porcentagem das imagens usadas para validação.
        """

        self.dataset_path = dataset_path
        self.img_size = img_size
        self.batch_size = batch_size
        self.val_split = val_split
        self.train_generator = None
        self.val_generator = None

        self.load_data()

    def load_data(self):
        """
        O ImageDataGenerator é uma classe do Keras (tensorflow.keras.preprocessing.image) que facilita o
        pré-processamento de imagens para redes neurais. Ele permite carregar imagens de um diretório e aplicar
        transformações como normalização, rotação, espelhamento, aumento de dados (data augmentation), entre outras

        obs: A divisão entre treino e validação não é aleatória por padrão no ImageDataGenerator quando
        usamos o parâmetro validation_split. A separação é feita de forma ordenada, baseada na ordem
        dos arquivos dentro das pastas.
        """

        # Instância de uma objeto do ImageDataGenerator, definindo como parâmetros operações para o pré processamento
        datagen = ImageDataGenerator(
            rescale=1.0 / 255,  # Normalização do valor dos pixels das imagens (Faixa de 0 à 1)
            validation_split=self.val_split  # Define a divisão dos dados (imagens )entre treino e validação
        )

        """
        O flow_from_directory do ImageDataGenerator é utilizado para carregar automaticamente as imagens de um 
        diretório organizado em subpastas, onde cada subpasta representa uma classe. Além disso, são aplicadas 
        as transformações definidas no momento da instância (como normalização) e as prepara em batches para 
        serem usadas no treinamento da CNN.
        """
        # Define a geração do grupo de treinamento, utilizando a instância do ImageData generator
        self.train_generator = datagen.flow_from_directory(

            self.dataset_path,  # Indica o caminho do diretório onde estão armazenadas as imagens
            target_size=self.img_size,  # Redimensiona o tamanho das imagens que serão carregadas na CNN
            batch_size=self.batch_size,  # Define o número de imagens por lote que será carregado em cada iteração
            class_mode='categorical',  # Define as classes. 'categorical' indica que as saídas serão vetores one-hot.
            subset='training'  # Aqui indicamos se queremos carregar os dados definidos em validation_split
            # obs: Os dados definidos em validation_split podem ser descritos po 'training' ou 'validation'
        )

        # Define a geração do grupo de treinamento, utilizando a instância do ImageData generator
        self.val_generator = datagen.flow_from_directory(

            self.dataset_path,  # Indica o caminho do diretório onde estão armazenadas as imagens
            target_size=self.img_size,  # Redimensiona o tamanho das imagens que serão carregadas na CNN
            batch_size=self.batch_size,  # Define o número de imagens por lote que será carregado em cada iteração
            class_mode='categorical',   # Define as classes. 'categorical' indica que as saídas serão vetores one-hot.
            subset='validation'  # Aqui indicamos se queremos carregar os dados definidos em validation_split
        )

        # Log das classes
        print("Classes identificadas:", self.train_generator.class_indices)
