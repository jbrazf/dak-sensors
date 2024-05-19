#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <wiringPi.h>

#define FLOW_SENSOR_PIN 27  // GPIO pin where the water flow sensor is connected
// #define LED_PIN 18           // GPIO pin to indicate the pulse count (optional)

volatile int pulseCount = 0; // Counter for pulse count

void countPulse()
{
    pulseCount++;
    // digitalWrite(LED_PIN, HIGH); // Optional: Turn on an LED to indicate each pulse
}


float calibrationFactor = 6.539;
double water_volume_total = 0;
unsigned long previousMills_pulse = 0;
unsigned short interval_pulse = 1000;
float flowRate;
float flowMilliLitres;
int pulse1Sec = 0;

int main()
{
    printf("Flow sensor pin used: %d \n", FLOW_SENSOR_PIN);
    if (wiringPiSetupGpio() == -1)
    {
        printf("wiringPi setup failed. Exiting...\n");
        return 1;
    }

    pinMode(FLOW_SENSOR_PIN, INPUT);
    // pinMode(LED_PIN, OUTPUT);

    // Attach the interrupt handler to the rising edge of the pulse signal
    if (wiringPiISR(FLOW_SENSOR_PIN, INT_EDGE_RISING, &countPulse) < 0)
    {
        printf("Unable to setup ISR. Exiting...\n");
        return 1;
    }

    printf("Water flow sensor pulse counter started.\n");

    int totall_pulse_count = 0;

    while (1)
    {
        if (millis() - previousMills_pulse > interval_pulse)
        {
            pulse1Sec = pulseCount;
            totall_pulse_count = totall_pulse_count + pulseCount;

            pulseCount = 0;

            flowRate = ((1000.0 / (millis() - previousMills_pulse)) * pulse1Sec) / calibrationFactor;
            previousMills_pulse = millis();
            
            printf("Flow Rate: %f\n", flowRate);
            // flowRate = pulse1Sec / calibrationFactor; // litre per minute
            flowMilliLitres = (flowRate / 60) * 1000;
            // flowMilliLitres = (flowRate / 60);
            printf("Pulse count: %d\n", pulse1Sec);
            printf("Pulse milli: %f\n", flowMilliLitres);
            water_volume_total = water_volume_total + flowMilliLitres;
            printf("Total pulses: %d\n", totall_pulse_count);
            printf("Total: %f\n", water_volume_total);

   
        }
    }
    return 0;
}
