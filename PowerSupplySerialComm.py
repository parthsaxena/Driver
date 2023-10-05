import serial

def interpret_status_byte(status_byte):
    status_bits = format(status_byte, '08b')
    print(f"Status Byte: {status_bits}")
    print(f"Overvoltage Protection Enabled: {status_bits[0] == '1'}")
    print(f"Output Enabled: {status_bits[1] == '1'}")
    print(f"Overcurrent Protection Enabled: {status_bits[3] == '1'}")
    print(f"Constant Current Mode: {status_bits[7] == '1'}")

def main():
    port = '/dev/cu.usbmodem001825B904581'  # Replace with your port
    baudrate = 9600  # Replace with your baud rate if different

    with serial.Serial(port, baudrate, timeout=1) as ser:
        ser.write(b'STATUS?\n')
        response = ser.read()
        if response:
            status_byte = ord(response)
            interpret_status_byte(status_byte)
        else:
            print("No response received.")

if __name__ == "__main__":
    main()