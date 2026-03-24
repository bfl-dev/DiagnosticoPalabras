# Documentación de Implementación y Arquitectura

Este documento detalla los principios de diseño, justificaciones técnicas y supuestos adoptados durante la construcción del Sistema de Minado de Código de GitHub, evaluados desde el punto de vista de la Arquitectura de Software.

---

## 1. Decisiones de Diseño

Las siguientes resoluciones arquitectónicas tienen como finalidad principal asegurar la escalabilidad, la limpieza de los datos (precisión) y la resiliencia del proceso continuo de minería.

### Arquitectura Productor-Consumidor
El sistema adopta el diseño de integración Productor-Consumidor con el fin de priorizar el **desacoplamiento**.
- **Beneficio Principal:** El proceso concurrente de minería (consultas de API recursivas, descarga web de código, descompresión *in-memory* y perfilado sintáctico de alto poder algorítmico) es increíblemente intensivo, ocupando picos tanto de CPU como de Throughput (Red/IO).
Obligando a separar por completo esta lógica dura del componente `Visualizer`, se asegura que la interfaz para el usuario final no experimentará ralentización ni denegaciones de servicio. Si el consumidor recibe congestiones masivas, el front-end y backend mantienen su responsividad para las lecturas. Cada contenedor escala e implementa su recuperación de errores de forma totalmente autónoma. 

### Uso de Análisis Sintáctico de Árbol (AST y javalang)
Para recuperar la firma o identificadores de los métodos encapsulados en los ficheros, evitamos el anti-patrón de implementar _Expresiones Regulares_ (RegEx) y optamos por el ecosistema de los _Abstract Syntax Trees_.
- **Precisión vs. Ruido (Data-Noise):** Parsear lenguajes robustos como Java o multipropósito como Python exclusivamente por texto induce abundantes falsos positivos estadísticos originados por comentarios, nombres de variables equívocos o literales multi-línea. Al parsear a nivel de compilador intermedio (AST), garantizamos localizar las declaraciones en su nodo preciso iterativo (`ast.FunctionDef` // `MethodDeclaration`), purificando infinitamente nuestra captura final frente al ruido provocado por enfoques arcaicos.

### Broker de Transacciones Temporales (Redis)
Se seleccionó ecosistema `Redis` como puente de memoria en lugar de modelos relacionales puramente tabulados.
- **Rankings Analíticos (Sorted Sets):** Las capacidades innatas que presentan estructuras como *Sorted Sets* hacen que el motor sea ideal. Al implementar la función atómica `ZINCRBY`, garantizamos simultáneamente actualizar el score del token en el índice invertido manteniendo un recuento con complejidades estables del tipo  **O(log(N))**, independientemente de la alta recurrencia paralela del flujo P2C de minería.

### Manejo de Resiliencia y Estado (Checkpoints)
La arquitectura persigue resiliencia de alto estrés; la descarga de millones de repositorios no puede reiniciarse perpetuamente al surgir colapsos del proceso.
- **Tolerancia y Reanudación:** Frente a cierres (Stop de contenedores) o interrupciones de red catastróficos, se incluyó un gestor inyectado en el Broker que serializa la paginación a nivel de lenguaje (`miner:checkpoint`). Cuando la imagen se reinicia, acude al estado del documento antes de ejecutar su iteración, imposibilitando cuellos de botella e ineficiencias de sobrecarga sobre la base de datos de GitHub recuperando sin fisuras su último progreso del set.

---

## 2. Supuestos y Consideraciones

El motor está gobernado bajo convenciones de contexto operacionales dictadas por las barreras propias de GitHub y de la filosofía limpia de datos.

### Lógica de Tokenización Asumida
Asumiendo que los programadores enuncian identificaciones funcionales y descriptivas, establecemos:

| Convención    | Comportamiento / Split           | Ejemplo                      | Token Generado               |
| ------------- | -------------------------------- | ---------------------------- | ---------------------------- |
| **camelCase** | Detección previa a Up-Case       | `parseHttpResponse`          | `parse`, `http`, `response`  |
| **PascalCase**| Detección previa a Up-Case       | `CalculateMetricsV2`         | `calculate`, `metrics`       |
| **snake_case**| Segmentación por subrayados      | `update_database_schema`     | `update`, `database`, `schema`|

Además, el framework aplica una regla heurística que asume que preposiciones (`is`, `to`, `from`) y términos muy cortos (longitud < 3 excluidos) ensucian el índice. Los caracteres numéricos puros y el *Stop-Words List* son excluidos preventivamente.

### Gestión Defensiva de Rate Limits en la API
- La recolección intensiva respeta explícitamente y como prioridad la integridad de la provisión oficial de código. Evaluando de manera pasiva y preventiva los headers `X-RateLimit-Remaining` y `X-RateLimit-Reset` se asume la inevitable barrera de solicitudes.
- Al detectarse un descenso crítico en la tasa de peticiones, el orquestador somete preventivamente a *time.sleep* todo el hilo concurrente sincronizando su despertar en base de epoch milimetrado asegurando un comportamiento de raspado cívico al ecosistema general.

### Alcance Direccional del Minado
Asumiendo que recolectar repositorios nulos afecta la fiabilidad estadística sobre qué _"sintonías y convencionales"_ adoptan las ingenierías fuertes:
- **Calidad Sobre Cantidad:** En vez de escrutar cada rincón masivo, se priorizan las solicitudes de repositorios ordenados **puramente por factor 'Stars' (*descendente*)**. Se garantiza como supuesto fundamental que los proyectos más consumidos son los directrices de la calidad real de código de la rama comunitaria.
