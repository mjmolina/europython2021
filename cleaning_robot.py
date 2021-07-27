import time
import digitalio
import touchio
import board
import time
from adafruit_hcsr04.adafruit_hcsr04 import HCSR04
from adafruit_circuitplayground.express import cpx
from adafruit_crickit import crickit

# Adding servo for usonic sensor
servo_distance = crickit.servo_2

# Creating the motors connection on seesaw motor port #1 and #2
motor1 = crickit.dc_motor_1
motor2 = crickit.dc_motor_2

# we connect the HCSR04 sensor to the board trigger to A2 port 
# and Echo to the A3 port on the CPX.
sonar = HCSR04(trigger_pin=board.A3, echo_pin=board.A2, timeout=2)

# Period of time to check the system
wait_time = 1

# This needs to be adapted according the distance sensor
stop_value = 40

# Initial sensor value
servo_distance.angle = 90

# Button to manage the power of the system
cpx.pixels.brightness = 0.01
is_on = False

def get_sonar_distance():
    value = None
    while not value:
        try:
            value = sonar.distance
        except RuntimeError as e:
            print("Error, sleeping 1 sec", e)
            time.sleep(0.5)
    return value

# Move wheels
def move_motors(left, right):
    try:
        print("Move servos:", left, right)
        motor1.throttle = left
        motor2.throttle = right
        time.sleep(0.4)
    except OSError as e:
        print(e)
        time.sleep(0.3)
        motor1.throttle = 0
        motor2.throttle = 0

# Move the usonic sensor
def move_sonar_sensor90(direction):
    angle_time = 0.4
    if direction == "left":
        servo_distance.angle = 180
        time.sleep(angle_time)
        servo_distance.angle = 90
    elif direction == "right":
        servo_distance.angle = 0
        time.sleep(angle_time)
        servo_distance.angle = 90
    else:
        print("invalid direction")

def red_pixels():
    cpx.pixels.fill((255, 0, 0))
    cpx.pixels.show()

def green_pixels():
    cpx.pixels.fill((0, 255, 0))
    cpx.pixels.show()

def blue_pixels():
    cpx.pixels.fill((0, 0, 255))
    cpx.pixels.show()

# Main loop
while True:

    # We implement a system to start and stop the robot
    # with the help of the board 'A' button
    if cpx.button_a:
        if is_on:
            red_pixels()
            is_on = False
        else:
            green_pixels()
            is_on = True

    # Normal behavior when it's on
    if is_on:
        # Read value: depending of the sensor power
        # this might fail, we turn the blue light to be aware.
        try:
            distance = get_sonar_distance()
        except:
            blue_pixels()
            is_on = False
            break

        print("Distance:", distance)
        if distance < stop_value:
            print("Critical distnace, stoping")
            move_motors(0, 0)
            time.sleep(wait_time)

            print("Checking distance: left (0 degrees)")
            move_sonar_sensor90("left")
            distance_0 = get_sonar_distance()
            time.sleep(0.5)
            print("Left distance:", distance_0)

            print("Checking distance: right (180 degrees)")
            move_sonar_sensor90("right")  # back to the center
            move_sonar_sensor90("right")
            distance_180 = get_sonar_distance()
            time.sleep(0.5)
            print("Right distance:", distance_180)
            move_sonar_sensor90("left")  # back to center

            if distance_0 < distance_180:
                print("Turning Right")  
                move_motors(0.9, 0.9)
                time.sleep(0.2)
                move_motors(0, 0)
                time.sleep(0.2)
            else:
                print("Turning left")  
                move_motors(-0.9, -0.9)
                time.sleep(0.2)
                move_motors(0, 0)
                time.sleep(0.2)
        else:
            print("Normal movement")
            # Note that due to installation, the motors needs to be
            # handle differently, and not with the same 'throttle' values.
            # Also this implementation moves forward little-by-little
            move_motors(0.7, -0.7)
            time.sleep(0.5)
            move_motors(0, 0)
            time.sleep(0.5)

    time.sleep(0.5)
