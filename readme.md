# Motion Capture System with MPU6050 and Flet Interface

## Overview

This project implements a motion capture system using the MPU6050 accelerometer/gyroscope sensor and displays the data in a user-friendly interface built with Flet. The system consists of three main components:

1.  **ESP32 Microcontroller Code (main.py):** Reads data from the MPU6050 sensor and transmits it over serial communication.
2.  **MPU6050 Library (MPU6050.py):** Provides an interface to interact with the MPU6050 sensor, handling I2C communication and data conversion.
3.  **Flet User Interface (INTERFAZ.PY):** Receives data from the serial port, parses it, and plots the accelerometer data in real-time using Matplotlib.

## Visuals

### Interface Image
![image](https://github.com/user-attachments/assets/b7807df8-7a22-4a14-b04e-db381ee217d2)


### Device Image
![image](https://github.com/user-attachments/assets/6691689e-d091-43c1-a58b-73e041c0b561)


## Code Description

### 1. ESP32 Microcontroller Code (main.py)

*   **Purpose:** This code runs on the ESP32 microcontroller and is responsible for initializing the MPU6050 sensor, reading accelerometer data, calculating angles, and sending the data to the serial port.
*   **Key Features:**
    *   Initializes the MPU6050 sensor using the `MPU6050.py` library.
    *   Reads accelerometer data in m/s².
    *   Calculates angles from accelerometer data.
    *   Transmits the data over serial communication for visualization.
*   **Dependencies:**
    *   `MPU6050.py` library.
    *   `machine` module for pin control.
    *   `time` module for delays.
    *   `math` module for mathematical functions.

### 2. MPU6050 Library (MPU6050.py)

*   **Purpose:** This library provides an abstraction layer for interacting with the MPU6050 sensor over the I2C protocol.
*   **Key Features:**
    *   Initializes the I2C communication.
    *   Reads raw accelerometer and gyroscope data.
    *   Converts raw data to meaningful units (g or m/s² for accelerometer, deg/s for gyroscope).
    *   Provides methods to set and get accelerometer and gyroscope ranges.
*   **Dependencies:**
    *   `machine` module for I2C communication.
    *   `time` module for delays.
    *   `math` module for mathematical functions.

### 3. Flet User Interface (INTERFAZ.PY)

*   **Purpose:** This code creates a graphical user interface using the Flet framework to visualize the accelerometer data received from the ESP32.
*   **Key Features:**
    *   Connects to the serial port and reads incoming data.
    *   Parses the data string to extract accelerometer values.
    *   Plots the accelerometer data in real-time using Matplotlib.
    *   Allows the user to start/stop data acquisition and save the data to a CSV file.
*   **Dependencies:**
    *   `flet` module for creating the user interface.
    *   `serial` module for serial communication.
    *   `threading` module for handling serial reading in a separate thread.
    *   `time` module for delays.
    *   `re` module for regular expressions (data parsing).
    *   `collections` module for the `deque` data structure.
    *   `matplotlib` module for plotting.
    *   `io` and `base64` modules for image handling.
    *   `csv` module for saving data to a CSV file.

## Spanish Section

## Visión General

Este proyecto implementa un sistema de captura de movimiento utilizando el sensor acelerómetro/giroscopio MPU6050 y muestra los datos en una interfaz fácil de usar construida con Flet. El sistema consta de tres componentes principales:

1.  **Código del Microcontrolador ESP32 (main.py):** Lee los datos del sensor MPU6050 y los transmite a través de la comunicación serial.
2.  **Librería MPU6050 (MPU6050.py):** Proporciona una interfaz para interactuar con el sensor MPU6050, manejando la comunicación I2C y la conversión de datos.
3.  **Interfaz de Usuario Flet (INTERFAZ.PY):** Recibe datos del puerto serial, los analiza y grafica los datos del acelerómetro en tiempo real utilizando Matplotlib.

## Elementos Visuales

### Imagen de la Interfaz

[Espacio para la Imagen de la Interfaz]

### Imagen del Dispositivo

[Espacio para la Imagen del Dispositivo]

## Descripción del Código

### 1. Código del Microcontrolador ESP32 (main.py)

*   **Propósito:** Este código se ejecuta en el microcontrolador ESP32 y es responsable de inicializar el sensor MPU6050, leer los datos del acelerómetro, calcular los ángulos y enviar los datos al puerto serial.
*   **Características Clave:**
    *   Inicializa el sensor MPU6050 utilizando la librería `MPU6050.py`.
    *   Lee los datos del acelerómetro en m/s².
    *   Calcula los ángulos a partir de los datos del acelerómetro.
    *   Transmite los datos a través de la comunicación serial para su visualización.
*   **Dependencias:**
    *   Librería `MPU6050.py`.
    *   Módulo `machine` para el control de pines.
    *   Módulo `time` para los retrasos.
    *   Módulo `math` para las funciones matemáticas.

### 2. Librería MPU6050 (MPU6050.py)

*   **Propósito:** Esta librería proporciona una capa de abstracción para interactuar con el sensor MPU6050 a través del protocolo I2C.
*   **Características Clave:**
    *   Inicializa la comunicación I2C.
    *   Lee los datos brutos del acelerómetro y del giroscopio.
    *   Convierte los datos brutos en unidades significativas (g o m/s² para el acelerómetro, deg/s para el giroscopio).
    *   Proporciona métodos para establecer y obtener los rangos del acelerómetro y del giroscopio.
*   **Dependencias:**
    *   Módulo `machine` para la comunicación I2C.
    *   Módulo `time` para los retrasos.
    *   Módulo `math` para las funciones matemáticas.

### 3. Interfaz de Usuario Flet (INTERFAZ.PY)

*   **Propósito:** Este código crea una interfaz gráfica de usuario utilizando el framework Flet para visualizar los datos del acelerómetro recibidos desde el ESP32.
*   **Características Clave:**
    *   Se conecta al puerto serial y lee los datos entrantes.
    *   Analiza la cadena de datos para extraer los valores del acelerómetro.
    *   Grafica los datos del acelerómetro en tiempo real utilizando Matplotlib.
    *   Permite al usuario iniciar/detener la adquisición de datos y guardar los datos en un archivo CSV.
*   **Dependencias:**
    *   Módulo `flet` para crear la interfaz de usuario.
    *   Módulo `serial` para la comunicación serial.
    *   Módulo `threading` para manejar la lectura serial en un hilo separado.
    *   Módulo `time` para los retrasos.
    *   Módulo `re` para las expresiones regulares (análisis de datos).
    *   Módulo `collections` para la estructura de datos `deque`.
    *   Módulo `matplotlib` para la graficación.
    *   Módulos `io` y `base64` para el manejo de imágenes.
    *   Módulo `csv` para guardar los datos en un archivo CSV.
