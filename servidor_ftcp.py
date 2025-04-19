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

def handle_tcp_connection(porta_tcp, caminho_arquivo):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.bind(('localhost', porta_tcp))
        tcp_sock.listen(1)
        print(f"[TCP] Escutando na porta {porta_tcp} para enviar {os.path.basename(caminho_arquivo)}")

        conn, endereco = tcp_sock.accept()

        comando = conn.recv(1024).decode().strip()
        if comando.startswith("GET"):
            arquivo_solicitado = comando.split()[1]
            if arquivo_solicitado != os.path.basename(caminho_arquivo): 
                conn.sendall(b"ERRO: Arquivo solicitado nao corresponde")
                return

            with conn:
                print(f"[TCP] Conexão recebida de {endereco}")

                # Envia o arquivo
                with open(caminho_arquivo, 'rb') as f:
                    while True:
                        dados = f.read(1024)
                        if not dados:
                            break
                        conn.sendall(dados)
                # Aqui: marca de fim de transmissão
                conn.sendall(b"<<EOF>>")
                
                print(f"[TCP] Arquivo {os.path.basename(caminho_arquivo)} enviado para {endereco}")

                # Espera pelo ACK com timeout
                conn.settimeout(5.0)
                try:
                    ack = conn.recv(1024)
                    if ack:
                        ack_decodificado = ack.decode().strip()
                        if ack_decodificado.startswith("FTCP_ACK"):
                            partes = ack_decodificado.split(',')
                            if len(partes) == 2:
                                try:
                                    num_bytes = int(partes[1])
                                    print(f"[TCP] FTCP_ACK recebido de {endereco} com {num_bytes} bytes confirmados.")
                                except ValueError:
                                    print(f"[TCP] FTCP_ACK recebido de {endereco}, mas número inválido: {partes[1]}")
                            elif ack_decodificado == "FTCP_ACK":
                                print(f"[TCP] FTCP_ACK simples recebido de {endereco}")
                            else:
                                print(f"[TCP] Formato inesperado no ACK de {endereco}: {ack_decodificado}")
                        else:
                            print(f"[TCP] ACK inválido de {endereco}: {ack_decodificado}")
                except socket.timeout:
                    print(f"[TCP] Nenhum ACK recebido de {endereco} (timeout)")
                finally:
                    conn.close()

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
        mensagem = mensagem.strip()
        partes = mensagem.split()
        if len(partes) != 3 or partes[0].upper() != "REQUEST":
            resposta = "ERRO, Formato de requisição inválido. Use: REQUEST <arquivo> <protocolo>"
            sock.sendto(resposta.encode(), endereco)
            continue

        _, nome_arquivo, protocolo = partes

        if nome_arquivo == os.path.basename(file_a):
            caminho_do_arquivo = file_a
        elif nome_arquivo == os.path.basename(file_b):
            caminho_do_arquivo = file_b
        else:
            resposta = "ERRO, Arquivo não encontrado"
            sock.sendto(resposta.encode(), endereco)
            print(f"[UDP] Resposta enviada para {endereco}: {resposta}")
            continue

        if protocolo.strip().upper() != "TCP":
            resposta = "ERRO, Apenas protocolo TCP é suportado nesta versão"

        elif proxima_porta_tcp > tcp_port_end:
            resposta = "ERRO, Nenhuma porta TCP disponível"

        else:
            resposta = str(proxima_porta_tcp)
            porta_tcp = proxima_porta_tcp

            # Inicia a thread para envio com TCP
            threading.Thread(
                target=handle_tcp_connection,
                args=(porta_tcp, caminho_do_arquivo),
                daemon=True
            ).start()
            resposta = f"RESPONSE,TCP,{proxima_porta_tcp},{nome_arquivo}"
            proxima_porta_tcp += 1

    except Exception as e:
        resposta = f"ERRO, Formato de mensagem inválido ({str(e)})"

    sock.sendto(resposta.encode(), endereco)
    print(f"[UDP] Resposta enviada para {endereco}: {resposta}")