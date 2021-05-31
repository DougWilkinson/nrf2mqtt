from sensorclass import Sensor
from nrfclass import NRFSensor
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const


# nrf2mqtt
# updated 1/2/2021

pipes = (b"\x01\x02\x03\x04\x00", b"\x01\x02\x03\x04\x04")
csn = Pin(4, mode=Pin.OUT, value=1)
ce = Pin(2, mode=Pin.OUT, value=0)
nrf = NRF24L01(1, csn, ce, channel=100, payload_size=32)
nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
nrf.start_listening()

def main():
    Sensor.MQTTSetup("template")
    while True:
        Sensor.Spin()
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                radio = buf[0]
                if radio not in NRFSensor.list:
                    NRFSensor(radio)
                NRFSensor.list[radio].update(buf[13],struct.unpack("I",buf[1:5]), struct.unpack("f",buf[9:13])
                print(NRFSensor.list[radio].publish)
                NRFSensor.Spin()
