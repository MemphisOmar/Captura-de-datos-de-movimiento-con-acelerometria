# Motion Capture System with MPU6050, Wi-Fi, and Flet Interface

## Overview

This project implements a motion capture system using the MPU6050 accelerometer/gyroscope sensor. It transmits data over Wi-Fi to a user-friendly interface built with Flet, which visualizes the data in real-time using Matplotlib. This project demonstrates a basic data pipeline, showcasing data acquisition, transmission, and visualization, relevant to data science applications.

The system consists of three main components:

1.  **ESP32 Microcontroller Code (main.py):** Reads data from the MPU6050 sensor and transmits it over Wi-Fi using TCP sockets.
2.  **MPU6050 Library (MPU6050.py):** Provides an interface to interact with the MPU6050 sensor, handling I2C communication and data conversion.
3.  **Flet User Interface (INTERFAZ.PY):** Receives data from the ESP32 over Wi-Fi, parses it, and plots the accelerometer data in real-time using Matplotlib.

## Visuals

### Interface Image
![image](https://github.com/user-attachments/assets/76c9582a-e2e1-47ce-8abf-77b0868832f7)



### Device Image
![image](https://github.com/user-attachments/assets/fc04ca9f-d922-47c6-9e9f-e91a62d0ea55)



## Code Description

### 1. ESP32 Microcontroller Code (main.py)

*   **Purpose:** This code runs on the ESP32 microcontroller and is responsible for initializing the MPU6050 sensor, reading accelerometer data, calculating angles, and sending the data over Wi-Fi using TCP sockets.
*   **Key Features:**
    *   Initializes the MPU6050 sensor using the `MPU6050.py` library.
    *   Reads accelerometer data in m/s².
    *   Calculates angles from accelerometer data.
    *   Transmits the data over Wi-Fi using TCP sockets for visualization.
*   **Dependencies:**
    *   `MPU6050.py` library.
    *   `machine` module for pin control.
    *   `time` module for delays.
    *   `math` module for mathematical functions.
    *   `network` module for Wi-Fi connectivity.
    *   `socket` module for TCP communication.

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

*   **Purpose:** This code creates a graphical user interface using the Flet framework to visualize the accelerometer data received from the ESP32 over Wi-Fi.
*   **Key Features:**
    *   Connects to the ESP32 over Wi-Fi and reads incoming data.
    *   Parses the data string to extract accelerometer values and angles.
    *   Plots the accelerometer data and angles in real-time using Matplotlib.
    *   Allows the user to start/stop data acquisition and save the data to a CSV file.
*   **Dependencies:**
    *   `flet` module for creating the user interface.
    *   `socket` module for Wi-Fi communication.
    *   `threading` module for handling data reading in a separate thread.
    *   `time` module for delays.
    *   `re` module for regular expressions (data parsing).
    *   `collections` module for the `deque` data structure.
    *   `matplotlib` module for plotting.
    *   `io` and `base64` modules for image handling.
    *   `csv` module for saving data to a CSV file.

## Data Science Relevance

This project demonstrates a simplified data science pipeline:

1.  **Data Acquisition:** The MPU6050 sensor acquires motion data.
2.  **Data Transmission:** The ESP32 transmits the data over Wi-Fi.
3.  **Data Visualization:** The Flet interface visualizes the data using Matplotlib, enabling real-time analysis.

The collected data can be further analyzed using various data science techniques for applications such as activity recognition, gesture analysis, and more.

## Spanish Section

## Visión General

Este proyecto implementa un sistema de captura de movimiento utilizando el sensor acelerómetro/giroscopio MPU6050. Transmite los datos a través de Wi-Fi a una interfaz fácil de usar construida con Flet, que visualiza los datos en tiempo real utilizando Matplotlib. Este proyecto demuestra una canalización de datos básica, que muestra la adquisición, transmisión y visualización de datos, relevante para aplicaciones de ciencia de datos.

El sistema consta de tres componentes principales:

1.  **Código del Microcontrolador ESP32 (main.py):** Lee los datos del sensor MPU6050 y los transmite a través de Wi-Fi utilizando sockets TCP.
2.  **Librería MPU6050 (MPU6050.py):** Proporciona una interfaz para interactuar con el sensor MPU6050, manejando la comunicación I2C y la conversión de datos.
3.  **Interfaz de Usuario Flet (INTERFAZ.PY):** Recibe datos del ESP32 a través de Wi-Fi, los analiza y grafica los datos del acelerómetro en tiempo real utilizando Matplotlib.

## Elementos Visuales

### Imagen de la Interfaz

[Espacio para la Imagen de la Interfaz]

### Imagen del Dispositivo

[Espacio para la Imagen del Dispositivo]

## Descripción del Código

### 1. Código del Microcontrolador ESP32 (main.py)

*   **Propósito:** Este código se ejecuta en el microcontrolador ESP32 y es responsable de inicializar el sensor MPU6050, leer los datos del acelerómetro, calcular los ángulos y enviar los datos a través de Wi-Fi utilizando sockets TCP.
*   **Características Clave:**
    *   Inicializa el sensor MPU6050 utilizando la librería `MPU6050.py`.
    *   Lee los datos del acelerómetro en m/s².
    *   Calcula los ángulos a partir de los datos del acelerómetro.
    *   Transmite los datos a través de Wi-Fi utilizando sockets TCP para su visualización.
*   **Dependencias:**
    *   Librería `MPU6050.py`.
    *   Módulo `machine` para el control de pines.
    *   Módulo `time` para los retrasos.
    *   Módulo `math` para las funciones matemáticas.
    *   Módulo `network` para la conectividad Wi-Fi.
    *   Módulo `socket` para la comunicación TCP.

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

*   **Propósito:** Este código crea una interfaz gráfica de usuario utilizando el framework Flet para visualizar los datos del acelerómetro recibidos desde el ESP32 a través de Wi-Fi.
*   **Características Clave:**
    *   Se conecta al ESP32 a través de Wi-Fi y lee los datos entrantes.
    *   Analiza la cadena de datos para extraer los valores del acelerómetro y los ángulos.
    *   Grafica los datos del acelerómetro y los ángulos en tiempo real utilizando Matplotlib.
    *   Permite al usuario iniciar/detener la adquisición de datos y guardar los datos en un archivo CSV.
*   **Dependencias:**
    *   Módulo `flet` para crear la interfaz de usuario.
    *   Módulo `socket` para la comunicación Wi-Fi.
    *   Módulo `threading` para manejar la lectura de datos en un hilo separado.
    *   Módulo `time` para los retrasos.
    *   Módulo `re` para las expresiones regulares (análisis de datos).
    *   Módulo `collections` para la estructura de datos `deque`.
    *   Módulo `matplotlib` para la graficación.
    *   Módulos `io` y `base64` para el manejo de imágenes.
    *   Módulo `csv` para guardar los datos en un archivo CSV.

## Relevancia para la Ciencia de Datos

Este proyecto demuestra una canalización de ciencia de datos simplificada:

1.  **Adquisición de Datos:** El sensor MPU6050 adquiere datos de movimiento.
2.  **Transmisión de Datos:** El ESP32 transmite los datos a través de Wi-Fi.
3.  **Visualización de Datos:** La interfaz Flet visualiza los datos utilizando Matplotlib, lo que permite el análisis en tiempo real.

Los datos recopilados se pueden analizar más a fondo utilizando diversas técnicas de ciencia de datos para aplicaciones como el reconocimiento de actividad, el análisis de gestos y más.
