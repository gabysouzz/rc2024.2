import configparser
import os
import socket

# Carrega configurações
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

# Exibe configuração
print(f"Cliente configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end} e UDP_PORT={udp_port}")

# Entrada do usuário
nome_arquivo = input("Digite o nome do arquivo (a.txt ou b.txt): ").strip()

# Protocolo fixo "TCP" (por enquanto)
protocolo = "TCP"
mensagem = f"{nome_arquivo},{protocolo}"

# Cria e envia UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(mensagem.encode(), ('localhost', udp_port))

# Aguarda resposta com a porta TCP
resposta, _ = sock.recvfrom(1024)
resposta = resposta.decode().strip()

if resposta.startswith("ERRO"):
    print(f"[UDP] Erro recebido: {resposta}")
else:
    porta_tcp = int(resposta)
    print(f"Cliente recebeu porta TCP para continuar a conexão: {porta_tcp}")

    # Conecta via TCP para baixar o arquivo
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sock:
        tcp_sock.connect(('localhost', porta_tcp))
        dados = b""
        while True:
            parte = tcp_sock.recv(1024)
            if not parte:
                break
            dados += parte

    # Salva o arquivo localmente
    with open(f"recebido_{nome_arquivo}", 'wb') as f:
        f.write(dados)
    print(f"[TCP] Arquivo {nome_arquivo} salvo como recebido_{nome_arquivo}")
