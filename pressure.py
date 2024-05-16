import smbus2
import time

def read_ads1100(bus, address):
    # Read 2 bytes of data
    data = bus.read_i2c_block_data(address, 0x00, 2)
    
    # Convert the data to 16-bits
    adc = (data[0] << 8) | data[1]
    
    # Check if 16th bit is set (negative number in 2's complement form)
    if adc & 0x8000:
        adc -= 65536
    
    return adc

def convert_to_voltage(adc_value, v_ref=5.0):
    # Convert ADC reading to voltage
    # Assuming the ADC value ranges from 0 to 32767 for 0V to 5V
    voltage = (adc_value / 32767.0) * v_ref
    return voltage

def main():
    I2C_ADDRESS = 0x48  # Change as needed
    bus = smbus2.SMBus(1)
    
    try:
        while True:
            adc_output = read_ads1100(bus, I2C_ADDRESS)
            voltage = convert_to_voltage(adc_output)
            print(f"Voltage: {voltage:.3f} V")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by user")
    finally:
        bus.close()

if __name__ == "__main__":
    main()
