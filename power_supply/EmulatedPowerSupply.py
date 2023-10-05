import serial

class EmulatedPowerSupply:
    def __init__(self):        
        self.commanded_voltage = 0.0
        self.commanded_current = 0.0
        self.voltage = 0.0
        self.current = 0.0
        
        self.output_state = False

    def set_voltage(self, voltage):
        self.commanded_voltage = voltage
        self.voltage = voltage

    def set_current(self, current):
        self.commanded_current = current
        self.current = current

    def handle_command(self, command):
        if command == "SOUR:VOLT?":
            return str(self.voltage)
        elif command.startswith("SOUR:VOLT"):
            try:
                voltage = float(command.split()[-1])
                self.set_voltage(voltage)
                return "OK"
            except ValueError:
                return "ERR"
        elif command == "SOUR:CURR?":
            return str(self.current)
        elif command.startswith("SOUR:CURR"):
            try:
                current = float(command.split()[-1])
                self.set_current(current)
                return "OK"
            except ValueError:
                return "ERR"
        elif command == "OUTP:STAT?":
            return "ON" if self.output_state else "OFF"
        elif command.startswith("OUTP:STAT"):
            state = command.split()[-1]
            if state == "ON":
                self.output_state = True
                return "OK"
            elif state == "OFF":
                self.output_state = False
                return "OK"
            else:
                return "ERR"
        else:
            return "ERR"


def main():
    psu = EmulatedPowerSupply()

    with serial.Serial('/dev/ttyUSB0', 9600) as ser:
        while True:            
            command = ser.readline().decode('ascii').strip()
            if command:                
                print(f"Received command {command}")
                response = psu.handle_command(command)
                ser.write((response + "\n").encode('ascii'))

if __name__ == '__main__':
    main()
