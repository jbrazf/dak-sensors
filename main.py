import os
import time
import pika
import pzem
import sht35
import struct
import smbus2
import ds18b20
import argparse
import pressure

from termcolor import cprint

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

LOG = True

AMBIENT_I2C_DEV = 0
AMBIENT_ADDRESS = 0x45

PRESSURE_I2C_DEV = 1
PRESSURE_ADDRESS = 0x48
GAIN = 1


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='dak-sensors',
                                     description='Read all configured sensors in a timely manner')
    parser.add_argument('-v', '--verbose', action='store_true', help='if the program should print the values its reading')
    args = parser.parse_args()
    
    LOG = args.verbose
    
    # initialization
    ambient_bus   = smbus2.SMBus(AMBIENT_I2C_DEV)
    pressure_bus  = smbus2.SMBus(PRESSURE_I2C_DEV)
    temp_sensors  = ds18b20.init_sensors()
    temp_master   = open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'w')
    energy_sensor = pzem.init_sensor()
    
    # configuration
    pressure.configure_ads1100(pressure_bus, gain=8)
    
    
    # connection to rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='python_sensors')
        
    old_time = time.time_ns()
    
    while True:
        
        now = time.time_ns()
        t0 = time.time()
        # read commands/triggers
        ds18b20.send_bulk_read_trigger(temp_master, LOG)
        
        sht35.send_read_command(ambient_bus)
        t1 = time.time()
        
        if LOG: cprint(f"{t1-t0}", 'red')
        # read final values 
        
        ambient_data  = sht35.read_values(ambient_bus)
        pressure_data = pressure.read_ads1100(pressure_bus)
        energy_data   = pzem.read_registers(energy_sensor)
        temp_data     = ds18b20.read_bulk_temp(temp_sensors)
        
        # data serialization
        data = struct.pack('lfffffffffff', now, pressure_data, *ambient_data, *energy_data, *temp_data)
        
        if LOG: print("\033c")
        
        if LOG: cprint(f"    -> pressure {pressure_data}", 'blue')
        if LOG: cprint(f"    -> ambient {ambient_data}", 'blue')
        if LOG: cprint(f"    -> pzem {energy_data}", 'blue')
        if LOG: cprint(f"    -> temp {temp_data}", 'blue')
        
        # write to message queue
        channel.basic_publish(exchange='', routing_key='python_sensors', body=data)

        after_writing = time.time_ns()
        if LOG: cprint(f"[Ocupancy Time]: {(after_writing - now)/1_000_000_000}", 'yellow')
        
        
        while time.time_ns() < now + 1_000_000_000:
            time.sleep(0.01)
            
        if LOG: cprint(f"[Waited]: {(time.time_ns() - after_writing)/1_000_000_000}", 'yellow')
        if LOG: cprint(f"[Total time]: {(now - old_time)/1_000_000_000}", 'yellow')
        
        old_time = now
    
    # cleanup
    ambient_bus.close()
    pressure_bus.close()
    temp_master.close()
    
    print(f"time to read: {t1-t0}")

