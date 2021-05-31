"""Test for nrf24l01 module.  Portable between MicroPython targets."""

import sys
import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

if sys.platform == "pyboard":
    cfg = {"spi": 2, "miso": "Y7", "mosi": "Y8", "sck": "Y6", "csn": "Y5", "ce": "Y4"}
elif sys.platform == "esp8266":  # Hardware SPI
    cfg = {"spi": 1, "miso": 12, "mosi": 13, "sck": 14, "csn": 4, "ce": 2}
elif sys.platform == "esp32":  # Software SPI
    cfg = {"spi": -1, "miso": 32, "mosi": 33, "sck": 25, "csn": 26, "ce": 27}
else:
    raise ValueError("Unsupported platform {}".format(sys.platform))

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
#pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
#pipes = (b"\x00\x04\x03\x02\x01", b"\x04\x04\x03\x02\x01")
pipes = (b"\x01\x02\x03\x04\x00", b"\x01\x02\x03\x04\x04")

csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
print("Using channel=100, 250K bitrate")
nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, channel=100, payload_size=32)
nrf.open_tx_pipe(pipes[0])

def master(num_needed=1, psize=32):
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    if cfg["spi"] == -1:
        spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
        nrf = NRF24L01(spi, csn, ce, payload_size=8)
    else:
        print("Using channel=100, 250K bitrate")
        nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, channel=100, payload_size=psize)

    nrf.open_tx_pipe(pipes[0])

    print("NRF24L01 master mode, sending %d packets..." % num_needed)
    num_sent = 0
    while num_sent < num_needed:
        # stop listening and send packet
        nrf.stop_listening()
        millis = utime.ticks_ms()
        print("sending ...")
        try:
            nrf.send(struct.pack("ii", millis))
        except OSError:
            pass

        num_sent += 1

        # delay then loop
        utime.sleep_ms(250)

    print("master finished sending!")


def slave():
    csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
    ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
    if cfg["spi"] == -1:
        spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
        nrf = NRF24L01(spi, csn, ce, payload_size=8)
    else:
        print("Using channel=100, 2M bitrate")
        nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, channel=100, payload_size=14)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])
    nrf.start_listening()

    print("NRF24L01 rx mode, waiting for packets... (ctrl-C to stop)")

    while True:
        if nrf.any():
            while nrf.any():
                buf = nrf.recv()
                uptime = struct.unpack("I",buf[1:5])
                vbatt = struct.unpack("f",buf[9:13])
                state = buf[13]
                print("uptime: ",uptime,"vbatt: ",vbatt, "state: ",state)


try:
    import pyb

    leds = [pyb.LED(i + 1) for i in range(4)]
except:
    leds = []

print("NRF24L01 test module loaded")
print("NRF24L01 pinout for test:")
print("    CE on", cfg["ce"])
print("    CSN on", cfg["csn"])
print("    SCK on", cfg["sck"])
print("    MISO on", cfg["miso"])
print("    MOSI on", cfg["mosi"])
print("run nrf24l01test.slave() on slave, then nrf24l01test.master() on master")

