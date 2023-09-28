import asyncio
import json
from PowerSupplyComm import PowerSupplyComm

class CommandServer:
    def __init__(self, power_supply_comm):
        self.power_supply_comm = power_supply_comm

    async def handle_client(self, reader, writer):
        while True:
            data = await reader.read(100)
            if not data:
                break

            command = json.loads(data.decode())
            if 'set_voltage' in command:                                
                res = await self.power_supply_comm.send_command(f'SOUR:VOLT {command["set_voltage"]}')
            if 'set_current' in command:
                res = await self.power_supply_comm.send_command(f'SOUR:CURR {command["set_current"]}')
            if 'enabled' in command:
                val = "ON" if command["set_voltage"] else "OFF"
                res = await self.power_supply_comm.send_command(f'OUTP {val}')

            # check if client is disconnected
            if writer.transport.is_closing():
                print("Commmand client disconnected")
                writer.close()
                await writer.wait_closed()
                return
            
            # attempt to write
            try:
                writer.write(res.encode() + b'\n')            
                await writer.drain()
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"Failed to write to client, disconnecting: {e}")                            
                writer.close()
                await writer.wait_closed()
                return
            
    async def run(self, host, port):
        server = await asyncio.start_server(
            self.handle_client, host, port
        )

        print(f'Command server listening on {host}:{port}')
        async with server:
            await server.serve_forever()