import flet as ft
import serial
import threading
import time
import re
from collections import deque
import matplotlib.pyplot as plt
import io
import base64
import csv

# --- Configuración del Puerto Serial ---
SERIAL_PORT = 'COM11'
BAUD_RATE = 115200  # Asegúrate de que coincida con la velocidad de tu ESP32
serial_connection = None
stop_event = threading.Event()

# --- Deques para almacenar los últimos N puntos de datos ---
MAX_DATA_POINTS = 50 # Número máximo de puntos a mostrar en el gráfico
accel_x_data = deque(maxlen=MAX_DATA_POINTS)
accel_y_data = deque(maxlen=MAX_DATA_POINTS)
accel_z_data = deque(maxlen=MAX_DATA_POINTS)

# --- Expresión regular para parsear la línea de datos ---
# Busca "Aceleración ... Ángulos ..." dentro de la línea
data_pattern = re.compile(
    r"Aceleración \(m/s²\) -> X:\s*([+-]?\d+\.\d+)\s*Y:\s*([+-]?\d+\.\d+)\s*Z:\s*([+-]?\d+\.\d+)\s*\|"
    r"\s*Ángulos \(grados\) -> X:\s*([+-]?\d+\.\d+)\s*Y:\s*([+-]?\d+\.\d+)\s*Z:\s*([+-]?\d+\.\d+)"
)

def read_from_serial(page: ft.Page, image_x: ft.Image, image_y: ft.Image, image_z: ft.Image, status_text: ft.Text, save_button: ft.ElevatedButton):
    """
    Función que se ejecuta en un hilo separado para leer datos del puerto serial.
    """
    global serial_connection

    try:
        serial_connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        status_text.value = f"Conectado a {SERIAL_PORT} @ {BAUD_RATE} bps"
        page.update()
        print(f"Conectado a {SERIAL_PORT}")

        start_time = time.time()  # Record the start time

        while not stop_event.is_set():
            if serial_connection.in_waiting > 0:
                line = serial_connection.readline().decode('utf-8').strip()
                # print(f"Recibido: {line}") # Para depuración

                match = data_pattern.search(line)
                if match:
                    try:
                        accel_x = float(match.group(1))
                        accel_y = float(match.group(2))
                        accel_z = float(match.group(3))

                        accel_x_data.append(accel_x)
                        accel_y_data.append(accel_y)
                        accel_z_data.append(accel_z)

                        # --- Crear y actualizar los gráficos de Matplotlib ---
                        def create_plot_image(x_data, y_data, x_label, y_label, title):
                            plt.clf()  # Limpiar la figura anterior
                            plt.plot(x_data, y_data)
                            plt.xlabel(x_label)
                            plt.ylabel(y_label)
                            plt.title(title)

                            # Convertir el gráfico a una imagen PNG
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png')
                            buf.seek(0)
                            return base64.b64encode(buf.read()).decode('utf-8')

                        # Calculate time elapsed for x-axis
                        time_elapsed = [i * 0.15 for i in range(len(accel_x_data))]  # Assuming 0.15 seconds per sample

                        # Update images
                        image_x.src_base64 = create_plot_image(time_elapsed, list(accel_x_data), "Tiempo (s)", "Aceleración X (m/s^2)", "Gráfico de Aceleración X")
                        image_y.src_base64 = create_plot_image(time_elapsed, list(accel_y_data), "Tiempo (s)", "Aceleración Y (m/s^2)", "Gráfico de Aceleración Y")
                        image_z.src_base64 = create_plot_image(time_elapsed, list(accel_z_data), "Tiempo (s)", "Aceleración Z (m/s^2)", "Gráfico de Aceleración Z")

                        page.update()  # Actualiza la UI
                        status_text.value = f"Últimos datos: {line}"
                        page.update()

                        save_button.disabled = False
                        page.update()

                    except ValueError as e:
                        print(f"Error al convertir datos: {e} en línea: {line}")
                else:
                    # print(f"Línea no coincide con el patrón: {line}") # Para depuración
                    pass  # La línea no es de datos de aceleración

            time.sleep(0.15)  # Pequeña pausa para no saturar el CPU

    except serial.SerialException as e:
        status_text.value = f"Error serial: {e}. Asegúrate de que el puerto COM esté libre y sea el correcto."
        page.update()
        print(f"Error serial: {e}")
    except Exception as e:
        status_text.value = f"Error inesperado: {e}"
        page.update()
        print(f"Error inesperado: {e}")
    finally:
        if serial_connection and serial_connection.is_open:
            serial_connection.close()
            print("Conexión serial cerrada.")
        status_text.value = f"Desconectado del puerto serial."
        page.update()


