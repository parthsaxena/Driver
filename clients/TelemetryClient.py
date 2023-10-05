import argparse
import asyncio
import time
from termcolor import colored

class TelemetryClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.count = 0

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        
    async def receive_telemetry(self):
        cumulative_latency = 0.0
        average_latency = 0.0
        start = None
        try:
            while True:
                data = await self.reader.read(100)
                if not data:
                    print("Connection closed by the server")
                    break                
                self.count += 1

                if not start:
                    start = time.time_ns()
                else:
                    end = time.time_ns()
                    cumulative_latency += end - start
                    start = end
                    average_latency = cumulative_latency / self.count

                digits = 2
                if (average_latency / (1e9)) < 0.01:
                    digits = 3

                prefix = colored(f'[{self.count}]', 'red', attrs=['bold', 'underline'])
                latency = f'{colored("Avg. Latency:", "green")} {colored(str(round(average_latency / (1e9), digits)) + "ms", "green", attrs=["bold"])}'
                print(f'{prefix} {data.decode()}   {latency}')                    
                
        except asyncio.CancelledError:
            pass
        finally:
            self.writer.close()
            await self.writer.wait_closed()

    async def run(self):
        await self.connect()
        await self.receive_telemetry()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telemetry Client')
    parser.add_argument('host', help='Host address of the telemetry server')
    parser.add_argument('port', type=int, help='Port number of the telemetry server')
    args = parser.parse_args()

    client = TelemetryClient(args.host, args.port)
    asyncio.run(client.run())