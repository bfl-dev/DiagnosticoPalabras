# Sistema de Minado de Código GitHub

## Introducción
Este proyecto es una solución de análisis de datos estructurada bajo una arquitectura **Productor-Consumidor** empleando contenedores Docker. El sistema se encarga de extraer, de manera automatizada y continua, los nombres de métodos y funciones más frecuentes en repositorios populares de **Python** y **Java** alojados en GitHub. El objetivo principal es proporcionar métricas en tiempo real sobre las convenciones de nombrado en la industria del software.

## Tecnologías
El sistema está construido utilizando el siguiente stack tecnológico:
- **Miner (Productor):** Python 3.11, librerías `ast` y `javalang` para el parsing e interacciones de red.
- **Visualizer (Consumidor):** Node.js (Express), Vanilla JS, Chart.js.
- **Broker y Persistencia:** Redis (Sorted Sets para recuento atómico y almacenamiento de estado).
- **Orquestación:** Docker y Docker Compose.

## Arquitectura (Breve)
El proyecto se divide en tres componentes interconectados mediante una red interna de Docker:
1. **Miner:** Consulta la API de GitHub, descarga el código fuente y extrae los tokens semánticos de los métodos. Actualiza atómicamente las frecuencias en el Broker.
2. **Broker (Redis):** Almacena el ranking global mediante conjuntos ordenados y asegura persistencia temporal de estado (checkpoints).
3. **Visualizer:** Consumidor ligero que consulta a Redis y muestra los resultados analíticos a través de un Dashboard interactivo (Single Page Application).

> [!NOTE]
> Para un desglose extendido y argumentación de todas las decisiones de diseño y supuestos del proyecto, consulta nuestra documentación técnica en [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Guía de Inicio Rápido

### Requisitos Previos
Antes de ejecutar el sistema, asegúrate de tener instalado y configurado lo siguiente en tu máquina host:
*   **Docker** (v20.10+ recomendado).
*   **Docker Compose** (v2.0+).
*   Un **Token de Acceso Personal de GitHub** (Personal Access Token). Puedes generarlo gratuitamente desde la [Configuración de Desarrollador de GitHub](https://github.com/settings/tokens).

### 1. Configuración del Entorno
Es necesario parametrizar las variables de entorno de ambos microservicios. Copia el archivo de entorno de ejemplo provisto en la raíz del repositorio:

```bash
cp .env.example .env
```
Posteriormente, abre el archivo `.env` recién creado con tu editor de texto e ingresa tu token temporal en la variable `GITHUB_TOKEN`.

### 2. Claridad de Ejecución
El proyecto está completamente dockerizado para evitar conflictos de sistema. Para levantar todos los servicios (Miner, Redis y Visualizer), ejecuta este **único comando** en tu terminal:

```bash
docker-compose up --build -d
```
*(El argumento `-d` mantendrá los contenedores corriendo silenciosamente en segundo plano. Omítelo si prefieres estudiar la secuencia de logs de la aplicación en vivo).*

### 3. Visualización en Tiempo Real
Con la orquestación en marcha, puedes acceder al panel de analíticas alojado por el servidor Express desde de tu navegador weab en:
👉 **[http://localhost:3000](http://localhost:3000)**