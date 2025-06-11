import flet as ft
import socket
import threading
import time
import re
from collections import deque
import matplotlib.pyplot as plt
import io
import base64
import csv

# --- Configuración de Conexión Wi-Fi ---
# ¡IMPORTANTE! Reemplaza con la IP que tu ESP32 muestra en el monitor serial
ESP32_IP = '192.168.137.108' # Ejemplo: '192.168.137.1' si tu PC comparte la red
PORT = 8080 # Debe coincidir con el puerto del ESP32
socket_connection = None
stop_event = threading.Event()

# --- Deques para almacenar los últimos N puntos de datos ---
MAX_DATA_POINTS = 150 # Número máximo de puntos a mostrar en el gráfico
accel_x_data = deque(maxlen=MAX_DATA_POINTS)
accel_y_data = deque(maxlen=MAX_DATA_POINTS)
accel_z_data = deque(maxlen=MAX_DATA_POINTS)
ang_x_data = deque(maxlen=MAX_DATA_POINTS)
ang_y_data = deque(maxlen=MAX_DATA_POINTS)
ang_z_data = deque(maxlen=MAX_DATA_POINTS)

# --- Expresión regular para parsear la línea de datos ---
# Adaptada al formato de mensaje del ESP32: "Aceleración (m/s²) -> X: ... Z: ... | Ángulos (grados) -> X: ... Z: ..."
data_pattern = re.compile(
    r"Aceleración \(m/s²\) -> X:\s*([+-]?\d+\.\d+)\s*Y:\s*([+-]?\d+\.\d+)\s*Z:\s*([+-]?\d+\.\d+)\s*\|"
    r"\s*Ángulos \(grados\) -> X:\s*([+-]?\d+\.\d+)\s*Y:\s*([+-]?\d+\.\d+)\s*Z:\s*([+-]?\d+\.\d+)"
)

def create_plot_image(x_data, y_data, x_label, y_label, title):
    """Crea un gráfico de Matplotlib y lo devuelve como imagen base64."""
    plt.clf()
    plt.plot(x_data, y_data)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

