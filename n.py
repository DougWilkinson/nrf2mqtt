from sensorclass import Sensor
from nrfclass import NRFSensor
from nrf24l01 import NRF24L01
import ustruct as struct
import utime,gc
from machine import Pin, SPI
gc.collect()
print(gc.mem_free())
from micropython import const


# nrf2mqtt
# updated 1/2/2021

def nrfInit(channel=100, payload=32, speed=0):
    si = [0x20, 0x0, 0x8]
    pipes = (b"\x01\x02\x03\x04\x00", b"\x01\x02\x03\x04\x04")
    csn = Pin(4, mode=Pin.OUT, value=1)
    ce = Pin(2, mode=Pin.OUT, value=0)
    nrf = NRF24L01(SPI(1), csn, ce, channel=100, payload_size=32, speed=si[speed])
    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()
    return nrf

def relay():
    if not Sensor.mqttconnected:
        Sensor.mqttconnected = Sensor.MQTTConnect()
    try:
        for nrf in NRFSensor.list:
            if NRFSensor.list[nrf].pubneeded:
                Sensor.Callpublish(Sensor.mqttclient, NRFSensor.basetopic, str(nrf) , [NRFSensor.list[nrf]])
    except:
        print("Error relaying from radio: ", nrf)
        Sensor.mqttconnected = False

def main():
    nrf = nrfInit()
    Sensor.MQTTSetup("nrf2mqtt")
    while True:
        Sensor.Spin()
        nrfcheck = utime.ticks_ms()
        if nrf.any():
            while (utime.ticks_ms() - nrfcheck) < 200:
                if nrf.any():
                    buf = nrf.recv()
                    radio = buf[0]
                    state = buf[13]
                    if radio not in NRFSensor.list:
                        NRFSensor(radio)
                        NRFSensor.list[radio].state = -1
                    NRFSensor.list[radio].update(buf[17],struct.unpack("I",buf[1:5])[0],struct.unpack("I",buf[5:9])[0], struct.unpack("I",buf[9:13])[0], struct.unpack("f",buf[13:17])[0])
                    print(NRFSensor.list[radio].publish)
                    nrfcheck = utime.ticks_ms()
            relay()
