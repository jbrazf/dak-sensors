from w1thermsensor import W1ThermSensor, Sensor

sensor_list: list[W1ThermSensor] = []

for sensor in W1ThermSensor.get_available_sensors([Sensor.DS18B20]):
    
    sensor_list.append(sensor)
    print("Sensor %s has temperature %.2f" % (sensor.id, sensor.get_temperature()))