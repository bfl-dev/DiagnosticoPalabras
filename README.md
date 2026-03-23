# Sistema de Minado de Código GitHub

Este proyecto es una solución de análisis de datos basada en una arquitectura **Productor-Consumidor** usando contenedores Docker. El objetivo principal es extraer los nombres de métodos más frecuentes en repositorios populares de **Python** y **Java** alojados en GitHub.

## Arquitectura

- **Productor (Miner)**: Aplicación Python que consulta la API de GitHub, clona/descarga código fuente, extrae los nombres de métodos y funciones utilizando [AST](https://docs.python.org/3/library/ast.html) para Python y [javalang](https://github.com/c2nes/javalang) para Java. Los métodos son tokenizados usando expresiones regulares para separar variables en camelCase, PascalCase y snake_case.
- **Broker (Redis)**: Almacena de manera atómica la frecuencia de las palabras extraídas mediante *Sorted Sets* (`ZINCRBY`). Además, almacena el estado de reanudación (checkpoint) en caso de reinicio de la aplicación.
- **Consumidor (Visualizer)**: Backend Node.js/Express muy liviano que expone una API para consultar el Top-N de palabras, junto a una SPA frontend en Vanilla JS interactiva que muestra gráficos en tiempo real con *Chart.js* y *WordCloud*.

---

## 🚀 Instalación y Despliegue

### Requisitos
- **Docker** y **Docker Compose**.
- Un Token de Acceso Personal de GitHub.

### 1. Configurar Variables de Entorno

```bash
cp .env.example .env
```
Edita el archivo `.env` y añade tu [GitHub Token](https://github.com/settings/tokens) en la variable `GITHUB_TOKEN`.

### 2. Levantar el Entorno

Con un solo comando, puedes compilar las imágenes e iniciar todos los servicios:

```bash
docker-compose up --build
```

### 3. Visualizar en Tiempo Real

Abre tu navegador web e ingresa a:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## Decisiones de Diseño

- **AST y javalang vs Expresiones Regulares Directas:** Extraer firmas de métodos por Regex es muy propenso a errores (e.g. código comentado, strings multilinea). El uso de árboles de sintaxis abstracta (AST para Python, javalang para Java) garantiza la recolección precisa *únicamente* de nombres de funciones/métodos declarados.
- **Redis Sorted Sets:** Esta estructura permite el conteo ultra rápido referenciado por una clave, ideal para analíticas en tiempo real. `ZINCRBY` incrementa el score del token de forma atómica en un único servidor de Redis.
- **Manejo de Estado (Checkpoints):** Es posible que el miner se detenga por reinicio del contenedor o agotamiento crítico de llamadas de la API. Guardar la paginación de los repositorios en una clave `miner:checkpoint` permite reanudar donde se dejó el proceso.
- **Arquitectura Productor-Consumidor:** Descopla el proceso intensivo de red, CPU (Regex+AST) del cliente ligero de visualización. De esta manera el front-end siempre se mantendrá receptivo e independiente del rate-limiting de GitHub del miner.

## TODO
- Añadir al visualizador una caja con los datos crudos. y resumen de los datos recibidos y presentados.
- Revisar el README.md 
- Realisar la documentacion basica de la implementacion (Deciciones de diseño, supuestos, etc)