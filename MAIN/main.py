# Adaptación del código de ejemplo para MPU6050 Accelerometer/Gyro Module
# para MicroPython en ESP32, centrado en el cálculo de ángulos.
# Envío de datos por Wi-Fi (Servidor TCP)

from MPU6050 import MPU6050 # Asegúrate de que esta librería (MPU6050.py) esté en tu ESP32
from machine import Pin      # Aunque no se use directamente para I2C, se mantiene por si es necesario
from time import sleep_ms
import math                  # Para funciones matemáticas como atan2 y degrees
import network
import socket

# --- Configuración de Wi-Fi ---
# ¡IMPORTANTE! Reemplaza con los datos de tu red compartida por la PC
SSID = 'NAME_SSID' # Tu SSID de la red compartida (Ej. 'MiHotspot')
PASSWORD = 'PASSWORD_NETWORK' # Tu Contraseña de la red compartida
PORT = 8080 # Puerto TCP para la comunicación, debe ser el mismo en el cliente de PC

# Inicializar el objeto MPU6050.
# Esta librería (MPU6050.py) debería manejar la inicialización I2C internamente.
# Si tu MPU6050 no funciona, es posible que los pines I2C por defecto de la librería
# no coincidan con tu hardware. (Comúnmente SDA=GPIO21, SCL=GPIO22 para ESP32)
mpu = MPU6050()

# Variables de conexión globales
sta_if = None
server_sock = None # Este será el socket que escucha las conexiones
client_sock = None # Este será el socket de la conexión activa con un cliente

def connect_wifi():
    """Intenta conectar el ESP32 a la red Wi-Fi especificada."""
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print(f"Conectando a la red Wi-Fi: {SSID}...")
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        timeout = 10 # segundos
        while not sta_if.isconnected() and timeout > 0:
            print(".", end="")
            sleep_ms(1000)
            timeout -= 1
        if sta_if.isconnected():
            print("\nWi-Fi conectado!")
            print('IP Address:', sta_if.ifconfig()[0])
            return True
        else:
            print("\n¡Fallo al conectar a Wi-Fi!")
            return False
    return True # Ya conectado

def setup():
    """
    Función de configuración inicial, similar a setup() en Arduino.
    Configura Wi-Fi, verifica el MPU6050 e inicia el servidor TCP.
    """
    global server_sock # Declarar que modificaremos la variable global

    if not connect_wifi():
        print("No se pudo establecer la conexión Wi-Fi. Reinicia el ESP32.")
        while True: # Bucle infinito para detener la ejecución si no hay Wi-Fi
            sleep_ms(1000)

    print("Iniciando MPU6050 y verificando conexión...")
    try:
        accel = mpu.read_accel_data()
        if not (isinstance(accel, dict) and 'x' in accel):
            raise ValueError("Datos de acelerómetro inesperados.")
        print("MPU6050 conectado correctamente.")
    except Exception as e:
        print(f"Error: MPU6050 no conectado o error de comunicación: {e}")
        print("Asegúrate de que la librería MPU6050.py esté configurada para los pines I2C correctos (ej. SDA=21, SCL=22).")
        while True: # Bucle infinito para indicar que el sensor no está disponible
            sleep_ms(1000)

    # --- Crear y bindear el socket del servidor UNA SOLA VEZ ---
    try:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Permite reusar la dirección rápidamente. Importante para evitar EADDRINUSE después de reinicios.
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(('', PORT)) # Escucha en todas las interfaces en el puerto especificado
        server_sock.listen(1) # Solo una conexión entrante a la vez (cola de 1)
        print(f"Servidor TCP iniciado en el puerto {PORT}. Esperando conexiones...")
    except OSError as e:
        print(f"ERROR al iniciar el servidor TCP: {e}. El puerto puede estar ocupado. Reiniciando...")
        sleep_ms(5000) # Pausa antes de un posible reinicio
        import machine
        machine.reset() # Reinicio forzado si el bind falla

    print("Listo para leer datos y servir por Wi-Fi.")

