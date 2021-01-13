#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
import argparse

ports = {
    "SER1": {
        'SERIN': 3,
        'SRCK': 5,
        'RCK': 7,
        'G': 11,
        'CLR': 13
    },
    "SER2": {
        'SERIN': 8,
        'SRCK': 10,
        'RCK': 12,
        'G': 16,
        'CLR': 18
    },
    "SER3": {
        'SERIN': 29,
        'SRCK': 31,
        'RCK': 33,
        'G': 35,
        'CLR': 37
    },
    "SER4": {
        'SERIN': 22,
        'SRCK': 24,
        'RCK': 26,
        'G': 32,
        'CLR': 36
    }
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "pins",
    type=int,
    help="The pin(s) that should be set.",
    nargs="+",
    choices=range(1, 9)
)
parser.add_argument(
    "-p",
    "--port",
    help="(required) Serial port number that the board is attached to.",
    required=True,
    dest="port",
    choices=ports.keys()
)
parser.add_argument(
    "-r",
    "--reset",
    help="Flag this if you want to reset the pin(s)",
    action="store_true"
)
args = parser.parse_args()
GPIO.setmode(GPIO.BOARD)
GPIO.setup(list(ports[args.port].values()), GPIO.OUT)

out = [0, 0, 0, 0, 0, 0, 0, 0]

if args.reset:
    for pin in args.pins:
        out[len(out) - pin] = 0
else:
    for pin in args.pins:
        out[len(out) - pin] = 1

GPIO.output(ports[args.port]['CLR'], GPIO.HIGH)
GPIO.output(ports[args.port]['G'], GPIO.HIGH)

for val in out:
    print(val)
    GPIO.output(ports[args.port]['SERIN'], val)
    sleep(0.02)
    GPIO.output(ports[args.port]['SRCK'], GPIO.HIGH)
    sleep(0.02)
    GPIO.output(ports[args.port]['SRCK'], GPIO.LOW)

GPIO.output(ports[args.port]['RCK'], GPIO.HIGH)
sleep(0.02)
GPIO.output(ports[args.port]['RCK'], GPIO.LOW)
GPIO.output(ports[args.port]['G'], GPIO.LOW)

sleep(5)
GPIO.cleanup()
