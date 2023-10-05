import asyncio
import serial_asyncio
from termcolor import colored

TIMEOUT = 1.0

class PowerSupplyComm:
    def __init__(self, port, lock, baudrate=9600, timeout=5):
        # config to communicate with serial port
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.reader = None
        self.writer = None

        # Commanded variables
        self.commanded_voltage = -1.0
        self.commanded_current = -1.0
        self.enabled = False

        # Lock to ensure R/W transactions don't occur concurrently                
        self.lock = lock

    async def connect(self):
        loop = asyncio.get_event_loop()
        self.reader, self.writer = await serial_asyncio.open_serial_connection(loop=loop, url=self.port, baudrate=self.baudrate)
        print(colored("[PowerSupplyComm]", 'cyan', attrs=['bold']), f"Connected to power supply at {colored(self.port, 'white', 'on_cyan')}")

    async def disconnect(self):
        # Check if we are connected first
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

    async def send_command(self, command):
        async with self.lock:
            # Make sure we are connected
            if self.writer is None:
                raise Exception("No connection to power supply.")
            
            # Write to socket / wait until write buffer clears
            self.writer.write((command + '\n').encode())            
            await self.writer.drain()
                        
            try:
                response = await asyncio.wait_for(self.reader.readline(), timeout=TIMEOUT)
                return response.decode().strip()
            except Exception as e:
                print(colored("[PowerSupplyComm]", 'cyan', attrs=['bold']), "Power supply didn't respond in time.")
                return "ERR"        
    
    async def get_telemetry(self):
        # Send commands to get voltage and current
        voltage = await self.send_command('SOUR:VOLT?')        
        current = await self.send_command('SOUR:CURR?')    

        # Make sure we got response from psu 
        if voltage == "ERR" or current == "ERR":
            return None

        # Build response with all channels
        telemetry_dict = {
            'voltage': float(voltage),
            'current': float(current),
            'set_voltage': float(self.commanded_voltage),
            'set_current': float(self.commanded_current),
            'enabled': self.enabled
        }

        return telemetry_dict
    
    async def set_voltage(self, new_voltage):
        self.commanded_voltage = new_voltage
        res = await self.send_command(f'SOUR:VOLT {new_voltage}')

        return res
    
    async def set_current(self, new_current):
        self.commanded_current = new_current
        res = await self.send_command(f'SOUR:CURR {new_current}')

        return res

    async def set_enabled(self, new_enabled):
        self.enabled = new_enabled
        msg = "ON" if self.enabled else "OFF"
        res = await self.send_command(f'OUTP:STAT {msg}')

        return res
    
    def __print(self, str):
        print(colored("[PowerSupplyComm]", 'cyan', attrs=['bold']), str)  