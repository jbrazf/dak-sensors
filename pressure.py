import smbus2
import time

# Function to write configuration register
def configure_ads1100(bus: smbus2.SMBus, address: int = 0x48, gain: int = 1):
    # Gain settings: 0x00 for 1, 0x01 for 2, 0x02 for 4, 0x03 for 8
    gain_config = {
        1: 0x00,
        2: 0x01,
        4: 0x02,
        8: 0x03
    }
    if gain not in gain_config:
        raise ValueError("Invalid gain value. Choose from 1, 2, 4, or 8.")
    
    # Configuration byte format: [0, 0, 0, gain (2 bits), 0, 0, 0, 0]
    config_byte = gain_config[gain] << 4
    bus.write_byte(address, config_byte)

def read_ads1100(bus: smbus2.SMBus, address: int = 0x48):
    # Read 2 bytes of data
    data = bus.read_i2c_block_data(address, 0x00, 2)
    
    # Convert the data to 16-bits
    adc = (data[0] << 8) | data[1]
    
    # Check if 16th bit is set (negative number in 2's complement form)
    if adc & 0x8000:
        adc -= 65536
    
    return adc

def convert_to_voltage(adc_value, v_ref=5.0, gain=1):
    # Convert ADC reading to voltage
    # Adjust the reference voltage based on the gain
    voltage = (adc_value / 32767.0) * (v_ref / gain)
    return voltage

def main():
    I2C_ADDRESS = 0x48  # Change as needed
    GAIN = 2  # Change gain as needed (1, 2, 4, or 8)
    bus = smbus2.SMBus(1)
    
    try:
        configure_ads1100(bus, I2C_ADDRESS, GAIN)
        while True:
            adc_output = read_ads1100(bus, I2C_ADDRESS)
            voltage = convert_to_voltage(adc_output, gain=GAIN)
            pressure = (voltage - 0.5) * (1.6 / (4.5 - 0.5))
            print(f"Voltage: {voltage:.3f} Pressure: {pressure:.3f} V")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
    finally:
        bus.close()

if __name__ == "__main__":
    main()
