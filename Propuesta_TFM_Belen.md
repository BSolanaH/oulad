# Propuesta a presentar — TFM

**Opción seleccionada:** 1) Análisis de un dataset (orientación Data Scientist)

**Título provisional:**
Sistema de detección temprana de riesgo académico a partir del comportamiento
de estudiantes en plataformas de aprendizaje online: un enfoque predictivo,
interpretable y productivizable sobre datos a gran escala.

---

## Descripción del TFM propuesto

El aprendizaje online genera grandes volúmenes de datos de comportamiento
(accesos, interacción con los recursos, progreso, actividad a lo largo del
curso) que rara vez se aprovechan para anticipar qué estudiantes están en
riesgo de no completar o no superar su formación. Este TFM propone construir un
**sistema de alerta temprana** que, a partir del comportamiento de las primeras
semanas de un curso, prediga el resultado final del estudiante (finalización,
abandono o suspenso) con suficiente antelación como para permitir una
intervención.

El trabajo se aborda como un problema de **modelización supervisada** sobre un
conjunto de datos **público, de licencia abierta y de gran tamaño** procedente
de una plataforma de aprendizaje online universitaria. La fuente principal
prevista es el *Open University Learning Analytics Dataset* (OULAD), que combina
información demográfica, de matrícula y de evaluación con un registro de
interacción diaria con el entorno virtual de aprendizaje del orden de millones
de eventos. Como fuente alternativa equivalente, que responde a la misma
pregunta de investigación con el mismo enfoque metodológico, se contempla el
conjunto de datos abiertos de cursos masivos online *HarvardX–MITx
(Person-Course, edX)*. La elección definitiva de la fuente se confirmará en la
fase inicial de exploración, manteniendo intactos el objetivo y el método.

El núcleo del trabajo no reside en el conjunto de datos sino en el tratamiento
que se hace de él. En particular, el TFM pondrá el foco en:

- **Ingeniería de variables de comportamiento temprano**: transformar el
  registro de interacción en variables que capturen *cómo* se comporta un
  estudiante en las primeras semanas (intensidad, regularidad, evolución
  temporal de la actividad), que serán los predictores del modelo.
- **Modelización predictiva comparada**: entrenar y comparar varias técnicas de
  machine learning, justificando su elección y analizando sus fortalezas y
  debilidades, con el objetivo explícito de aportar valor más allá de lo que
  ofrecería una solución AutoML.
- **Interpretabilidad y lectura de negocio**: explicar qué patrones de
  comportamiento anticipan el riesgo, traduciendo los resultados del modelo a
  conclusiones accionables comprensibles por un perfil no técnico.
- **Procesamiento a gran escala**: dado el volumen del registro de interacción,
  se incorporará una capa de procesamiento distribuido (Spark/Databricks) como
  parte del pipeline de preparación de datos.
- **Productivización**: el modelo final se dispondrá de forma que pueda recibir
  el comportamiento de un estudiante nuevo y devolver una predicción de riesgo,
  demostrando su uso en un equivalente a una aplicación empresarial.

El proyecto se beneficia de mi experiencia profesional en el sector de la
formación y el e-learning, que aporta criterio de dominio para la interpretación
de los resultados y la formulación de conclusiones útiles para un equipo de
negocio.

---

## Índice provisional de la memoria

1. **Introducción y contexto**
   1.1. El problema del abandono y el rendimiento en la formación online
   1.2. Objetivos del trabajo y pregunta de investigación
   1.3. Alcance y enfoque

2. **Datos y contexto del problema**
   2.1. Descripción de la fuente de datos y sus derechos de uso
   2.2. Estructura del conjunto: comportamiento, demografía y resultados
   2.3. Definición de la variable objetivo (riesgo / resultado final)

3. **Análisis exploratorio (EDA)**
   3.1. Caracterización de los estudiantes y de su actividad
   3.2. Patrones de comportamiento y su relación con el resultado
   3.3. Hallazgos relevantes para el modelado

4. **Preparación de datos y procesamiento a gran escala**
   4.1. Arquitectura del pipeline de datos
   4.2. Procesamiento distribuido del registro de interacción (Spark/Databricks)
   4.3. Ingeniería de variables de comportamiento temprano

5. **Modelización predictiva**
   5.1. Planteamiento del problema y estrategia de validación
   5.2. Técnicas empleadas y justificación
   5.3. Comparativa de modelos: rendimiento, fortalezas y debilidades
   5.4. Más allá del AutoML: aportación propia

6. **Interpretabilidad y discusión**
   6.1. Variables y patrones que anticipan el riesgo
   6.2. Lectura de negocio de los resultados
   6.3. Limitaciones del modelo

7. **Productivización**
   7.1. Diseño de la solución para predicción sobre nuevos estudiantes
   7.2. Demostración de funcionamiento extremo a extremo

8. **Conclusiones y líneas futuras**
   8.1. Conclusiones para un equipo de negocio
   8.2. Mejoras y extensiones posibles (p. ej. análisis de texto/feedback
        del estudiante en fuentes que lo permitan)

9. **Bibliografía** (máx. media cara)

**Anexos** (fuera del límite de 20 caras): código desarrollado, EDA detallado,
ejecución completa de modelos.
