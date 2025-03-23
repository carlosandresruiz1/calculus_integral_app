# Pcalculo Integral

Esta aplicación está diseñada para analizar y comprender incidentes de tráfico utilizando cálculos de cálculo integral. Proporciona herramientas avanzadas para simplificar y resolver problemas relacionados con integrales, permitiendo modelar y predecir patrones de tráfico. Su objetivo principal es ayudar a prevenir futuros incidentes de tráfico mediante un análisis más profundo y eficiente de los datos.

## Guía de Instalación

Sigue estos pasos para configurar la aplicación:

### 1. Clonar el Repositorio
Clona este repositorio en tu máquina local usando:
```
git clone <repository-url>
```

### 2. Crear un Entorno Virtual
Navega al directorio del proyecto y crea un entorno virtual:
```
cd Pcalculo integral
python -m venv venv
```

### 3. Activar el Entorno Virtual
- En **Windows**:
  ```
  venv\Scripts\activate.ps1
  ```
- En **macOS/Linux**:
  ```
  source venv/bin/activate
  ```

### 4. Instalar Dependencias
Una vez activado el entorno virtual, instala las dependencias requeridas usando `requirements.txt`:
```
pip install -r requirements.txt
```

### 5. Iniciar el Servidor de Django
Para iniciar el servidor de desarrollo de Django, ejecuta el siguiente comando desde el directorio del proyecto:
```
python manage.py runserver
```
Esto iniciará el servidor en `http://127.0.0.1:8000/`. Abre esta URL en tu navegador para acceder a la aplicación.

## Notas
- Asegúrate de tener Python instalado (preferiblemente la versión 3.7 o superior).
- Siempre activa el entorno virtual antes de ejecutar la aplicación o instalar paquetes adicionales.

¡Disfruta usando la aplicación Pcalculo Integral!
