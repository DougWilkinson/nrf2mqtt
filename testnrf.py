import ustruct as struct
import utime
from machine import Pin, SPI
from nrf24l01 import NRF24L01
from micropython import const


# testnrf
# updated 2/6/2021

pipes = (b"\x01\x02\x03\x04\x08", b"\x01\x02\x03\x04\x00")
csn = Pin(4, mode=Pin.OUT, value=1)
ce = Pin(2, mode=Pin.OUT, value=0)
nrf = NRF24L01(SPI(1), csn, ce, channel=100, payload_size=32, speed=0x20)
nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
#nrf.start_listening()

def xmit(nrf, radio=7,uptime=7,failed=777,sent=777,batt=7.7,state=77):
    buf = struct.pack("BIIIfB",radio,uptime,failed,sent,batt,state)
    print(buf)
    nrf.send(buf)

