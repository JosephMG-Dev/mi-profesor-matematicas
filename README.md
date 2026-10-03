# 🎓 Mi Profesor de Matemáticas Personal

Una aplicación web educativa, interactiva y personalizada que funciona como un **profesor particular de matemáticas**. Diseñada especialmente para estudiantes de **Ingeniería de Sistemas** que buscan superar dificultades previas y dominar las matemáticas paso a paso: desde las operaciones aritméticas elementales hasta los fundamentos necesarios para las asignaturas de ingeniería (álgebra lineal, funciones, lógica y cálculo).

---

## 🌟 Visión y Filosofía Pedagógica

Esta plataforma no es un simple banco de preguntas con respuestas automáticas de «correcto» o «incorrecto». Su objetivo es **enseñar a pensar matemáticamente**:

* **Sin presiones ni límites de tiempo arbitrarios**: Cada estudiante avanza a su propio ritmo.
* **Comprensión profunda ("¿Por qué funciona?")**: Se explican los conceptos detrás de cada regla o algoritmo en lugar de memorizar fórmulas sin sentido.
* **Conexión directa con la Ingeniería de Sistemas**: Se vinculan los conceptos matemáticos con aplicaciones reales en programación, gráficos por computadora, algoritmos, complejidad computacional ($O(n)$) y bases de datos.
* **Pistas graduales en 3 niveles**: Ayuda al estudiante a encontrar la solución por sí mismo antes de mostrar el procedimiento completo.
* **Diagnóstico inteligente del error**: Diferencia entre errores de cálculo, confusión de signos, fallos procedimentales o descuidos de notación, ofreciendo retroalimentación constructiva y empática.

---

## 🚀 Características Principales

### 1. 🧭 Evaluación Diagnóstica Inicial
* Prueba interactiva de 16 preguntas breves, progresivas y sin estrés.
* Determina el punto de partida real del estudiante y desbloquea el nivel adecuado sin obligarlo a repetir lo que ya domina.

### 2. 🗺️ Mapa de Ruta por Niveles (54 Lecciones)
La currícula está estructurada de manera modular y acumulativa, cubriendo desde la base escolar hasta el **curso universitario completo de Matemática para la Ingeniería (2026-2)**:
1. **Nivel 1: Sumas y Restas** (Propiedades, rectas numéricas, números con signo, problemas aplicados).
2. **Nivel 2: Multiplicaciones** (Tablas, productos de varios dígitos, jerarquía operacional).
3. **Nivel 3: Divisiones** (Cociente, residuo, divisibilidad, factores primos).
4. **Nivel 4: Fracciones, Decimales y Porcentajes** (Simplificación, MCD/MCM, conversiones).
5. **Nivel 5: Potencias, Raíces y Logaritmos** (Leyes de exponentes, radicación, logaritmos y complejidad $O(\log n)$).
6. **Nivel 6: Álgebra Básica y Fundamentos de Computación** (Términos semejantes, ecuaciones lineales, productos notables, ecuaciones cuadráticas, conversión binaria y hexadecimal).
7. **Nivel 7: Matemática para la Ingeniería (Sílabo Oficial 2026-2 - 16 Sesiones)**:
   - *Sesión 1 (7.1)*: Números Reales, Desigualdades, Intervalos y Valor Absoluto.
   - *Sesión 2 (7.2)*: Expresiones Racionales y Fracciones Algebraicas.
   - *Sesión 3 (7.3)*: Matrices y Operaciones Matriciales en Ingeniería (suma, escalar, producto matricial).
   - *Sesión 4 (7.4)*: Determinantes y Matriz Inversa (Sarrus, Gauss-Jordan).
   - *Sesión 5 (7.5)*: Sistemas de Ecuaciones Lineales y Regla de Cramer.
   - *Sesión 6 (7.6)*: Funciones Reales y Modelos en Ingeniería (Dominio, rango, costos, ingresos).
   - *Sesión 7 (7.7)*: Composición de Funciones $(f \circ g)(x)$ y Función Inversa $f^{-1}$.
   - *Sesión 8/9 (7.8)*: Funciones Seccionadas (por Tramos) y Análisis Gráfico.
   - *Sesión 10 (7.9)*: Examen Parcial Consolidado de Ingeniería.
   - *Sesión 11 (7.10)*: Coordenadas Polares y Curvas Planas (conversión polar $\leftrightarrow$ cartesiana).
   - *Sesión 12 (7.11)*: Límites de Funciones, Límites Laterales y Teoremas.
   - *Sesión 13 (7.12)*: Cálculo Analítico de Límites (indeterminaciones $0/0$, racionalización, límites al infinito).
   - *Sesión 14 (7.13)*: Continuidad de Funciones y Análisis de Discontinuidades.
   - *Sesión 15 (7.14)*: Derivadas, Reglas de Derivación, Regla de la Cadena y Criterios de Optimización.
   - *Sesión 16 (7.15)*: Examen Final Integral de Matemática para la Ingeniería.