def create_placeholder_image():
    """Crea una imagen de Matplotlib con texto de marcador de posición."""
    plt.clf()
    plt.text(0.5, 0.5, "Esperando datos...", ha='center', va='center')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def read_from_wifi(page: ft.Page, image_x: ft.Image, image_y: ft.Image, image_z: ft.Image, status_text: ft.Text, save_button: ft.ElevatedButton):
    """
    Función que se ejecuta en un hilo separado para leer datos del socket Wi-Fi.
    """
    global socket_connection
    buffer = b'' # Buffer para almacenar datos parciales

    if ESP32_IP == '192.168.XXX.XXX':
        status_text.value = "ERROR: ¡Por favor, actualiza ESP32_IP con la dirección IP de tu ESP32!"
        page.update()
        return

    try:
        status_text.value = f"Conectando a ESP32 ({ESP32_IP}:{PORT})..."
        page.update()

        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_connection.connect((ESP32_IP, PORT))
        socket_connection.settimeout(0.5) # Pequeño timeout para no bloquear indefinidamente

        status_text.value = f"Conectado a ESP32 ({ESP32_IP}:{PORT})"
        page.update()
        print(f"Conectado a ESP32 en {ESP32_IP}:{PORT}")

        while not stop_event.is_set():
            try:
                data = socket_connection.recv(128) # Leer hasta 128 bytes
                if not data: # Si no hay datos, el socket se cerró en el otro extremo
                    raise ConnectionError("Conexión perdida con ESP32.")

                buffer += data
                
                # Procesar líneas completas del buffer
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    line_str = line.decode('utf-8').strip()
                    print(f"Recibido: {line_str}") # Para depuración

                    match = data_pattern.search(line_str)
                    if match:
                        try:
                            accel_x = float(match.group(1))
                            accel_y = float(match.group(2))
                            accel_z = float(match.group(3))
                            ang_x = float(match.group(4))
                            ang_y = float(match.group(5))
                            ang_z = float(match.group(6))

                            print(f"Parsed data: Accel X={accel_x}, Y={accel_y}, Z={accel_z}, Ang X={ang_x}, Y={ang_y}, Z={ang_z}")

                            accel_x_data.append(accel_x)
                            accel_y_data.append(accel_y)
                            accel_z_data.append(accel_z)
                            ang_x_data.append(ang_x)
                            ang_y_data.append(ang_y)
                            ang_z_data.append(ang_z)

                            # Actualizar UI en el hilo principal de Flet
                            def update_ui_from_data():
                                if accel_x_data: # Solo si hay datos
                                    # Asumiendo 0.5 segundos por muestra del ESP32
                                    time_elapsed = [i * 0.5 for i in range(len(accel_x_data))] 

                                    image_x.src_base64 = create_plot_image(time_elapsed, list(accel_x_data), "Tiempo (s)", "Acc X (m/s²)", "Aceleración X")
                                    image_y.src_base64 = create_plot_image(time_elapsed, list(accel_y_data), "Tiempo (s)", "Acc Y (m/s²)", "Aceleración Y")
                                    image_z.src_base64 = create_plot_image(time_elapsed, list(accel_z_data), "Tiempo (s)", "Acc Z (m/s²)", "Aceleración Z")
                                    
                                    # Opcional: Si quieres mostrar ángulos también, puedes añadir más gráficos
                                    # O incluso un solo gráfico con varias líneas, o solo actualizar el status_text
                                    
                                    status_text.value = f"Últimos datos: {line_str}"
                                    save_button.disabled = False
                                page.update()

                            # Ejecutar actualización de UI en el contexto del bucle de eventos de Flet
                            update_ui_from_data()

                        except ValueError as e:
                            print(f"Error al convertir datos: {e} en línea: {line_str}")
                    else:
                        print(f"Línea no coincide con el patrón: {line_str}") # Para depuración

            except socket.timeout:
                pass # No hay datos en este momento, sigue intentando
            except ConnectionError as e:
                status_text.value = f"Error de conexión: {e}. Reintentando..."
                page.update()
                print(f"Error de conexión: {e}")
                socket_connection.close()
                socket_connection = None
                # Intentar reconectar
                while not stop_event.is_set():
                    try:
                        socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        socket_connection.connect((ESP32_IP, PORT))
                        socket_connection.settimeout(0.5)
                        status_text.value = f"Reconectado a ESP32 ({ESP32_IP}:{PORT})"
                        page.update()
                        print(f"Reconectado a ESP32 en {ESP32_IP}:{PORT}")
                        break # Sale del bucle de reintento
                    except (socket.error, ConnectionRefusedError) as re_e:
                        # print(f"Reintento de conexión fallido: {re_e}")
                        time.sleep(1) # Esperar antes de reintentar
                if stop_event.is_set():
                    break # Salir si se ha solicitado detener

            except Exception as e:
                status_text.value = f"Error inesperado al leer: {e}"
                page.update()
                print(f"Error inesperado al leer: {e}")
                break # Salir del bucle en caso de error grave

    except (socket.error, ConnectionRefusedError) as e:
        status_text.value = f"Error de conexión inicial: {e}. Asegúrate de que el ESP32 esté encendido y la IP sea correcta."
        page.update()
        print(f"Error de conexión inicial: {e}")
    except Exception as e:
        status_text.value = f"Error inesperado al iniciar conexión: {e}"
        page.update()
        print(f"Error inesperado al iniciar conexión: {e}")
    finally:
        if socket_connection:
            socket_connection.close()
            print("Conexión de socket cerrada.")
        status_text.value = "Desconectado de Wi-Fi."
        page.update()
        socket_connection = None


