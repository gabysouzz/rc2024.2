# Relatório do Projeto: Protocolo de Transferência de Arquivos Personalizado – FTCP

Este relatório tem como objetivo demonstrar o entendimento dos protocolos de comunicação utilizados na implementação (camada de transporte, rede e camada 7), bem como a análise do tráfego gerado durante a transferência de arquivos. Os alunos deverão capturar o tráfego, analisar os pacotes com o Wireshark e refletir sobre aspectos como fragmentação de dados na camada de rede e a transferência de dados na camada de aplicação.

Cada grupo deve entregar um relatorio (*via classroom*) com 4 elementos;

1. [Introdução](#1-introdução)
2. [Descrição da Implementação](#2-descrição-da-implementação)
3. [Análise do Protocolo](#3-análise-do-protocolo)
4. [Discussão](#4-discussão)

## 1. Introdução

*   **Objetivo do Projeto:** Descreva brevemente o objetivo principal do projeto, que foi desenvolver um cliente e um servidor para transferência de arquivos utilizando o protocolo FTCP, conforme especificado.
*   **Motivação:** (Opcional) Comente brevemente sobre a importância de entender protocolos de rede e a diferença entre TCP e UDP no contexto da transferência de arquivos.
*   **Estrutura do Relatório:** Apresente um resumo das seções que compõem este relatório.

## 2. Descrição da Implementação

Descrição breve (não pode execeder uma pagina) dos itens abaixo:

*   **Arquivo de Configuração (`config.ini`):** Apresente o conteúdo do arquivo `config.ini` utilizado nos seus testes.
*   **Arquivos de Teste (`a.txt`, `b.txt`):** Descreva brevemente o conteúdo dos arquivos `a.txt` e `b.txt` utilizados.

## 3. Análise do Protocolo

Esta seção é crucial e deve demonstrar o funcionamento do protocolo FTCP nas camadas de transporte e aplicação, utilizando capturas de tela do Wireshark.

**Instruções:**
*   Execute o servidor e o cliente.
*   Inicie uma captura no Wireshark (na interface de loopback `lo` ou `localhost` se cliente e servidor estiverem na mesma máquina, ou na interface de rede apropriada se em máquinas diferentes).
*   Realize uma transferência de arquivo bem-sucedida, para os arquivos `a.txt` e `b.txt`usando TCP.
*   (Opcional) Tente realizar uma solicitação inválida (e.g., pedir protocolo UDP) para capturar a mensagem de erro.
*   Pare a captura e utilize filtros no Wireshark para isolar os pacotes relevantes (ex: `udp.port == <UDP_PORT>`, `tcp.port == <TCP_PORT>`, ou filtre pelo IP do cliente/servidor).
    *   **Para mais informações de como utilizar o wireshark consulte o [link](./wireshark_tutorial.md)**

* Escrita do relatorio:
  * Utilize as capturas de telas
  *   **Para cada captura de tela, adicione anotações (círculos, setas, texto) destacando os pontos importantes.**

### 3.1. Etapa 1: Negociação Inicial via UDP

Demonstrar a troca de mensagens UDP entre cliente e servidor para negociar a porta e o protocolo de transferência.
*   **Captura e Análise:**
    *   **Pacote de Requisição (Cliente -> Servidor):**
        *   Inclua uma captura de tela do pacote UDP enviado pelo cliente.
        *   **Camada de Transporte (UDP):** Destaque as portas de origem (efêmera do cliente) e destino (porta `UDP_PORT` do servidor, conforme `config.ini`). Mencione que é um datagrama sem conexão prévia.
        *   **Camada de Aplicação (FTCP sobre UDP):** Destaque o *payload* do datagrama UDP, mostrando a mensagem `REQUEST,TCP,a.txt` (ou `b.txt`). Confirme que a codificação (e.g., UTF-8) está correta.
    *   **Pacote de Resposta (Servidor -> Cliente):**
        *   Inclua uma captura de tela do pacote UDP de resposta do servidor.
        *   **Camada de Transporte (UDP):** Destaque as portas de origem (`UDP_PORT` do servidor) e destino (porta temporaria do cliente, a mesma da qual ele enviou a requisição).
        *   **Camada de Aplicação (FTCP sobre UDP):** Destaque o *payload*, mostrando a mensagem `RESPONSE,TCP,<TCP_PORT>,<ARQUIVO>` (substitua pelos valores reais). Confirme que a porta TCP informada corresponde à `TCP_PORT` do `config.ini`.
    *   **(Opcional) Pacote de Erro (Servidor -> Cliente):**
        *   Se capturou uma tentativa inválida, inclua a captura de tela.
        *   **Camada de Aplicação (FTCP sobre UDP):** Destaque o *payload* mostrando a mensagem de erro, como `ERROR,PROTOCOLO INVALIDO,,`.

### 3.2. Etapa 2: Transferência de Dados via TCP

Demonstrar o estabelecimento da conexão TCP, a troca de comandos da aplicação FTCP e a transferência confiável do arquivo.

*   **Captura e Análise:**
    *   **Estabelecimento da Conexão (Three-Way Handshake):**
        *   Inclua uma captura de tela mostrando os pacotes SYN, SYN-ACK e ACK.
        *   **Camada de Transporte (TCP):** Destaque as flags (SYN, ACK), os números de sequência/confirmação iniciais e as portas de origem (efêmera do cliente) e destino (`TCP_PORT` do servidor, informada na Etapa 1). Explique como isso estabelece uma conexão confiável.
    *   **Solicitação do Arquivo (Cliente -> Servidor):**
        *   Inclua uma captura de tela do pacote TCP contendo o comando `get`.
        *   **Camada de Aplicação (FTCP sobre TCP):** Destaque o *payload* do segmento TCP, mostrando o comando `get,<ARQUIVO>`.
        *   **Camada de Transporte (TCP):** Note como o TCP encapsula os dados da aplicação.
    *   **Transferência dos Dados do Arquivo (Servidor -> Cliente):**
        *   Inclua capturas de tela de *alguns* segmentos TCP que transportam o conteúdo do arquivo. Não precisa de todos, mas mostre o início, meio ou fim.
        *   **Camada de Aplicação (FTCP sobre TCP):** Mostre que o *payload* desses segmentos contém partes do arquivo (`a.txt` ou `b.txt`).
        *   **Camada de Transporte (TCP):** Destaque os números de sequência crescentes nos pacotes do servidor e os números de confirmação (ACK) correspondentes enviados pelo cliente (podem estar em pacotes separados ou junto com dados do cliente, se houvesse). Explique como isso garante a entrega ordenada e confiável.
    *   **Confirmação de Recebimento (Cliente -> Servidor):**
        *   Inclua uma captura de tela do pacote TCP contendo o comando `ftcp_ack`.
        *   **Camada de Aplicação (FTCP sobre TCP):** Destaque o *payload* mostrando `ftcp_ack,<numero_de_bytes>`. Verifique se o número de bytes corresponde ao tamanho do arquivo transferido.
        *   **Camada de Transporte (TCP):** Mostre como este comando final da aplicação também é transportado via TCP.
    *   **Encerramento da Conexão:**
        *   Inclua uma captura de tela mostrando a troca de pacotes com flags FIN e ACK.
        *   **Camada de Transporte (TCP):** Explique brevemente como os pacotes FIN/ACK são usados para encerrar a conexão de forma ordenada por ambos os lados.

## 4. Discussão

*   **Desafios Encontrados:** Quais foram as maiores dificuldades durante a implementação? (Ex: lidar com sockets, threads, codificação, depuração do protocolo).
*   **Decisões de Projeto:** Houve alguma decisão de implementação importante que você tomou e gostaria de justificar?
*   **Possíveis Melhorias:** O que poderia ser melhorado ou adicionado ao protocolo FTCP ou à sua implementação? (Ex: Suporte real a UDP para transferência, criptografia, janelas deslizantes mais complexas, tratamento de erros mais robusto).


