import socket
import threading

def udp_echo():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(('0.0.0.0', 5698))
    print("UDP server listening on port 5698")
    while True:
        data, addr = udp_sock.recvfrom(1024)
        if not data:
            continue
        print(f"UDP Received from {addr}: {data.decode('utf-8')}")
        # Echo back the received data
        udp_sock.sendto(data, addr)

def handle_tcp_client(conn, addr):
    print(f"TCP Client connected from {addr}")
    with conn:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print(f"TCP Received from {addr}: {data.decode('utf-8')}")
            # Echo back the data
            conn.sendall(data)
    print(f"TCP Client disconnected from {addr}")

def tcp_echo():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('0.0.0.0', 6000))
    tcp_sock.listen(5)
    print("TCP server listening on port 6000")
    while True:
        conn, addr = tcp_sock.accept()
        client_thread = threading.Thread(target=handle_tcp_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()

if __name__ == '__main__':
    # Iniciar thread para UDP
    udp_thread = threading.Thread(target=udp_echo)
    udp_thread.daemon = True
    udp_thread.start()

    # Iniciar thread para TCP
    tcp_thread = threading.Thread(target=tcp_echo)
    tcp_thread.daemon = True
    tcp_thread.start()

    print("Servidor rodando. Pressione Ctrl+C para encerrar.")

    try:
        # Mantém o programa principal em execução
        while True:
            pass
    except KeyboardInterrupt:
        print("Servidor encerrado.")
