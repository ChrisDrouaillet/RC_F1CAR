import struct
import time
from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01

# --- 1. CONFIGURACIÓN DE HARDWARE ---

# LED Integrado (GPIO 8)
led = Pin(8, Pin.OUT)
led.value(1) # Apagado (1=OFF en C3 Super Mini)

# Servo de Dirección (Pin 2) - Configuración Segura
servo = PWM(Pin(2), freq=50)

# Radio nRF24L01 (Pines SPI Hardware)
csn = Pin(7, mode=Pin.OUT, value=1)
ce  = Pin(3, mode=Pin.OUT, value=0)
spi = SPI(1, baudrate=4000000, polarity=0, phase=0, 
          sck=Pin(4), mosi=Pin(6), miso=Pin(5))

nrf = NRF24L01(spi, csn, ce, payload_size=6)

# --- 2. INICIO DE COMUNICACIÓN ---
print("Iniciando Receptor...")

try:
    nrf.reg_write(0x06, 0x07) # Potencia MÁXIMA (0dBm) y 1Mbps
    nrf.set_channel(120)      # Canal 120
    nrf.open_rx_pipe(1, b'\xe1\xf0\xf0\xf0\xf0')
    nrf.start_listening()
    print("Radio OK. Esperando Mando...")
except OSError:
    print("¡ERROR! No se detecta el módulo nRF24L01.")

# --- 3. FUNCIÓN DE MOVIMIENTO (RANGO SEGURO) ---
def mover_servo_seguro(valor_adc):
    # RANGO PROTEGIDO: 40 a 115
    # Evita que el servo golpee los topes mecánicos
    min_safe = 40
    max_safe = 115
    
    # Mapeo matemático
    duty = int(min_safe + (valor_adc / 4095) * (max_safe - min_safe))
    servo.duty(duty)

# --- 4. BUCLE PRINCIPAL ---
while True:
    if nrf.any():
        while nrf.any():
            try:
                buf = nrf.recv()
                # Recibimos: X (Dirección), Y (Motor), B (Botón)
                x, y, b = struct.unpack("HHH", buf)
                
                # A. Mover Dirección
                mover_servo_seguro(x)
                
                # B. Controlar LED
                if b == 0:
                    led.value(0) # Encender
                else:
                    led.value(1) # Apagar
                
                # (Aquí agregaremos el motor C.C. cuando tengas el driver)
                
            except Exception as e:
                pass # Ignorar errores de paquete