### 3. 🎯 Flujo por Lección Estilo Khan Academy (3 Etapas Obligatorias)
Cada lección sigue una estructura secuencial rigurosa para garantizar que nadie intente resolver sin haber aprendido primero:
* **Fase 1: 📖 Teoría y Ejemplos Resueltos**:
  - Explicación conceptual intuitiva (sin tecnicismos intimidantes).
  - Fundamento lógico (*¿por qué funciona?*).
  - Conexión directa con la **Ingeniería de Sistemas** (memoria RAM, GPU rendering, Machine Learning, grafos, algoritmos).
  - **Ejemplo modelo resuelto paso a paso** con todo el desglose.
  - Errores comunes a evitar y consejos nemotécnicos del profesor.
* **Fase 2: ✏️ Práctica Guiada con Ayudas**:
  - Ejercicios interactivos con **pistas graduales en 3 niveles**.
  - Botón de rescate *«🤷 No sé cómo resolver esto»* que muestra el método paso a paso.
  - Enlace permanente para volver a consultar la teoría del tema en cualquier momento.
  - **Contador silencioso**: Sin reloj en pantalla que genere estrés o ansiedad.
* **Fase 3: 🎯 Examen de Dominio**:
  - Evaluación formal de 4 preguntas **sin pistas ni ayudas**.
  - Aprobación requerida ($\ge 75\%$) para declarar la lección oficialmente dominada y desbloquear el siguiente tema en el mapa del curso.
  - Medición silenciosa de tiempo para registrar fluidez y automatización.

### 4. 🧮 Motor Matemático Avanzado con SymPy y KaTeX
* **Validación Simbólica con SymPy**: Reconoce equivalencia matemática real (por ejemplo: `2(x+3)` y `2x+6` son ambas consideradas correctas, al igual que factorizaciones e intervalos).
* **Tipografía Matemática con KaTeX**: Fórmulas algebraicas, matrices, derivadas y límites renderizados con calidad LaTeX tipográfica profesional en navegador.

### 5. 📊 Seguimiento, Analítica y Logros
* **Panel de Progreso**: Gráficos interactivos con Chart.js (tasa de acierto, evolución temporal y distribución por nivel).
* **Racha de Días (Streak)**: Fomenta la constancia diaria mediante un contador de sesiones activas.
* **🏆 20 Logros Desbloqueables**: Medallas que premian la resiliencia, el esfuerzo, las rachas de respuestas correctas y los temas completados.
* **Historial Detallado**: Registro completo de cada ejercicio resuelto, tiempo empleado, intentos y errores clasificados.

---

## 🛠️ Stack Tecnológico

