import time
from w1thermsensor import W1ThermSensor, Sensor

sensor_list: list[W1ThermSensor] = []

def bulk_read_temperatures():
    # Initialize the sensor
    sensor = W1ThermSensor()

    # Trigger bulk read
    with open("/sys/bus/w1/devices/w1_bus_master1/therm_bulk_read", "w") as f:
        f.write("trigger")

    # Wait for conversion to complete
    time.sleep(1)  # Adjust sleep time as necessary based on sensor conversion time

    # Read temperatures from all sensors
    sensors = W1ThermSensor.get_available_sensors()
    for sensor in sensors:
        temperature = sensor.get_temperature()
        print(f"Sensor {sensor.id}: {temperature:.2f}°C")


def get_sensor_list(sl) -> list[W1ThermSensor]:
    if sl == []:
        sl = W1ThermSensor.get_available_sensors([Sensor.DS18B20])
    return sl
    
def one_shot_temp():
    l = get_sensor_list(sl=sensor_list)
    return list(map(lambda x: x.get_temperature(), l))
    
if __name__ == "__main__":
    t0 = time.time()
    bulk_read_temperatures()
    t1 = time.time()
    print(t1-t0)
    
    pass
# end def