import configparser
import os

# aqui ta carregando o config.ini que eu fiz
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

# ta lendo os valores do [SERVER] em config.ini
tcp_port_start = int(config['SERVER']['TCP_PORT_START'])
tcp_port_end = int(config['SERVER']['TCP_PORT_END'])
udp_port = int(config['SERVER']['UDP_PORT'])
file_a = config['SERVER']['FILE_A']
file_b = config['SERVER']['FILE_B']

# print qualquer so pra mostrar que recebeu a config
print(f"Servidor configurado com TCP_PORT_START={tcp_port_start}, TCP_PORT_END={tcp_port_end} e UDP_PORT={udp_port}")