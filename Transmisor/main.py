import struct
import time
from machine import Pin, ADC, SPI
from nrf24l01 import NRF24L01

# --- CONFIGURACIÓN DE HARDWARE ---
csn = Pin(5, mode=Pin.OUT, value=1)
ce  = Pin(4, mode=Pin.OUT, value=0)

# Joystick (Calibrado a 3.3V)
joy_x = ADC(Pin(34))
joy_y = ADC(Pin(35)) # Lo enviamos de una vez para cuando pongas el motor
joy_btn = Pin(32, mode=Pin.IN, pull=Pin.PULL_UP)

joy_x.atten(ADC.ATTN_11DB)
joy_y.atten(ADC.ATTN_11DB)

# NRF24L01 (SPI Hardware)
spi = SPI(1, baudrate=4000000, polarity=0, phase=0, 
          sck=Pin(18), mosi=Pin(23), miso=Pin(19))

# Payload = 6 bytes (2 bytes X + 2 bytes Y + 2 bytes Botón)
nrf = NRF24L01(spi, csn, ce, payload_size=6)

# Configuración de Radio
nrf.reg_write(0x06, 0x07) # Potencia MÁXIMA (0dBm) y 1Mbps
nrf.set_channel(120)
nrf.open_tx_pipe(b'\xe1\xf0\xf0\xf0\xf0')

print("Mando listo. Enviando datos...")

while True:
    try:
        # 1. Leer sensores
        x = joy_x.read()
        y = joy_y.read()
        b = joy_btn.value() # 1=Suelto, 0=Presionado
        
        # 2. Empaquetar (H = entero de 2 bytes)
        # Enviamos: Eje X, Eje Y, Estado Botón
        paquete = struct.pack("HHH", x, y, b)
        
        # 3. Enviar
        nrf.send(paquete)
        
        # Debug (Opcional: comenta esta línea si va muy lento)
        # print(f"TX -> X:{x} Y:{y} Btn:{b}")
        
    except OSError:
        pass # Ignorar errores puntuales de envío
        
    time.sleep(0.02) # ~50 veces por segundo (muy fluido)