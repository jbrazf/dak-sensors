import RPi.GPIO as GPIO
import threading
import time

# GPIO setup
FLOW_SENSOR_PIN = 27  # Pin where the YF-B5 is connected
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLOW_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Variables for counting pulses and time
pulse_count = 0
flow_rate = 0

# Callback function to count pulses
def count_pulse(channel):
    global pulse_count
    pulse_count += 1

# Attach interrupt to GPIO pin
GPIO.add_event_detect(FLOW_SENSOR_PIN, GPIO.FALLING, callback=count_pulse)

# Function to calculate flow rate
def calculate_flow_rate():
    global pulse_count, flow_rate
    time_elapsed = 1.0  # Since we call this function every 1 second
    flow_rate = (pulse_count / time_elapsed) / 5.5
    print(f"Flow Rate: {flow_rate:.3f} L/min")
    pulse_count = 0  # Reset pulse count after each calculation

    # Schedule the next calculation
    threading.Timer(1.0, calculate_flow_rate).start()

try:
    # Start the first calculation after 1 second
    threading.Timer(1.0, calculate_flow_rate).start()

    # Keep the main thread running, but do nothing
    while True:
        time.sleep(10)

except KeyboardInterrupt:
    print("Measurement stopped by User")

finally:
    GPIO.cleanup()