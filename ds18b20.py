import os
import glob
import time

bulk_read_dict = {
                '-1': 'still in conversion',
                '0' : 'no bulk conversion pending',
                '1' : 'conversion is complete'
            }

# Function to initialize the sensors and retrieve the device file paths
def init_sensors():
    base_dir = '/sys/bus/w1/devices/'
    device_folders = glob.glob(base_dir + '28*')
    device_files = [f + '/w1_slave' for f in device_folders]
    return device_files

def send_bulk_read_trigger(file, LOG: bool):
    if LOG: print("    sent bulk read trigger")
    r = -1
    r = file.write('trigger\n')
    file.flush()
    return r

def get_conversion_status():
    with open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'r') as f:
        conversion_status = f.read().strip()
        return conversion_status
        
def read_bulk_temp(device_files: list[str]):
    # Wait for conversions to finish by reading w1_master_bulk_read
    with open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'r') as f:
        conversion_status = f.read().strip()
        
        while conversion_status == -1:
            time.sleep(0.05)
            f.seek(0)
            conversion_status = f.read().strip()
            print(f"bulk read status: {bulk_read_dict[conversion_status]}")
    
    temperatures = []
    for device_file in device_files:
        lines = read_temp_raw(device_file)
        while (not lines) or (lines[0].strip()[-3:] != 'YES'):
            time.sleep(0.1)
            lines = read_temp_raw(device_file)  
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temperatures.append(temp_c)
    return temperatures

# Function to read temperature from a device file
def read_temp_raw(device_file):
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

# Function to read all temperatures in bulk
def read_temps_oneshot(device_files):
    # Write 'Y' to /sys/bus/w1/devices/w1_bus_master1/w1_master_slaves_bulk_read to trigger bulk read
    with open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'w') as f:
        f.write('trigger\n')
    
    # Wait for conversions to finish by reading w1_master_bulk_read
    with open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'r') as f:
        x = True
        while x: 
            v = f.read().strip()
            bulk_read_dict = {
                '-1': 'still in conversion',
                '0' : 'no bulk conversion pending',
                '1' : 'conversion is complete'
            }
            print(f"bulk read status: {bulk_read_dict[v]}")
            if v == "1": x = False
            f.seek(0)

    temperatures = {}
    for device_file in device_files:
        lines = read_temp_raw(device_file)
        while (not lines) or (lines[0].strip()[-3:] != 'YES'):
            time.sleep(0.1)
            lines = read_temp_raw(device_file)
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            temperatures[device_file] = {'Celsius': temp_c, 'Fahrenheit': temp_f}
    return temperatures

# Perform bulk read and print the results
if __name__ == "__main__":
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    
    t0 = time.time()
    device_files = init_sensors()
    temperatures = read_temps_oneshot(device_files)
    t1 = time.time()
    
    print(temperatures)
    print(t1-t0)