def main(page: ft.Page):
    page.title = "Visualizador MPU6050 Wi-Fi Flet"
    page.vertical_alignment = ft.CrossAxisAlignment.START
    page.window_width = 1000 # Aumentado para mejor visualización de 3 gráficos
    page.window_height = 700

    status_text = ft.Text("Esperando conexión Wi-Fi...", size=16, weight=ft.FontWeight.BOLD)

    image_x = ft.Image(src_base64="", expand=True)
    image_y = ft.Image(src_base64="", expand=True)
    image_z = ft.Image(src_base64="", expand=True)

    start_button = ft.ElevatedButton(
        "Iniciar Wi-Fi",
        icon=ft.Icons.WIFI,
        on_click=lambda e: (start_wifi_reading_thread(page, image_x, image_y, image_z, status_text, save_button),
                            setattr(e.control, 'disabled', True),
                            setattr(page.controls[0].controls[1].controls[1], 'disabled', False), # Habilita el botón de detener
                            page.update())
    )
    stop_button = ft.ElevatedButton(
        "Detener Wi-Fi",
        icon=ft.Icons.STOP,
        on_click=lambda e: (stop_wifi_reading(e),
                            setattr(e.control, 'disabled', True),
                            setattr(page.controls[0].controls[1].controls[0], 'disabled', False), # Habilita el botón de iniciar
                            page.update()),
        disabled=True
    )

    def save_data(e):
        filename = "sensor_data_wifi.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Tiempo (s)", "Acc X (m/s^2)", "Acc Y (m/s^2)", "Acc Z (m/s^2)", "Ang X (deg)", "Ang Y (deg)", "Ang Z (deg)"])
            time_elapsed = [i * 0.5 for i in range(len(accel_x_data))] # Asumiendo 0.5 segundos por muestra del ESP32
            for i in range(len(accel_x_data)):
                writer.writerow([time_elapsed[i], accel_x_data[i], accel_y_data[i], accel_z_data[i], ang_x_data[i], ang_y_data[i], ang_z_data[i]])
        status_text.value = f"Datos guardados en {filename}"
        page.update()

    save_button = ft.ElevatedButton(
        "Guardar Datos",
        icon=ft.Icons.SAVE,
        on_click=save_data,
        disabled=True
    )

    page.add(
        ft.Column(
            [
                ft.Row([ft.Text("Captura de Movimiento MPU6050 por Wi-Fi", size=18, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([start_button, stop_button, save_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                ft.Row([status_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row(
                    [
                        # Gráficos de aceleración
                        ft.Container(content=image_x, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.Colors.BLACK38)),
                        ft.Container(content=image_y, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.Colors.BLACK38)),
                        ft.Container(content=image_z, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.Colors.BLACK38)),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                # Puedes añadir más filas para los gráficos de ángulo si los necesitas visibles
                # ft.Row(
                #     [
                #         ft.Container(content=image_ang_x, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.colors.BLACK38)),
                #         ft.Container(content=image_ang_y, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.colors.BLACK38)),
                #         ft.Container(content=image_ang_z, padding=ft.padding.all(5), expand=True, border=ft.border.all(1, ft.colors.BLACK38)),
                #     ],
                #     vertical_alignment=ft.CrossAxisAlignment.START,
                # ),
            ],
            expand=True,
        )
    )

    page.on_disconnect = lambda e: stop_event.set()


def start_wifi_reading_thread(page: ft.Page, image_x: ft.Image, image_y: ft.Image, image_z: ft.Image, status_text: ft.Text, save_button: ft.ElevatedButton):
    """Inicia el hilo para la lectura Wi-Fi."""
    accel_x_data.clear()
    accel_y_data.clear()
    accel_z_data.clear()
    ang_x_data.clear()
    ang_y_data.clear()
    ang_z_data.clear()

    image_x.src_base64 = create_placeholder_image()
    image_y.src_base64 = create_placeholder_image()
    image_z.src_base64 = create_placeholder_image()
    page.update()

    save_button.disabled = True
    page.update()

    stop_event.clear()
    wifi_thread = threading.Thread(target=read_from_wifi, args=(page, image_x, image_y, image_z, status_text, save_button), daemon=True)
    wifi_thread.start()

def stop_wifi_reading(e: ft.ControlEvent):
    """Detiene el hilo de lectura Wi-Fi."""
    stop_event.set()


if __name__ == "__main__":
    # Necesitas instalar flet:
    # pip install flet
    ft.app(target=main)