import minimalmodbus
import serial

def init_sensor():
    sensor = minimalmodbus.Instrument('/dev/serial0', 0xF8)  # Adjust '/dev/ttyUSB0' to your serial port
    sensor.serial.baudrate = 9600
    sensor.serial.bytesize = 8
    sensor.serial.parity = serial.PARITY_NONE
    sensor.serial.stopbits = 1
    sensor.serial.timeout = 1
    sensor.mode = minimalmodbus.MODE_RTU
    return sensor

def read_registers(sensor: minimalmodbus.Instrument):
    try:
        # Read 10 registers starting from 0x0000
        registers = sensor.read_registers(0x0000, 10, 4)

        voltage = registers[0] / 10.0  # Voltage in V
        current = ((registers[2] << 16) + registers[1]) / 1000.0  # Current in A
        power = ((registers[4] << 16) + registers[3]) / 10.0  # Power in W
        energy = ((registers[6] << 16) + registers[5])  # Energy in Wh
        frequency = registers[7] / 10.0  # Frequency in Hz
        power_factor = registers[8] / 100.0  # Power Factor
        alarm = registers[9]  # Alarm status
        
        return (voltage, current, power, energy, frequency, power_factor)
    except Exception as e:
        print(f"Error reading from PZEM-004T V3: {e}")
        return -1    

def print_pzem_registers(registers: tuple[float, float, float, int, float, float]):
    
    print(f"Voltage: {registers[0]}V")
    print(f"Current: {registers[1]}A")
    print(f"Power: {registers[2]}W")
    print(f"Energy: {registers[3]}Wh")
    print(f"Frequency: {registers[4]}Hz")
    print(f"Power Factor: {registers[5]}")


if __name__ == "__main__":
    
    sensor = minimalmodbus.Instrument('/dev/serial0', 0xF8)  # Adjust '/dev/ttyUSB0' to your serial port
    sensor.serial.baudrate = 9600
    sensor.serial.bytesize = 8
    sensor.serial.parity = serial.PARITY_NONE
    sensor.serial.stopbits = 1
    sensor.serial.timeout = 1
    sensor.mode = minimalmodbus.MODE_RTU
    
    try:
        # Read 10 registers starting from 0x0000
        registers = sensor.read_registers(0x0000, 10, 4)

        voltage = registers[0] / 10.0  # Voltage in V
        current = ((registers[2] << 16) + registers[1]) / 1000.0  # Current in A
        power = ((registers[4] << 16) + registers[3]) / 10.0  # Power in W
        energy = ((registers[6] << 16) + registers[5])  # Energy in Wh
        frequency = registers[7] / 10.0  # Frequency in Hz
        power_factor = registers[8] / 100.0  # Power Factor
        alarm = registers[9]  # Alarm status
        
        print_pzem_registers((voltage, current, power, energy, frequency, power_factor))
    except Exception as e:
        print(f"Error reading from PZEM-004T V3: {e}")
        print(-1)