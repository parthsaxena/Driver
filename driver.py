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

SERIAL_PORT = "/dev/cu.usbserial-A9VJRTLE"
        
if __name__ == '__main__':    

    async def main():
        lock = asyncio.Lock()
        power_supply_comm = PowerSupplyComm(SERIAL_PORT, lock, baudrate=9600)
        command_server = CommandServer(power_supply_comm)
        telemetry_server = TelemetryServer(power_supply_comm)
        await power_supply_comm.connect()
                
        loop = asyncio.get_event_loop()
        
        # Start telemetry server
        telemetry_task = loop.create_task(telemetry_server.run(host="localhost", port=8000))

        # Start command server
        command_task = loop.create_task(command_server.run(host="localhost", port=8001))                    

        await asyncio.gather(telemetry_task, command_task, return_exceptions=False)
    
    asyncio.run(main())