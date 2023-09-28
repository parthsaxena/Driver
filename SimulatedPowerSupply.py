import socket
import threading

class SimulatedPowerSupply:

    def __init__(self):
        self.voltage = 0.0
        self.current = 0.0
        self.output_enabled = False

    def handle_scpi_command(self, command):        
        if command == 'MEAS:VOLT?':            
            return str(self.voltage)
        elif command == 'MEAS:CURR?':
            return str(self.current)
        elif command.startswith('SOUR:VOLT '):
            self.voltage = float(command.split(' ')[1])
            return 'OK'
        elif command.startswith('SOUR:CURR '):
            self.current = float(command.split(' ')[1])
            return 'OK'
        elif command == 'OUTP ON':
            self.output_enabled = True
            return 'OK'
        elif command == 'OUTP OFF':
            self.output_enabled = False
            return 'OK'
        else:
            return 'ERR'
        
    def handle_client(self, conn, addr):
        print(f'Connected by {addr}')

        try:
            while True:
                command = conn.recv(1024).decode().strip()
                if not command:
                    break
                
                # Get response and add newline char
                response = self.handle_scpi_command(command)                                        
                conn.sendall(response.encode() + b'\n')
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f'Client {addr} disconnected: {e}')
        finally:
            conn.close()
        
    def run(self, host='0.0.0.0', port=5025):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            s.listen()

            print(f'Simulated Power Supply listening on {host}:{port}')            
            
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == '__main__':
    supply = SimulatedPowerSupply()
    threading.Thread(target=supply.run).start()
