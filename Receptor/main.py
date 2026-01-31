import struct
from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time

print("--- ROBOT FINAL: ESCUCHANDO ---")

# LED (GPIO 8)
led = Pin(8, Pin.OUT)
# Parpadeo de saludo
for _ in range(3):
    led.value(0); time.sleep(0.1); led.value(1); time.sleep(0.1)

# Pines C3
csn = Pin(7, mode=Pin.OUT, value=1)
ce = Pin(3, mode=Pin.OUT, value=0)
spi = SPI(1, baudrate=4000000, polarity=0, phase=0,
          sck=Pin(4), mosi=Pin(6), miso=Pin(5))

nrf = NRF24L01(spi, csn, ce, payload_size=4)

# --- SINCRONIZACIÓN ---
# Misma velocidad y canal que el mando
nrf.reg_write(0x06, 0x02) # 1Mbps, -12dBm
nrf.set_channel(120)

direccion = b'\xe1\xf0\xf0\xf0\xf0'
nrf.open_rx_pipe(1, direccion)
nrf.start_listening()

while True:
    if nrf.any():
        while nrf.any():
            try:
                buf = nrf.recv()
                (estado,) = struct.unpack("i", buf)
                
                if estado == 1:
                    print("¡TOCADO! -> ENCENDER")
                    led.value(0) # ON
                else:
                    print("SUELTO -> APAGAR")
                    led.value(1) # OFF
            except:
                pass