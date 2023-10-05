import asyncio
import json
from PowerSupplyComm import PowerSupplyComm
from termcolor import colored

class CommandServer:
    def __init__(self, power_supply_comm):
        self.power_supply_comm = power_supply_comm

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(100)
            if not data:
                break

            res = "ERR"
            try:
                command = json.loads(data.decode())
                if 'set_voltage' in command:    
                    res = await self.power_supply_comm.set_voltage(command["set_voltage"])                            
                    # res = await self.power_supply_comm.send_command(f'SOUR:VOLT {command["set_voltage"]}')
                if 'set_current' in command:
                    res = await self.power_supply_comm.set_current(command["set_current"]) 
                    # res = await self.power_supply_comm.send_command(f'SOUR:CURR {command["set_current"]}')
                if 'enabled' in command:                    
                    res = await self.power_supply_comm.set_enabled(command["enabled"]) 
                    # res = await self.power_supply_comm.send_command(f'OUTP {val}')
            except Exception as e:
                print(f"Got exception {e}")
                pass            

            # check if client is disconnected
            if writer.transport.is_closing():
                print(colored("[CommandServer]", 'green', attrs=['bold']), "Commmand client disconnected")
                writer.close()
                await writer.wait_closed()
                return
            
            # attempt to write
            try:
                writer.write(res.encode() + b'\n')            
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(colored("[CommandServer]", 'green', attrs=['bold']), f"Failed to write to client, disconnecting: {e}")                            
                writer.close()
                await writer.wait_closed()
                return
            
    async def run(self, host, port):
        server = await asyncio.start_server(
            self.handle_client, host, port
        )

        server_location = colored(f"{host}:{port}", 'white', 'on_green')
        print(colored("[CommandServer]", 'green', attrs=['bold']), f'Command server listening on {server_location}')
        async with server:
            await server.serve_forever()