def main(page: ft.Page):
    page.title = "Proyecto Final Captura de movimiento mediante acelerometría"  # "Visualizador de Aceleración ESP32"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    page.window_width = 800
    page.window_height = 600

    # --- Elementos de la UI ---
    status_text = ft.Text("Esperando conexión al puerto serial...", size=16, weight=ft.FontWeight.BOLD) # "Esperando conexión al puerto serial..."

    # --- Controles de imagen para los gráficos ---
    image_x = ft.Image(src_base64="", expand=True)
    image_y = ft.Image(src_base64="", expand=True)
    image_z = ft.Image(src_base64="", expand=True)

    # Botones para iniciar/detener
    def start_reading(e):
        start_serial_reading(e, page, image_x, image_y, image_z, status_text, save_button)

    start_button = ft.ElevatedButton(
        "Iniciar Lectura", # "Iniciar Lectura"
        icon=ft.icons.PLAY_ARROW,
        on_click=start_reading
    )
    stop_button = ft.ElevatedButton(
        "Detener Lectura", # "Detener Lectura"
        icon=ft.icons.STOP,
        on_click=lambda e: stop_serial_reading(e, page, image_x, image_y, image_z, status_text),
        disabled=True # Deshabilitado al inicio
    )

    def save_data(e):
        # Save data to CSV file
        filename = "sensor_data.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Tiempo (s)", "Aceleración X (m/s^2)", "Aceleración Y (m/s^2)", "Aceleración Z (m/s^2)"])
            time_elapsed = [i * 0.15 for i in range(len(accel_x_data))]
            for i in range(len(accel_x_data)):
                writer.writerow([time_elapsed[i], accel_x_data[i], accel_y_data[i], accel_z_data[i]])
        status_text.value = f"Data saved to {filename}"
        page.update()

    save_button = ft.ElevatedButton(
        "Guardar Datos", # "Guardar Datos"
        icon=ft.icons.SAVE,
        on_click=save_data,
        disabled=True
    )

    page.add(
        ft.Column(
            [
                ft.Row([ft.Text("Captura de Movimiento Mediante Acelerometria", size=12, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER), # "Visualizador de Aceleración del ESP32"
                ft.Row([start_button, stop_button, save_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Row([status_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(
                    [
                        ft.Container(
                            content=image_x,
                            padding=ft.padding.all(10),
                            expand=True,
                            width=page.window_width / 3,  # 1/3 de la pantalla
                            border=ft.border.all(1, ft.colors.BLACK38),
                        ),
                        ft.Container(
                            content=image_y,
                            padding=ft.padding.all(10),
                            expand=True,
                            width=page.window_width / 3,  # 1/3 de la pantalla
                            border=ft.border.all(1, ft.colors.BLACK38),
                        ),
                        ft.Container(
                            content=image_z,
                            padding=ft.padding.all(10),
                            expand=True,
                            width=page.window_width / 3,  # 1/3 de la pantalla
                            border=ft.border.all(1, ft.colors.BLACK38),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            expand=True, # Permite que la columna principal se expanda
        )
    )

    # Al cerrar la ventana, asegúrate de detener el hilo serial
    page.on_disconnect = lambda e: stop_event.set()


def start_serial_reading(e: ft.ControlEvent, page: ft.Page, image_x: ft.Image, image_y: ft.Image, image_z: ft.Image, status_text: ft.Text, save_button: ft.ElevatedButton):
    """Inicia el hilo de lectura serial."""
    global serial_connection
    if serial_connection and serial_connection.is_open:
        print("Ya hay una conexión serial activa.")
        return

    # Limpiar datos previos
    accel_x_data.clear()
    accel_y_data.clear()
    accel_z_data.clear()

    # Initialize images with a placeholder
    def create_placeholder_image():
        plt.clf()
        plt.text(0.5, 0.5, "Esperando datos...", ha='center', va='center')
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    image_x.src_base64 = create_placeholder_image()
    image_y.src_base64 = create_placeholder_image()
    image_z.src_base64 = create_placeholder_image()
    page.update()

    save_button.disabled = True
    page.update()

    stop_event.clear() # Asegura que el evento de parada esté limpio
    serial_thread = threading.Thread(target=read_from_serial, args=(page, image_x, image_y, image_z, status_text, save_button), daemon=True)
    serial_thread.start()
    e.control.disabled = True # Deshabilita el botón de iniciar
    page.controls[0].controls[1].controls[1].disabled = False # Habilita el botón de detener
    page.update()

def stop_serial_reading(e: ft.ControlEvent, page: ft.Page, image_x: ft.Image, image_y: ft.Image, image_z: ft.Image, status_text: ft.Text):
    """Detiene el hilo de lectura serial.""" # "Detiene el hilo de lectura serial."
    stop_event.set() # Señaliza al hilo para que se detenga
    e.control.disabled = True # Deshabilita el botón de detener
    page.controls[0].controls[1].controls[0].disabled = False # Habilita el botón de iniciar
    page.update()

# Ejecuta la aplicación Flet
if __name__ == "__main__":
    # Necesitas instalar flet y pyserial:
    # pip install flet pyserial

    # Asegúrate de que el puerto COM11 sea correcto y esté disponible.
    # En Windows, puede que necesites un controlador CH340 para tu ESP32.
    # En Linux/macOS, los puertos suelen ser /dev/ttyUSB0 o /dev/tty.SLAB_USBtoUART
    # Revisa la salida de tu IDE de Arduino o de un gestor de dispositivos para confirmar el puerto.

    ft.app(target=main)