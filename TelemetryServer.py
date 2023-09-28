import json
import asyncio
from PowerSupplyComm import PowerSupplyComm

# Constants
DATA_COLLECTION_FREQUENCY = 10
BROADCAST_FREQUENCY = 10

class TelemetryServer:
    def __init__(self, power_supply_comm):
        self.power_supply_comm = power_supply_comm
        self.clients = []
        self.queue = asyncio.Queue()

    async def handle_client(self, reader, writer):
        self.clients.append(writer)
        addr = writer.get_extra_info('peername')
        print(f'Telemetry server received connection from {addr}')

    async def collect_data(self):
        while True:
            telemetry_dict = await self.power_supply_comm.get_telemetry()
            await self.queue.put(telemetry_dict)
            # print("collected data!")
            await asyncio.sleep(1 / DATA_COLLECTION_FREQUENCY)

    async def broadcast_telemetry(self):
        while True:
            if len(self.clients) > 0:                               
                while self.queue.qsize() > 1:
                    await self.queue.get()

                telemetry_dict = await self.queue.get()
                # print(f"got latest data {telemetry_dict}")
                telemetry_data = json.dumps(telemetry_dict)

                disconnected_clients = []

                for client in self.clients:                
                    # Attempt to write telemetry data to client
                    try:
                        client.write(telemetry_data.encode())
                        await client.drain()
                    except (ConnectionResetError, BrokenPipeError, OSError) as e:
                        print(f"Telemetry client disconnected: {client.get_extra_info('peername')}")
                        disconnected_clients.append(client)
                
                for client in disconnected_clients:                 
                    self.clients.remove(client)
                    try:
                        client.close()
                        await client.wait_closed()                    
                    except Exception as e:
                        pass                    

            await asyncio.sleep(1 / BROADCAST_FREQUENCY)

    async def run(self, host, port):
        server = await asyncio.start_server(
            self.handle_client, host, port
        )

        # spawn data collectio & broadcast tasks
        collection_task = asyncio.create_task(self.collect_data())
        broadcast_task = asyncio.create_task(self.broadcast_telemetry())

        print(f'Telemetry server listening on {host}:{port}')
        async with server:
            await server.serve_forever()