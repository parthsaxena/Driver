import asyncio
import json
from PowerSupplyComm import PowerSupplyComm
from TelemetryServer import TelemetryServer
from CommandServer import CommandServer

# Constants
BAUDRATE = 9600
READ_BYTES = 128
READ_FREQUENCY = 20
BROADCAST_FREQUENCY = 10
        
if __name__ == '__main__':
    power_supply_comm = PowerSupplyComm('localhost', 5025)
    command_server = CommandServer(power_supply_comm)
    telemetry_server = TelemetryServer(power_supply_comm)

    async def main():
        await power_supply_comm.connect()
                

        # Start telemetry server
        telemetry_task = asyncio.create_task(telemetry_server.run(host="localhost", port=8000))

        # Start command server
        command_task = asyncio.create_task(command_server.run(host="localhost", port=8001))
                        
        await asyncio.gather(telemetry_task, command_task, return_exceptions=True)

    asyncio.run(main())