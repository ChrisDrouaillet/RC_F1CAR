import struct
from machine import Pin, SPI
from nrf24l01 import NRF24L01
import time

print("--- MANDO FINAL: TOUCH + BAJO CONSUMO ---")

# Pines
sensor_touch = Pin(14, Pin.IN) 
led_wroom = Pin(2, Pin.OUT) # Feedback visual
csn = Pin(5, mode=Pin.OUT, value=1)
ce = Pin(4, mode=Pin.OUT, value=0)
spi = SPI(1, baudrate=4000000, polarity=0, phase=0,
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

nrf = NRF24L01(spi, csn, ce, payload_size=4)

# --- AJUSTE MAESTRO DE POTENCIA ---
# Valor 0x02 significa:
# - Velocidad: 1 Mbps (Súper estable)
# - Potencia: -12 dBm (Baja corriente -> EVITA REINICIOS)
nrf.reg_write(0x06, 0x02)

# Canal 120 (Limpio de WiFi)
nrf.set_channel(120)

direccion = b'\xe1\xf0\xf0\xf0\xf0'
nrf.open_tx_pipe(direccion)

print("Mando listo. Toca el sensor...")
estado_anterior = -1 

while True:
    try:
        estado_actual = sensor_touch.value()
        
        if estado_actual != estado_anterior:
            # Feedback visual local
            led_wroom.value(estado_actual)
            
            print(f"Enviando: {estado_actual}")
            mensaje = struct.pack("i", estado_actual)
            nrf.send(mensaje)
            
            estado_anterior = estado_actual
            
        time.sleep(0.05)
        
    except OSError:
        # Si da error, parpadeo rápido
        led_wroom.value(0)
        time.sleep(0.05)
        led_wroom.value(1)