# Adaptación del código de ejemplo para MPU6050 Accelerometer/Gyro Module
# para MicroPython en ESP32, centrado en el cálculo de ángulos.

from MPU6050 import MPU6050 # Asegúrate de que esta librería (MPU6050.py) esté en tu ESP32
from machine import Pin     # Aunque no se use directamente para I2C, se mantiene por si es necesario
from time import sleep_ms
import math                 # Para funciones matemáticas como atan2 y degrees

# Inicializar el objeto MPU6050.
# Esta librería (MPU6050.py) debería manejar la inicialización I2C internamente.
# Si tu MPU6050 no funciona, es posible que los pines I2C por defecto de la librería
# no coincidan con tu hardware. (Comúnmente SDA=GPIO21, SCL=GPIO22 para ESP32)
mpu = MPU6050()

def setup():
    """
    Función de configuración inicial, similar a setup() en Arduino.
    """
    print("Iniciando MPU6050 y verificando conexión...")

    # Aunque la librería no tiene un 'testConnection' explícito en el ejemplo,
    # intentaremos leer datos para ver si hay errores, o puedes añadir una comprobación
    # si la librería MPU6050.py ofrece una. Por ahora, asumimos que si se puede leer, está conectado.
    try:
        accel = mpu.read_accel_data()
        if not (isinstance(accel, dict) and 'x' in accel):
            # Si no es un diccionario o le faltan claves, podría ser un problema de conexión
            raise ValueError("Datos de acelerómetro inesperados.")
        print("MPU6050 conectado correctamente.")
    except Exception as e:
        print(f"Error: MPU6050 no conectado o error de comunicación: {e}")
        print("Asegúrate de que la librería MPU6050.py esté configurada para los pines I2C correctos (ej. SDA=21, SCL=22).")
        while True: # Bucle infinito para indicar que el sensor no está disponible
            sleep_ms(1000) # Pausa para no saturar el serial

    # Tu código original tenía setFullScaleAccelRange.
    # Esta librería (MPU6050.py) no expone esa función directamente en el ejemplo.
    # Asumimos que los valores de read_accel_data() ya están escalados a ms^-2.
    # Si necesitas cambiar el rango, tendrías que modificar la librería MPU6050.py.

    print("Listo para leer datos.")

def loop():
    """
    Bucle principal de ejecución, similar a loop() en Arduino.
    """
    # Leer valores del acelerómetro (ya están en ms^-2 según la librería)
    accel = mpu.read_accel_data()
    ax_ms2 = accel["x"]
    ay_ms2 = accel["y"]
    az_ms2 = accel["z"]

    # Leer temperatura (comentada en tu ejemplo original, pero disponible)
    # temp_celsius = mpu.read_temperature()

    # Cálculo de ángulos usando los valores de aceleración en ms^-2
    # Convertimos a 'g' para mantener la lógica original de tu código, aunque no es estrictamente necesario
    # para atan2 si las unidades son consistentes. Aquí dividimos por 9.81 para obtener "g".
    ax_g = ax_ms2 / 9.81
    ay_g = ay_ms2 / 9.81
    az_g = az_ms2 / 9.81

    # Cálculo de ángulos (en radianes inicialmente)
    # Utilizamos el módulo 'math' para las funciones matemáticas
    ang_x_rad = math.atan2(ay_g, math.sqrt(ax_g*ax_g + az_g*az_g))
    ang_y_rad = math.atan2(-ax_g, math.sqrt(ay_g*ay_g + az_g*az_g)) # Nota: Es común usar -ax para ang_y en algunos sistemas de coordenadas
    ang_z_rad = math.atan2(math.sqrt(ax_g*ax_g + ay_g*ay_g), az_g) # Este ángulo z a menudo es el 'pitch' o 'roll' si no se usa giroscopio

    # Convertir a grados
    ang_x_deg = math.degrees(ang_x_rad)
    ang_y_deg = math.degrees(ang_y_rad)
    ang_z_deg = math.degrees(ang_z_rad)

    # Mostrar los valores en el monitor serial
    # Usamos f-strings para un formato más legible (Python 3.6+ y MicroPython reciente)
    print(f"Aceleración (m/s²) -> X: {ax_ms2:.3f} Y: {ay_ms2:.3f} Z: {az_ms2:.3f} | "
          f"Ángulos (grados) -> X: {ang_x_deg:.1f} Y: {ang_y_deg:.1f} Z: {ang_z_deg:.1f}")
    # print(f"Temperatura: {temp_celsius:.2f}°C") # Descomenta para ver la temperatura

    # Pausa de 500 milisegundos
    sleep_ms(500)

# Ejecutar la función de configuración una vez, y luego el bucle principal continuamente.
if __name__ == "__main__":
    setup()
    while True:
        loop()
