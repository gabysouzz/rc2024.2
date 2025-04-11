"""
Servidor UDP/TCP para envio de arquivos.

Este servidor escuta por requisições UDP contendo o nome de um arquivo e o protocolo desejado.
Caso o protocolo seja TCP e o arquivo seja válido, o servidor responde com uma porta TCP para conexão.
Em seguida, envia o conteúdo do arquivo por uma conexão TCP.

Configurações de porta e arquivos são lidas a partir do arquivo config.ini.
"""

import configparser
import os
import socket
import threading

# Carrega o arquivo de configuração
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# Lê os parâmetros do servidor definidos em config.ini
tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

print(f"Servidor configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end} e UDP_PORT={udp_port}")

def handle_tcp_connection(porta: int, caminho_arquivo: str):
    """
    Estabelece uma conexão TCP na porta especificada e envia o conteúdo do arquivo.

    Args:
        porta (int): Porta TCP para escutar.
        caminho_arquivo (str): Caminho do arquivo a ser enviado.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_sock.bind(('', porta))
        tcp_sock.listen(1)
        print(f"[TCP] Escutando na porta {porta} para enviar {os.path.basename(caminho_arquivo)}")

        conn, addr = tcp_sock.accept()
        print(f"[TCP] Conexão recebida de {addr}")
        with conn:
            try:
                with open(caminho_arquivo, 'rb') as f:
                    conn.sendall(f.read())
                print(f"[TCP] Arquivo {os.path.basename(caminho_arquivo)} enviado para {addr}")
            except FileNotFoundError:
                erro_msg = f"[TCP] ERRO: Arquivo {caminho_arquivo} não encontrado!"
                print(erro_msg)
                conn.sendall(erro_msg.encode())

# Inicializa a próxima porta TCP disponível
proxima_porta_tcp = tcp_port_start

# Cria o socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', udp_port))
print(f"[UDP] Servidor escutando na porta {udp_port}")

# Loop principal do servidor
while True:
    dados, endereco = sock.recvfrom(1024)
    mensagem = dados.decode().strip()
    print(f"[UDP] Mensagem recebida de {endereco}: {mensagem}")

    try:
        nome_arquivo, protocolo = mensagem.split(",")

        if nome_arquivo == os.path.basename(file_a):
            caminho_do_arquivo = file_a
        elif nome_arquivo == os.path.basename(file_b):
            caminho_do_arquivo = file_b
        else:
            resposta = "ERRO: Arquivo não encontrado"
            sock.sendto(resposta.encode(), endereco)
            print(f"[UDP] Resposta enviada para {endereco}: {resposta}")
            continue
        
        # Valida o protocolo (apenas o TCP suportado)
        if protocolo.strip().upper() != "TCP":
            resposta = "ERRO: Apenas protocolo TCP é suportado nesta versão"
        
        # Verifica se há portas TCP que estão disponíveis
        elif proxima_porta_tcp > tcp_port_end:
            resposta = "ERRO: Nenhuma porta TCP disponível"
        
        else:
            resposta = str(proxima_porta_tcp)
            porta_tcp = proxima_porta_tcp
            proxima_porta_tcp += 1

            # Decide qual arquivo será enviado
            caminho_do_arquivo = file_a if nome_arquivo == os.path.basename(file_a) else file_b

            # Inicia a thread para envio com TCP
            threading.Thread(
                target=handle_tcp_connection,
                args=(porta_tcp, caminho_do_arquivo),
                daemon=True
            ).start()

    except Exception as e:
        resposta = f"Formato de mensagem inválido ({str(e)})"
    
    # Envia a resposta com UDP para o cliente
    sock.sendto(resposta.encode(), endereco)
    print(f"[UDP] Resposta enviada para {endereco}: {resposta}")
