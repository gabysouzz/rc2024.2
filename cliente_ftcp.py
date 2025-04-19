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
import time

# Carrega configurações
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Extrai dados do config.ini
tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

print(f"[CONFIG] Cliente configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end}, UDP_PORT={udp_port}")

# Entrada do usuário
name_file = input("Digite o nome do arquivo (a.txt ou b.txt): ").strip()

# Protocolo fixado como TCP
protocol = "TCP"
message = f"REQUEST {name_file} {protocol}"

# Negociação inicial via UDP
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.sendto(message.encode(), ('localhost', udp_port))
print(f"[UDP] Mensagem enviada: {message}")

# Recebe resposta do servidor
response, _ = udp_sock.recvfrom(1024)
response = response.decode().strip()

if response.startswith("ERRO"):
    print(f"[UDP] Erro: {response}")
else:
    if response.startswith("RESPONSE,TCP"):
        partes = response.split(',')
        if len(partes) == 4:
            tcp_port = int(partes[2])
        else:
            print("[UDP] Erro: Formato de resposta inválido.")
            udp_sock.close()
            exit(1)

    print(f"[UDP] Porta TCP recebida: {tcp_port}")

    time.sleep(0.5)  # Espera o servidor abrir a porta
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect(('localhost', tcp_port))
        print(f"[TCP] Conectado ao servidor na porta {tcp_port}")

        tcp_sock.sendall(f"GET {name_file}\r\n".encode())

        data = b""
        while True:
            piece = tcp_sock.recv(1024)
            if b"<<EOF>>" in piece:
                data += piece.replace(b"<<EOF>>", b"")
                break
            data += piece

        # Salva o arquivo
        with open(f"recebido_{name_file}", 'wb') as f:
            f.write(data)
        print(f"[TCP] Arquivo recebido e salvo como recebido_{name_file}")

        # Dá um tempo antes de enviar ACK (não fecha a conexão ainda!)
        time.sleep(0.2)

        # Envia ACK com número de bytes
        try:
            ack_message = f"FTCP_ACK,{len(data)}"
            tcp_sock.sendall(ack_message.encode())
            print(f"[TCP] {ack_message} enviado ao servidor.")
            time.sleep(0.5)  # Mantém conexão viva após ACK
        except Exception as e:
            print(f"[TCP] Erro ao enviar FTCP_ACK: {e}")