def loop():
    global client_sock, server_sock # Acceder a las variables globales

    # Si no hay cliente conectado, intenta aceptar una nueva conexión.
    # El accept es no-bloqueante debido al timeout para que el loop pueda continuar.
    if client_sock is None:
        try:
            # print("Esperando nueva conexión de cliente...") # Descomenta para depuración
            server_sock.settimeout(0.1) # Espera 100ms por una conexión
            client_sock, addr = server_sock.accept()
            print(f'Cliente conectado desde: {addr}')
            # Si la conexión fue exitosa, podemos restablecer el timeout a None para el server_sock
            # o mantenerlo con timeout si quieres que el servidor pueda hacer otras cosas.
            # Aquí lo ponemos a None para que el accept bloquee en futuras ocasiones si es necesario.
            # Si tu ESP32 hace otras cosas que no deben bloquear, considera dejar un timeout bajo
            # en el server_sock o hacerlo completamente no-bloqueante y usar select.
            server_sock.settimeout(None)
        except OSError as e:
            # Manejo de errores de accept (ej. timeout EWOULDBLOCK o ETIMEDOUT)
            # AHORA INCLUIMOS 116 (ETIMEDOUT) AQUÍ
            if e.args[0] == 110 or e.args[0] == 116: # EWOULDBLOCK (110) o ETIMEDOUT (116)
                # print("No hay cliente conectado aún, esperando...") # Puedes descomentar para depurar
                pass # No hay cliente, no es un error crítico para el server_sock
            else:
                # Esto es un error crítico para el server_sock, por ejemplo, puerto ya en uso.
                print(f"Error al aceptar conexión (crítico): {e}")
                if server_sock:
                    server_sock.close()
                server_sock = None # Marcar como roto para un posible reinicio en setup()
                sleep_ms(1000)
            return # Si no hay cliente conectado EN ESTE MOMENTO (o error en accept), no enviar datos.

    # Si llegamos aquí, client_sock NO ES None, lo que significa que tenemos un cliente para enviar datos.

    # ... (El resto del código de lectura del MPU6050 y envío de datos permanece igual) ...

    # Leer valores del acelerómetro (ya están en ms^-2 según la librería)
    accel = mpu.read_accel_data()
    ax_ms2 = accel["x"]
    ay_ms2 = accel["y"]
    az_ms2 = accel["z"]

    ax_g = ax_ms2 / 9.81
    ay_g = ay_ms2 / 9.81
    az_g = az_ms2 / 9.81

    ang_x_rad = math.atan2(ay_g, math.sqrt(ax_g*ax_g + az_g*az_g))
    ang_y_rad = math.atan2(-ax_g, math.sqrt(ay_g*ay_g + az_g*az_g))
    ang_z_rad = math.atan2(math.sqrt(ax_g*ax_g + ay_g*ay_g), az_g)

    ang_x_deg = math.degrees(ang_x_rad)
    ang_y_deg = math.degrees(ang_y_rad)
    ang_z_deg = math.degrees(ang_z_rad)

    # Formatear el mensaje:
    msg = (f"Aceleración (m/s²) -> X: {ax_ms2:.3f} Y: {ay_ms2:.3f} Z: {az_ms2:.3f} | "
           f"Ángulos (grados) -> X: {ang_x_deg:.1f} Y: {ang_y_deg:.1f} Z: {ang_z_deg:.1f}\n")

    try:
        client_sock.sendall(msg.encode('utf-8'))
        # print(f"DEBUG: Dato enviado: {msg.strip()[:50]}...") # Para depuración en serial
    except OSError as e:
        print(f"Error al enviar datos: {e}. Cliente desconectado.")
        if client_sock:
            client_sock.close()
        client_sock = None # Marcar que no hay cliente conectado para que acepte uno nuevo en la próxima iteración

    sleep_ms(500) # Pausa entre envíos de datos

# Ejecutar la función de configuración una vez, y luego el bucle principal continuamente.
if __name__ == "__main__":
    setup()
    while True:
        loop()
