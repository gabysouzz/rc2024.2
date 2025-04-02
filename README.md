# Projeto: Protocolo de Transferência de Arquivos Personalizado – FTCP

Este repositório contém a implementação do projeto **FTCP (File Transfer Custom Protocol)**, um sistema cliente-servidor para transferência de arquivos utilizando os protocolos TCP e UDP de forma customizada, conforme especificado nas instruções.

## Equipe

*   **Integrante 1:** Aline Brito Maracajá
*   **Integrante 2:** Daniele de Oliveira
*   **Integrante 3:** Gabrielly de Souza Lima
*   **Integrante 3:** Maria Clara Oliveira Guedes

*   *(Adicione mais linhas conforme necessário)*

## Visão Geral do Projeto

O objetivo principal é desenvolver um cliente e um servidor que se comunicam através de um protocolo próprio (FTCP). A negociação inicial ocorre via UDP, onde o cliente requisita um arquivo (`a.txt` ou `b.txt`) e especifica o protocolo de transferência (obrigatoriamente TCP nesta versão). O servidor responde com a porta TCP designada para a transferência. Em seguida, o cliente estabelece uma conexão TCP nessa porta, solicita o arquivo, o recebe e confirma o recebimento antes de encerrar a conexão.

## Entregáveis

A entrega final do projeto consiste nos itens detalhados na tabela abaixo. Certifique-se de que todos os itens listados para o repositório Git estejam presentes e atualizados na branch principal (`main` ou `master`) antes da data final.

| Item # | Descrição                                      | Forma de Entrega                  |
| :----- | :--------------------------------------------- | :-------------------------------- |
| 1      | **Código Fonte** (Cliente e Servidor)          | Repositório Git (este)            |
| 2      | **Arquivos de Teste** (`a.txt` e `b.txt`)      | Repositório Git (este)            |
| 3      | **Arquivo de Configuração** (`config.ini`)     | Repositório Git (este)            |
| 4      | **Arquivo de Captura de Tráfego** (`.pcapng`) | Repositório Git (este)            |
| 5      | **Relatório de Análise** (PDF ou Markdown)   | Google Classroom (1 por equipe)   |


## Documentação Importante

Consulte os seguintes arquivos neste repositório para obter detalhes completos sobre cada parte do projeto:

*   **[📄 Especificação do Protocolo FTCP](./protocolo.md):** Descreve em detalhes as etapas de negociação (UDP) e transferência (TCP), os formatos das mensagens e o fluxo de comunicação esperado entre cliente e servidor.
*   **[🦈 Tutorial de Análise com Wireshark](./wireshark_tutorial.md):** Contém um guia passo a passo sobre como usar o Wireshark para analisar o arquivo de captura (`.pcap`), incluindo exemplos com DHCP/DNS e instruções específicas para analisar o tráfego do seu protocolo FTCP.
*   **[📝 Instruções para o Relatório](./relatorio.md):** Apresenta a estrutura e o conteúdo esperado para o relatório final, focando na análise do protocolo e do tráfego de rede capturado.
*   **[🐍 Exemplo de servidor/cliente (Python)](./echo_server.py):** Um código de exemplo em Python demonstrando um servidor e cliente "echo" que opera simultaneamente em TCP e UDP. 

## Como Executar (Exemplo Básico)

1.  **Configuração:** Certifique-se de que o arquivo `config.ini` está presente na mesma pasta dos scripts e configurado corretamente com as portas desejadas e os caminhos para os arquivos `a.txt` e `b.txt`.
2.  **Iniciar o Servidor:**
    
    ```bash
    python servidor_ftcp.py
    ```
3.  **Executar o Cliente (em outro terminal):**
    ```bash
    python cliente_ftcp.py a.txt
    ```
