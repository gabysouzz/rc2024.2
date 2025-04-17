import configparser
import os
import socket
import threading

# Carrega o arquivo de configuração
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

print(f"Servidor configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end} e UDP_PORT={udp_port}")

def handle_tcp_connection(porta: int, caminho_arquivo: str):
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
                    data = f.read()
                    conn.sendall(data)
                    print(f"[TCP] Enviado {len(data)} bytes para {addr}")
                
                # Espera o ACK do cliente
                ack_data = conn.recv(1024).decode().strip()
                if ack_data.startswith("ACK,"):
                    ack_bytes = int(ack_data.split(",")[1])
                    if ack_bytes == len(data):
                        print(f"[TCP] ACK válido recebido de {addr}")
                    else:
                        print(f"[TCP] ERRO: ACK com bytes incorretos: {ack_bytes}")
                else:
                    print(f"[TCP] ERRO: ACK malformado recebido: {ack_data}")

            except FileNotFoundError:
                erro_msg = f"[TCP] ERRO: Arquivo {caminho_arquivo} não encontrado!"
                print(erro_msg)
                conn.sendall(erro_msg.encode())

proxima_porta_tcp = tcp_port_start
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', udp_port))
print(f"[UDP] Servidor escutando na porta {udp_port}")

while True:
    dados, endereco = sock.recvfrom(1024)
    mensagem = dados.decode().strip()
    print(f"[UDP] Mensagem recebida de {endereco}: {mensagem}")

    try:
        # Verifica se é um comando REQUEST,<arquivo>
        if not mensagem.startswith("REQUEST,"):
            resposta = "ERRO: Comando inválido. Use: REQUEST,<arquivo>"
            sock.sendto(resposta.encode(), endereco)
            continue

        partes = mensagem.split(",", 1)
        if len(partes) != 2:
            resposta = "ERRO: Formato incorreto. Use: REQUEST,<arquivo>"
            sock.sendto(resposta.encode(), endereco)
            continue

        nome_arquivo = partes[1].strip()

        if nome_arquivo == os.path.basename(file_a):
            caminho_do_arquivo = file_a
        elif nome_arquivo == os.path.basename(file_b):
            caminho_do_arquivo = file_b
        else:
            resposta = "ERRO: Arquivo não encontrado"
            sock.sendto(resposta.encode(), endereco)
            continue

        # Protocolo fixo: TCP
        if proxima_porta_tcp > tcp_port_end:
            resposta = "ERRO: Nenhuma porta TCP disponível"
        else:
            resposta = str(proxima_porta_tcp)
            porta_tcp = proxima_porta_tcp
            proxima_porta_tcp += 1

            threading.Thread(
                target=handle_tcp_connection,
                args=(porta_tcp, caminho_do_arquivo),
                daemon=True
            ).start()

    except Exception as e:
        resposta = f"Formato de mensagem inválido ({str(e)})"

    sock.sendto(resposta.encode(), endereco)
    print(f"[UDP] Resposta enviada para {endereco}: {resposta}")