Detecção de Dor em Camundongos com Redes Neurais Convolucionais
Este repositório contém um projeto voltado para a detecção de dor em camundongos, utilizando redes neurais convolucionais (CNNs) para a extração e análise de padrões visuais. O objetivo é desenvolver um modelo capaz de identificar sinais indicativos de dor a partir de imagens extraídas de vídeos.

### Metodologia
Este trabalho tem como principal objetivo conduzir uma investigação aprofundada sobre a viabilidade e a eficiência da aplicação de técnicas avançadas de aprendizado de máquina para a detecção de dor em camundongos. Especificamente, busca-se avaliar a capacidade das Redes Neurais Convolucionais (CNNs) em identificar padrões morfológicos e comportamentais que possam indicar estados de desconforto ou sofrimento nos animais.

A metodologia empregada baseia-se na exploração de diferentes arquiteturas de CNNs, visando determinar a mais eficaz na captura e caracterização de atributos visuais correlacionados à expressão de dor. Para isso, é realizada uma análise detalhada de imagens digitais da face dos camundongos, utilizando como referência a Rat Grimace Scale (RGS), um método amplamente reconhecido na literatura para a avaliação da expressão facial relacionada à dor em roedores.

Os principais atributos faciais considerados na análise incluem:
✅ Região ocular: alterações no fechamento ou na forma dos olhos podem indicar estados dolorosos;

✅ Posicionamento e formato das orelhas: mudanças na orientação ou na posição podem estar associadas a estados de dor;

✅ Configuração da boca e do focinho: padrões específicos na contração muscular nessas regiões podem ser indicativos de dor.

Para viabilizar a análise, o projeto inclui o desenvolvimento de uma ferramenta de processamento de vídeos capaz de extrair frames específicos, possibilitando a construção de um ground truth confiável para o treinamento da rede neural.

### Tópicos Abordados
✅ Fundamentos do processamento digital de imagens

✅ Leitura, Escrita e Manipulação de dados

✅ Fundamentos sobre redes neurais e aprendizado de máquina

✅ Processos do veterinário, voltados aos estudos com camundongos

✅ Técnicas para extração de dados relevantes

### Estrutura do Repositório
O repositório está organizado da seguinte forma:

/

├── Projeto Neural Network/

├── Projeto Video Player/

├── Videos/

├── VideoPlayer1F - Copia

└── VideoPlayer1F

Sendo:

✅ Projeto Neural Network - Contém as arquiteturas de rede nueral implementadas em python para o projeto

✅ Projeto Video Player - Contém a ferramenta de extração de frames para a construção de um dataset de ground-truth (a partir de um arquivo de vídeo)

✅ Videos - Contém vídeos para teste da ferramenta de extração de frames

✅ VideoPlayer1F - Copia - Implementação inicial da ferramenta de extração de frames, utilizando o jupyter notebook

✅ VideoPlayer1F - Implementação inicial da ferramenta de extração de frames, utilizando o jupyter notebook

FUNCIONAMENTO DA FERRAMENTA DE EXTRAÇÃO DE FRAMES:
