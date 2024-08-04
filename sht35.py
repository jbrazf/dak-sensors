import smbus2
import time

# Function to read data from the sensor
def read_sht35():
    # SHT35 address and commands
    SHT35_ADDRESS = 0x45  # Default I2C address of the SHT35
    MEASURE_CMD = [0x2C, 0x06]  # High repeatability measurement command

    # Open the I2C bus
    bus = smbus2.SMBus(0)

    # Send measurement command
    bus.write_i2c_block_data(SHT35_ADDRESS, MEASURE_CMD[0], MEASURE_CMD[1:])

    # Wait for the sensor measurement to complete
    time.sleep(0.5)

    # Read 6 bytes of data: temperature and humidity
    data = bus.read_i2c_block_data(SHT35_ADDRESS, 0x00, 6)

    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0

    # Close the I2C bus
    bus.close()

    return cTemp, humidity

def send_read_command(bus: smbus2.SMBus, address: int = 0x45):
    MEASURE_CMD = [0x2C, 0x06]
    bus.write_i2c_block_data(address, MEASURE_CMD[0], MEASURE_CMD[1:])

def read_values(bus: smbus2.SMBus, address: int = 0x45):
    data = bus.read_i2c_block_data(address, 0x00, 6)

    # Convert the data
    temp = data[0] * 256 + data[1]
    cTemp = -45 + (175 * temp / 65535.0)
    humidity = 100 * (data[3] * 256 + data[4]) / 65535.0
    
    return cTemp, humidity

# Main function to output the temperature and humidity
def print_sht35(temperature, humidity):
    print(f"Temperature: {temperature:.2f} C")
    print(f"Humidity: {humidity:.2f} %")


