"""
Cliente UDP/TCP para transferência de arquivos.

Este código implementa um cliente responsável por solicitar um arquivo a um servidor. 
Inicialmente, ele se comunica com o servidor utilizando o protocolo UDP, enviando uma 
mensagem que contém o nome do arquivo desejado e o protocolo a ser utilizado para transferência 
(fixado como TCP). Após receber do servidor a indicação de uma porta TCP disponível, o cliente 
estabelece uma conexão TCP com essa porta. Por meio dessa conexão, ele recebe o conteúdo do arquivo 
solicitado e o armazena localmente. 
"""


import os
import socket
import configparser


#Configuraçoes iniciais
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

#Extrai os dados do config.ini
tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

print(f"[CONFIG] Cliente configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end}, UDP_PORT={udp_port}")

# Entrada do usuário
name_file = input("Digite o nome do arquivo (a.txt ou b.txt): ").strip()

# Fixa o protocolo: TCP
protocol = "TCP"
message = f"{name_file},{protocol}"

# Negociação inicial via UDP
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.sendto(message.encode(), ('localhost', udp_port))
print(f"[UDP] Mensagem enviada: {message}")

# Recebe a porta TCP do servidor como resposta
response, _ = udp_sock.recvfrom(1024)
response = response.decode().strip()

if response.startswith("ERRO"):
    print(f"[UDP] Erro: {response}")
else:
    tcp_port = int(response)
    print(f"[UDP] Porta TCP recebida: {tcp_port}")

    # Estabelece conexão TCP para baixar o arquivo
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect(('localhost', tcp_port))
        print(f"[TCP] Conectado ao servidor na porta {tcp_port}")

        dados = b""
        while True:
            piece = tcp_sock.recv(1024)
            if not piece:
                break
            data += piece

    # Salva o arquivo de forma local
    name_file_local = f"recebido_{name_file}"
    with open(name_file_local, 'wb') as f:
        f.write(data)

    print(f"[TCP] Arquivo recebido e salvo como {name_file_local}")
