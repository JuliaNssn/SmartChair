import MessageGenerator as msg_gen
import serial
import time
import gyroscope
import sys

import find_serialport


sys.path.append('/home/chair/git/SmartChair/pi_python/py-beacon')
from proximity import Scanner
scanner = Scanner(loops=3)

# port = serial.Serial("/dev/tty.wchusbserial410", 9600, timeout=None)
port = serial.Serial(find_serialport.get_serial_port(), 9600, timeout=None)
# port = serial.Serial("com3", 9600, timeout=None)
port = False

pressure_sensor_ids = list(range(0, 10))
acceleration_sensor_ids = list(range(0, 3))
test = list(range(0, 16))


def distance_sensor():
    json_list = []
    print("distance_sensor()")
    # get Values
    value = [1]
    # Validation

    # get json
    json_list.append(msg_gen.pack_to_json(1, "distance", [0], value))
    return json_list


def acceleration_sensor():
    print("acceleration_sensor")
    json_list = []
    gyro_values = []
    gyro_values.append(gyroscope.get_accelerator_values())
    gyro_values.append(gyroscope.get_gyro_values())

    # get json
    json_list.append(msg_gen.pack_to_json(1, "acceleration", acceleration_sensor_ids, gyro_values[0]))
    json_list.append(msg_gen.pack_to_json(1, "gyroscope", acceleration_sensor_ids, gyro_values[1]))

    return json_list


def sound_sensor():
    json_list = []
    print("sound_sensor()")
    # get Values
    value = [1]
    # Validation

    # get json
    json_list.append(msg_gen.pack_to_json(1, "sound", [0], value))
    return json_list


def location():
    json_list = []
    print("location()")
    # get Values

    while True:
        for beacon in scanner.scan():
            # get values
            splitArr = beacon.split(',')

            # build json string
            json = '{"uuid" : "' + str(splitArr[1]) + '", "major" : "' + str(splitArr[2]) + '", "minor" : "' + str(
                splitArr[3]) + '", "dB" : "' + str(splitArr[5]) + '", "time" : ' + time.time() + '}'

            # add to queue
            json_list.append(json)

    return json_list


def serial_sensors():

    #print("port is open: ", port.is_open)
    json_list = []

    port.write(b'ss')
    port.flush()

    while not port.inWaiting():
        time.sleep(0.001)
        # print("waiting for lines")

    start_sequence = port.read()
    print(start_sequence)

    while not start_sequence == b'G':
        print("start_sequence not valid")
        time.sleep(0.001)
        start_sequence = port.read()

    port.read(2)

    print("start_sequence valid")
    analogs = []
    analog_values = []

    i = 0
    while i < 16:
        analogs.append(port.readline())
        i += 1

    temperature = port.read(6)

    j = 0
    while j < 16:

        if j == 4:
            j += 4

        if j == 14:
            break

        analog_values.append(int(analogs[j]))
        j += 1


    temperature_value = []
    temperature_value.append(float(temperature))

    print("analogs: ", analog_values)
    print("temperature: ", temperature_value)
    json_list.append(msg_gen.pack_to_json(1, "pressure", pressure_sensor_ids, analog_values))
    json_list.append(msg_gen.pack_to_json(1, "temperature", [0], temperature_value))

    return json_list