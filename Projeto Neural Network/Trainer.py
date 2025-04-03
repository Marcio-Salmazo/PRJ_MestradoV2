import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.callbacks import TensorBoard
import os


class Trainer:

    def __init__(self, model, train_data, val_data, epochs=20):
        """
        Classe responsável por gerenciar o treinamento do modelo, o que envolve a compilação e as métricas
        parametro model: Modelo CNN criado.
        parametro train_data: Dados de treinamento.
        parametro val_data: Dados de validação.
        parametro epochs: Número de épocas para o treinamento.
        """
        self.model = model
        self.train_data = train_data
        self.val_data = val_data
        self.epochs = epochs
        self.history = None

    def compile_and_train(self, logName):
        """
        Função responsável por compilar o modelo e dar inicio ao treinamento
        O método .compile() define as configurações do modelo antes do treinamento.
            * optimizer='adam' → O Adam (Adaptive Moment Estimation) é um otimizador que
              ajusta os pesos da rede durante o treinamento de maneira eficiente.
            * loss='categorical_crossentropy' → Essa é a função de erro usada para
              problemas de classificação multiclasse.
            * metrics=['accuracy'] → Define que a acurácia será monitorada durante o treinamento.
        """
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )

        """
        O método .fit() inicia o treinamento do modelo.
            * self.train_data → Conjunto de imagens usadas para o treinamento.
            * epochs=self.epochs → Número total de vezes que o modelo verá todos os dados de treinamento. 
              Mais épocas podem melhorar o aprendizado, mas também podem causar overfitting.
            * validation_data=self.val_data → Conjunto de validação para avaliar 
              o desempenho do modelo durante o treinamento.
        """

        # Criar o diretório "logs/fit/" caso não exista
        log_dir = "logs/fit/"
        os.makedirs(log_dir, exist_ok=True)  # Garante que o diretório existe

        # Criar um subdiretório único para cada execução
        run_id = logName + '_run_' + str(len(os.listdir(log_dir)) + 1)
        log_dir = os.path.join(log_dir, run_id)

        # Definir o callback do TensorBoard
        tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

        self.history = self.model.fit(
            self.train_data,
            epochs=self.epochs,
            validation_data=self.val_data,
            callbacks=[tensorboard_callback]
        )

        # obs:  O resultado do treinamento é armazenado em self.history,
        # que contém os valores da acurácia e da perda ao longo das épocas.
    '''
    def plot_metrics(self):
        """
        Essa função gera gráficos para visualizar o desempenho do treinamento.
        """
        plt.figure(figsize=(12, 5))  # Cria uma nova figura para os gráficos, com tamanho 12x5 polegadas.

        # Plotando Acurácia
        plt.subplot(1, 2, 1)
        plt.plot(self.history.history['accuracy'], label='Treino')
        plt.plot(self.history.history['val_accuracy'], label='Validação')
        plt.xlabel('Épocas')
        plt.ylabel('Acurácia')
        plt.legend()

        # Plotando Perda
        plt.subplot(1, 2, 2)
        plt.plot(self.history.history['loss'], label='Treino')
        plt.plot(self.history.history['val_loss'], label='Validação')
        plt.xlabel('Épocas')
        plt.ylabel('Perda')
        plt.legend()

        plt.show()
    '''