* **Backend**: Python 3.12 con [Flask](https://flask.palletsprojects.com/) (API RESTful y servicio web).
* **Base de Datos**: [Microsoft SQL Server 2019](https://www.microsoft.com/sql-server) conectada mediante `pyodbc` con el driver oficial `ODBC Driver 17 for SQL Server`.
* **Frontend**: Single Page Application (SPA) construida en **HTML5 semántico**, **Vanilla JavaScript** y **Vanilla CSS** con sistema de diseño oscuro, responsivo y animaciones fluidas.
* **Visualización de Datos**: [Chart.js 4.4](https://www.chartjs.org/) para las métricas de rendimiento y evolución del estudiante.

---

## 📁 Estructura del Proyecto

```text
d:/Mats/
├── .env                  # Variables de entorno y credenciales (local)
├── .env.example          # Plantilla de configuración
├── requirements.txt      # Dependencias de Python (Flask, pyodbc)
├── app.py                # Servidor principal Flask y endpoints de la API REST
├── database.py           # Conexión a SQL Server, esquema de tablas y consultas
├── ejercicios.py         # Motor generador de ejercicios, pistas y diagnóstico
├── teoria.py             # Guías pedagógicas, conceptos y ejemplos modelo resueltos
├── static/
│   ├── css/
│   │   └── styles.css    # Sistema de diseño, temas y estilos responsivos
│   └── js/
│       └── app.js        # Lógica del cliente, estado SPA, eventos y gráficos
└── templates/
    └── index.html        # Plantilla HTML principal de la aplicación
```

---

## ⚙️ Requisitos Previos

1. **Python 3.10 o superior** (probado y optimizado en Python 3.12).
2. **Microsoft SQL Server 2019** (o superior) instalado y con servicio activo.
3. **ODBC Driver 17 for SQL Server** instalado en el sistema operativo.

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar o acceder al directorio del proyecto
```powershell
cd d:\Mats
```

### 2. Configurar las variables de entorno
Crea o edita el archivo `.env` en la raíz del proyecto con tus credenciales de SQL Server:
```env
DB_SERVER=localhost
DB_NAME=Prueba
DB_USER=sa
DB_PASSWORD=tu_contraseña_aqui
```

### 3. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 4. Iniciar la aplicación
Ejecuta el servidor Flask:
```powershell
python app.py
```

Al iniciar, la aplicación:
1. Comprueba y establece la conexión con SQL Server 2019.
2. Crea automáticamente las tablas si no existen (`perfil`, `lecciones`, `ejercicios`, `sesiones`, `logros`, `evaluacion_diagnostica`).
3. Carga la currícula completa de 54 lecciones (incluyendo las 16 sesiones de Ingeniería 2026-2) y el catálogo de 20 logros.
4. Inicia el servidor en el puerto `5000`.

### 5. Abrir en el navegador
Abre tu navegador web y visita:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## 🗄️ Modelo de Datos (SQL Server 2019)

La base de datos relacional almacena el ciclo de vida del estudiante a través de 6 tablas principales:

* **`perfil`**: Información del usuario, nivel actual, lección en curso, racha de días, mejor racha y estado de evaluación inicial.
* **`lecciones`**: Catálogo de 54 lecciones con nivel, orden, porcentaje de dominio (0-100%), ejercicios completados y estado (`bloqueada`, `en_progreso`, `dominada`).
* **`ejercicios`**: Historial de cada ejercicio practicado con operación, respuestas, acierto (`BIT`), número de intentos, tiempo en segundos, uso de pistas y categoría de error.
* **`sesiones`**: Tiempos de estudio diarios, minutos acumulados y ejercicios resueltos por sesión.
* **`logros`**: Catálogo de medallas con título, descripción, icono y fecha de desbloqueo.
* **`evaluacion_diagnostica`**: Resultados detallados del test inicial para calibrar el punto de partida.

---

## 🎓 Conexiones con la Ingeniería de Sistemas

A lo largo del curso, las matemáticas se contextualizan con conceptos informáticos:
* **Aritmética y Números Enteros**: Representación binaria, complemento a 2, desbordamiento de enteros (*integer overflow*).
* **Fracciones y Decimales**: Aritmética de punto flotante IEEE 754, errores de redondeo en software crítico.
* **Potencias y Logaritmos**: Complejidad algorítmica ($O(\log n)$, $O(n^2)$), árboles binarios, búsqueda binaria.
* **Álgebra**: Variables, ecuaciones invariantes de bucle, funciones puras y transformaciones.
* **Matrices y Vectores**: Gráficos 3D por computadora (transformaciones homogéneas, shaders), redes neuronales y *machine learning*.
* **Lógica Proposicional**: Tablas de verdad, álgebra de Boole, compuertas lógicas y condicionales en programación.

---

## 🤝 Soporte y Contribuciones

Desarrollado para potenciar el aprendizaje continuo y adaptativo. Si deseas extender el generador con nuevos módulos o ejercicios avanzados, consulta el archivo [ejercicios.py](file:///d:/Mats/ejercicios.py).
