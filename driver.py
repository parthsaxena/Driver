import asyncio
import json
from PowerSupplyComm import PowerSupplyComm
from TelemetryServer import TelemetryServer
from CommandServer import CommandServer

# Constants
BAUDRATE = 9600
TELEMETRY_PORT = 8000
COMMAND_PORT = 8001
SERIAL_PORT = "/dev/cu.usbserial-A9VJRTLE"
        
if __name__ == '__main__':    

    async def main():
        # Initialize lock for power supply transactions
        lock = asyncio.Lock()
        power_supply_comm = PowerSupplyComm(SERIAL_PORT, lock, baudrate=BAUDRATE)
        await power_supply_comm.connect()

        # Initialize command & telemetry servers
        command_server = CommandServer(power_supply_comm)
        telemetry_server = TelemetryServer(power_supply_comm)                                
        
        # Start servers
        loop = asyncio.get_event_loop()
        telemetry_task = loop.create_task(telemetry_server.run(host="localhost", port=TELEMETRY_PORT))        
        command_task = loop.create_task(command_server.run(host="localhost", port=COMMAND_PORT))                    

        await asyncio.gather(telemetry_task, command_task, return_exceptions=False)
    
    asyncio.run(main())