# User Behavior Monitor

**Created by Thomas O'neil Álvarez**

## Descripción

Esta herramienta monitorea los inicios de sesión de los usuarios en tiempo real y detecta anomalías basadas en múltiples inicios de sesión en un corto período de tiempo.

## Imagen de la Herramienta

![User Behavior Monitor](https://github.com/ccyl13/user_behavior_monitor/raw/main/2.png)

## Instalación

1. **Clona el repositorio:**

   ```bash
   git clone https://github.com/ccyl13/user_behavior_monitor.git
   cd user_behavior_monitor
   chmod +x user_behavior_monitor.py
   pip install psutil colorama
   pip install watchdog
   python user_behavior_monitor.py
