import socket
import time
import sys
import os
import threading

class RegistryServer:
    def __init__(self, host='127.0.0.1', port=65430):
        self.host = host
        self.port = port
        self.available_servers = []
        self.lock = threading.Lock()  # For thread-safe list operations

    def handle_server_connection(self, conn, addr):
        """Handle incoming server connections and maintain availability"""
        try:
            # Receive server's port number
            size = conn.recv(4)
            s1 = int.from_bytes(size, 'big')
            server_port = conn.recv(s1)
            server_port = int(server_port.decode())
            
            # Add server to available servers list
            server_info = (addr[0], server_port)
            with self.lock:
                if server_info not in self.available_servers:
                    self.available_servers.append(server_info)
                    print(f"Server registered: {addr[0]}:{server_port}")
                    print("Available servers:", self.available_servers)

            # Keep connection open to monitor server availability
            while True:
                # Simple heartbeat check
                try:
                    conn.send(b'ping')
                    response = conn.recv(4)
                    if not response:
                        raise ConnectionError
                    time.sleep(1)
                except:
                    break

        except Exception as e:
            print(f"Error handling server connection: {e}")
        finally:
            # Remove server from available list when connection breaks
            with self.lock:
                if server_info in self.available_servers:
                    self.available_servers.remove(server_info)
                    print(f"Server removed: {addr[0]}:{server_port}")
                    print("Available servers:", self.available_servers)
            conn.close()

    def handle_client_connection(self, conn, addr):
        """Handle client connections and send available server list"""
        try:
            # Send number of available servers
            with self.lock:
                num_servers = len(self.available_servers)
                conn.sendall(num_servers.to_bytes(4, 'big'))

                # Send each server's information
                for server_host, server_port in self.available_servers:
                    # Send host
                    host_data = server_host.encode()
                    size = len(host_data)
                    conn.sendall(size.to_bytes(4, 'big'))
                    conn.sendall(host_data)
                    
                    # Send port
                    conn.sendall(server_port.to_bytes(4, 'big'))

        except Exception as e:
            print(f"Error handling client connection: {e}")
        finally:
            conn.close()

    def start(self):
        """Start the registry server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            print(f"Registry server started on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                print(f"New connection from {addr}")

                # First byte indicates connection type (1 for server, 2 for client)
                conn_type = conn.recv(1)
                
                if conn_type == b'1':
                    # Server connection
                    thread = threading.Thread(
                        target=self.handle_server_connection,
                        args=(conn, addr)
                    )
                else:
                    # Client connection
                    thread = threading.Thread(
                        target=self.handle_client_connection,
                        args=(conn, addr)
                    )
                
                thread.daemon = True
                thread.start()

if __name__ == "__main__":
    registry = RegistryServer()
    try:
        registry.start()
    except KeyboardInterrupt:
        print("\nRegistry server shutting down...")
        sys.exit(0)