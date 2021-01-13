# Flask Server imports
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
# Mock imports
import sys
import fake_rpi

sys.modules['RPi'] = fake_rpi.RPi  # Fake RPi (GPIO)
sys.modules['RPi.GPIO'] = fake_rpi.RPi._GPIO

# pylint: disable=wrong-import-position
# GPIO imports
import RPi.GPIO as GPIO
from time import sleep
# pylint: enable=wrong-import-position

ports = {}
pinStates = {
    "SER1": [0, 0, 0, 0, 0, 0, 0, 0],
    "SER2": [0, 0, 0, 0, 0, 0, 0, 0],
    "SER3": [0, 0, 0, 0, 0, 0, 0, 0],
    "SER4": [0, 0, 0, 0, 0, 0, 0, 0]
}

app = Flask(__name__)
CORS(app)
GPIO.setmode(GPIO.BOARD)


@app.route('/setup', methods=['POST'])
def setup():
    response = {'status': 'success'}
    if request.method == 'POST':
        print("Received Setup-Data: ")
        data = request.get_json()
        ports[data["port"]] = data["gpio"]
        ports[data["port"]]['board'] = data["board"]
        print(ports)
        response["ports"] = ports
        if data["board"] == "im8":
            GPIO.setup(ports[data["port"]]["SERIN"],
                       GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(ports[data["port"]]["SRCK"], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(ports[data["port"]]["RCK"], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(ports[data["port"]]["G"], GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(ports[data["port"]]["CLR"], GPIO.OUT, initial=GPIO.HIGH)
        elif data["board"] == "om8":
            GPIO.setup(ports[data["port"]]["MODE"],
                       GPIO.OUT, initial=GPIO.HIGH)
            GPIO.setup(ports[data["port"]]["SEROUT"], GPIO.IN)
            GPIO.setup(ports[data["port"]]["CLK"], GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(ports[data["port"]]["CLKSTOP"],
                       GPIO.OUT, initial=GPIO.LOW)
        return jsonify(response)
    else:
        return jsonify("Fail")


@app.route('/cleanup', methods=['POST'])
def cleanup():
    response = {'status': 'success'}
    if request.method == 'POST':
        print("Cleaning GPIOs")
        GPIO.cleanup()
        return jsonify(response)
    else:
        return jsonify("Fail")


@app.route('/shift', methods=['POST'])
def shift():
    response = {'status': 'success'}
    if request.method == 'POST':
        data = request.get_json()
        print("Shifting received data")
        if ports[data['port']]['board'] == 'im8':
            print("Shifting on im8...")
            if isinstance(data['pin'], list):
                print("... with list")
                for pin in data['pin']:
                    pinStates[data['port']][len(
                        pinStates[data['port']]) - pin] ^= 1
            else:
                print("... with single pin")
                pinStates[data['port']][data['pin']-1] ^= 1
            GPIO.output(ports[data['port']]['G'], GPIO.HIGH)
            for val in pinStates[data['port']]:
                GPIO.output(ports[data['port']]['SERIN'], val)
                sleep(0.02)
                GPIO.output(ports[data['port']]['SRCK'], GPIO.HIGH)
                sleep(0.02)
                GPIO.output(ports[data['port']]['SRCK'], GPIO.LOW)
            GPIO.output(ports[data['port']]['RCK'], GPIO.HIGH)
            sleep(0.02)
            GPIO.output(ports[data['port']]['RCK'], GPIO.LOW)
            GPIO.output(ports[data['port']]['G'], GPIO.LOW)
        elif ports[data['port']]['board'] == 'om8':
            print("Reading on om8")
            GPIO.output(ports[data['port']]['MODE'], GPIO.LOW)
            sleep(0.02)
            GPIO.output(ports[data['port']]['MODE'], GPIO.HIGH)
            for i in range(8):
                GPIO.output(ports[data['port']]['CLK'], GPIO.HIGH)
                sleep(0.02)
                GPIO.output(ports[data['port']]['CLK'], GPIO.LOW)
                pinStates[data['port']][i] = GPIO.input(
                    ports[data['port']]['SEROUT'])
        print(f"pinStates@{data['port']}: {pinStates[data['port']]}")
        response["pinStates"] = pinStates[data['port']]
        response["port"] = data['port']
        return jsonify(response)
    else:
        return jsonify("Fail")


if __name__ == '__main__':
    try:
        print("Starting app")
        app.run(debug=True, host="127.0.0.1", port="5000")
    except Exception as e:
        print(e)
        GPIO.cleanup()
    GPIO.cleanup()
