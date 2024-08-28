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
import RPi.GPIO as GPIO
from termcolor import cprint

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

AMBIENT_I2C_DEV = 0
AMBIENT_ADDRESS = 0x45

PRESSURE_I2C_DEV = 1
PRESSURE_ADDRESS = 0x48
GAIN = 1

FLOW_SENSOR_PIN = 27

def init_non_dryer_sensors():
    pressure_bus = smbus2.SMBus(PRESSURE_I2C_DEV)
    temp_sensors = ds18b20.init_sensors()
    temp_master = open('/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read', 'w')
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    pulse_count = 0
    flow_rate = 0
    
    pressure.configure_ads1100(pressure_bus, gain=8)
    GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.RISING, callback=count_pulse)
    
    return pressure_bus, temp_sensors, temp_master, pulse_count, flow_rate

def cleanup_non_dryer_sensors(pressure_bus, temp_master):
    pressure_bus.close()
    temp_master.close()

def count_pulse(channel):
    global pulse_count
    pulse_count += 1

if __name__ == "__main__":
    global pulse_count
    parser = argparse.ArgumentParser(prog='dak-sensors',
                                     description='Read all configured sensors in a timely manner')
    parser.add_argument('-v', '--verbose', action='store_true', help='if the program should print the values it’s reading')
    parser.add_argument('-w', '--washer', action='store_true', help='If this program is running for a washer')
    args = parser.parse_args()
    
    LOG = args.verbose
    WASHER = not args.dryer
    
    # initialization
    ambient_bus = smbus2.SMBus(AMBIENT_I2C_DEV)
    energy_sensor = pzem.init_sensor()
    
    if WASHER:
        pressure_bus, temp_sensors, temp_master, pulse_count, flow_rate = init_non_dryer_sensors()
    
    # connection to rabbitmq
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='python_sensors')
    
    old_time = time.time_ns()
    
    while True:
        if WASHER:
            liters_per_pulse = 1.0 / (6.539 * 60)
            water_data = pulse_count * liters_per_pulse
            flow_rate = (pulse_count / 1) / 6.539
            
            cprint(f'pulse count - {pulse_count}', 'red', 'on_black')
            pulse_count = 0
            
            # Read non-dryer sensors
            ds18b20.send_bulk_read_trigger(temp_master, LOG)
            pressure_data = pressure.read_ads1100(pressure_bus)
            temp_data = ds18b20.read_bulk_temp(temp_sensors)
        else:
            water_data = 0
            flow_rate = 0
            pressure_data = 0
            temp_data = [0, 0]
        
        sht35.send_read_command(ambient_bus)
        t1 = time.time()
        
        if LOG:
            cprint(f"{t1 - time.time()}", 'red')
        
        # Read ambient and energy sensors
        ambient_data = sht35.read_values(ambient_bus)
        energy_data = pzem.read_registers(energy_sensor)
        
        # Data serialization
        data = struct.pack('l13f', time.time_ns(), pressure_data, *ambient_data, *energy_data, *temp_data, water_data, flow_rate)
        
        if LOG:
            print("\033c")
            cprint(f"    -> pressure {pressure_data}", 'blue')
            cprint(f"    -> ambient {ambient_data}", 'blue')
            cprint(f"    -> pzem {energy_data}", 'blue')
            cprint(f"    -> temp {temp_data}", 'blue')
            cprint(f"    -> water used {water_data}", 'blue')
            cprint(f"    -> flow rate {flow_rate}", 'blue')
        
        # Write to message queue
        channel.basic_publish(exchange='', routing_key='python_sensors', body=data)
        
        after_writing = time.time_ns()
        if LOG:
            cprint(f"[Ocupancy Time]: {(after_writing - time.time_ns())/1_000_000_000}", 'yellow')
        
        while time.time_ns() < time.time_ns() + 1_000_000_000:
            time.sleep(0.01)
        
        if LOG:
            cprint(f"[Waited]: {(time.time_ns() - after_writing)/1_000_000_000}", 'yellow')
            cprint(f"[Total time]: {(time.time_ns() - old_time)/1_000_000_000}", 'yellow')
        
        old_time = time.time_ns()
    
    if WASHER:
        cleanup_non_dryer_sensors(pressure_bus, temp_master)
    
    print(f"time to read: {t1 - time.time()}")