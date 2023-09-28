import json
import asyncio
from PowerSupplyComm import PowerSupplyComm

# Constants
DATA_COLLECTION_FREQUENCY = 50
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
        latest_telemetry = None
        while True:
            if len(self.clients) > 0:                               
                # Pop all older telemetry data until latest
                while self.queue.qsize() > 1:
                    await self.queue.get()
                
                # Get latest telemetry if available
                if self.queue.qsize() != 0:
                    latest_telemetry = await self.queue.get()                
                
                # Convert telemetry dict to JSON
                telemetry_data = json.dumps(latest_telemetry)

                # Store disconnected clients while broadcasting
                disconnected_clients = []

                # Broadcast data to each client
                for client in self.clients:                
                    # Attempt to write telemetry data to client
                    try:
                        client.write(telemetry_data.encode())
                        await client.drain()
                    except (ConnectionResetError, BrokenPipeError, OSError) as e:
                        print(f"Telemetry client disconnected: {client.get_extra_info('peername')}")
                        disconnected_clients.append(client)
                
                # Remove each client that is disconnected
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