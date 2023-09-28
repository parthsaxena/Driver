import asyncio

class PowerSupplyComm:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    async def disconnect(self):
        # check if we are connected
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send_command(self, command):
        """
        Sends an SCPI command to the power supply
        """

        # make sure we are connected
        if self.writer is None:
            raise Exception("Connection not established. Call connect() first.")
        
        # write to socket
        self.writer.write(command.encode())
        await self.writer.drain()

        # read response from socket             
        try:
            response = await asyncio.wait_for(self.reader.readline(), timeout=5.0)  # 5 seconds timeout
        except asyncio.TimeoutError:
            print("Timeout while waiting for response")
            return None
        return response.decode()
    
    async def get_telemetry(self):
        """
        Retrieves telemetry data from power supply.
        Assumes SCPI commands 'MEAS:VOLT?' and 'MEAS:CURR?'
        """        

        voltage = await self.send_command('MEAS:VOLT?')        
        current = await self.send_command('MEAS:CURR?')

        telemetry_dict = {
            'voltage': float(voltage),
            'current': float(current)
        }

        return telemetry_dict