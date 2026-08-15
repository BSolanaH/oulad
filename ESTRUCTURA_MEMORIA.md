# Estructura de la Memoria TFM

> Guardado: 14 agosto 2026. Revisar antes de empezar a redactar.

---

## Restricciones de la guía UCM

- **Máximo 20 páginas** (folio, tamaño ~A4). NO cuentan: portada, contraportada, índice, anexos.
- Fuente Verdana o Arial, tamaño 10-11.
- Bibliografía: media página, dentro del límite de 20.
- Orientación: informe técnico-empresarial. NO paper científico, NO PowerPoint.
- Puede entregarse como PDF, DOCX o notebook HTML exportado.
- El código y estudios detallados van en **Anexos** (sin límite de páginas).

---

## Entregables

| Entregable | Formato | Límite |
|---|---|---|
| Memoria | PDF / DOCX / HTML | 20 páginas |
| Vídeo | MP4 (o link YouTube/Vimeo) | 5 min / 50 MB |
| Anexos | Notebooks (.ipynb o HTML) | Sin límite |

**Nombre del fichero zip:** `Belen_Solana_Hurtado_Prediccion_Abandono_OULAD.zip`

---

## Estructura propuesta (estimación de páginas)

### Portada (no cuenta)
- Título, nombre, máster, fecha

### Índice (no cuenta)

---

### 1. Introducción y contexto del problema — 1,5 páginas
- Problema: deserción en educación online (cifras de contexto)
- Objetivo: sistema de alerta temprana a 4 semanas vista
- Dataset OULAD: fuente pública UCI, por qué este dataset (tamaño, riqueza de señales)
- Unidad de análisis: matrícula (estudiante × módulo × presentación) — no el estudiante individual

### 2. Dataset y auditoría de calidad — 2 páginas
- Estructura del OULAD: 7 tablas, 32.593 matrículas, 7 módulos, 4 presentaciones
- Hallazgos clave de la auditoría tabla por tabla:
  - Duplicados reales en studentVle.csv (787.170 filas exactas, estrategia de fix)
  - GGG: TMA/CMA con weight=0 estructural — distinto de EEE
  - 93 Withdrawn sin date_unregistration concentrados en TEST (limitación)
  - AAA sin presentación B — consecuencia para el split
- Decisiones de preprocesado documentadas:
  - Filtro de activos: excluir date_unregistration ≤ 27 (5.040 excluidos)
  - Variable objetivo: binaria Fail+Withdrawn=1 / Pass+Distinction=0
  - Split cronológico: TRAIN 2013B+2013J+2014B → TEST 2014J
- Dataset final: 27.553 matrículas, balance 44,2% riesgo / 55,8% no riesgo

### 3. Análisis exploratorio — 3 páginas
- Riesgo por módulo (gráfico): CCC 62% → AAA 29%, variación de 33pp
- Predictores demográficos (gráficos clave):
  - num_of_prev_attempts: gradiente 0→3 intentos (41,8% → 71,2%)
  - highest_education: gradiente de 36pp
  - imd_band: gradiente socioeconómico
- Señal VLE: clics por semana (no riesgo vs riesgo, ratio ~1,8), actividad pre-curso
- Señal de evaluaciones: tasa de entrega en módulos con eval (97,9% vs 78,4%)
- ⚠️ Nota redacción: "nivel socioeconómico del entorno" — NO "deprivación económica"

### 4. Metodología — 2 páginas
- Variable objetivo y justificación (balance manejable, accionable)
- Ventana de predicción 0-27 días: justificación y anti-leakage explícito
  - Excluidas: final_result, date_unregistration
  - studentVle filtrado a date ≤ 27; studentAssessment filtrado a date_submitted ≤ 27 e is_banked=0
- Split cronológico: por qué no aleatorio (distributional shift temporal)
- Tabla resumen de las 25 features construidas:
  - 9 demográficas (de student_info)
  - 9 de comportamiento VLE (incluyendo pre-curso y regularidad)
  - 4 de evaluaciones (con tratamiento diferenciado EEE/GGG)
  - 3 identificadores / target

### 5. Pipeline de producción en Spark — 1,5 páginas
- Justificación: arquitectura escalable para producción real — NO por volumen del CSV
- Diagrama del flujo: ingestión CSV → dedup studentVle → features VLE → features assessment → ensamblado → export
- Dedup studentVle: dos tipos de duplicados y su tratamiento diferenciado
- Output: df_modelo_spark.csv (27.553 × 25) reproducible desde notebooks
- Cómo se usaría en producción: nuevas cohortes → mismo pipeline → predicción inmediata

### 6. Modelado comparativo y resultados — 4 páginas
- Tres modelos comparados: Regresión Logística, Random Forest, CatBoost
  - Tabla comparativa de AUC y F1 con umbral por defecto
  - Justificación de CatBoost como modelo final (categoricals nativos, robustez)
- Umbral optimizado (0,34 vs 0,50):
  - Justificación de negocio: coste de no intervenir > coste de sobreintervenir
  - AUC 0,737 | F1 0,64 | Recall 0,78 con umbral 0,34
- Análisis de robustez (solapamiento TRAIN/TEST):
  - TEST completo: AUC 0,737 | TEST sin solapamiento: AUC 0,730 ← número honesto
- Rendimiento por módulo con umbral 0,34 (tabla)
- Tuning: random search 20 iteraciones, spread de 0,008 — el techo está en las features

### 7. Interpretabilidad SHAP — 2 páginas
- Feature importance global (gráfico beeswarm o bar)
- Hallazgos principales con implicación de negocio:
  - nota_media y nota_min dominan: señal de evaluación en primeras semanas es clave
  - studied_credits: patrón no monótono, captura dificultad del módulo
  - num_of_prev_attempts: outliers con 3+ marcados fuertemente como riesgo
  - entrego_algo: redundante con nota_media — no aporta señal adicional
  - gender: 8ª en ranking pero efecto moderado — no preocupante
- EEE y GGG: el modelo predice solo con VLE y demografía, AUC > 0,69 en ambos

### 8. Conclusiones y líneas futuras — 1,5 páginas
- Conclusiones principales:
  - AUC 0,730 (estimación conservadora sobre estudiantes no vistos en TRAIN)
  - La señal de las primeras 4 semanas es suficiente para identificar riesgo
  - Features de evaluación > features VLE > demografía en importancia
  - El pipeline Spark permite aplicar el modelo a nuevas cohortes sin reescribir código
- Limitaciones documentadas:
  - 93 Withdrawn sin fecha de baja concentrados en TEST (asimetría de calidad)
  - BBB: señal comprimida en ventana (media de clics 4× menor que FFF)
  - 18 inscritos tardíos (date_registration > 27): features a 0 por ausencia
  - Pico de bajas en día 27 concentrado en 2013B, no patrón institucional universal
- Líneas futuras:
  - Ventanas más cortas (0-14, 0-21) para intervención más temprana
  - Features adicionales: pendiente de actividad semanal, tipos de recurso específicos
  - Comparación con LSTM u otros modelos secuenciales para capturar evolución temporal

### 9. Bibliografía — 0,5 páginas
- Dataset OULAD: Kuzilek et al. (2017)
- CatBoost: Prokhorenkova et al. (2018)
- SHAP: Lundberg & Lee (2017)
- Referencias contexto deserción online (2-3 papers)

---

## Anexos (sin límite de páginas)

- Anexo A: `01_EDA.ipynb` — Auditoría de calidad y análisis exploratorio
- Anexo B: `02_features.ipynb` — Pipeline de feature engineering (pandas)
- Anexo C: `03_modelo.ipynb` — Modelado, comparativa, SHAP, tuning
- Anexo D: `04_spark_features.ipynb` — Pipeline de producción en PySpark

---

## Pendiente antes de empezar a redactar

- [ ] Añadir Regresión Logística y Random Forest a `03_modelo.ipynb` para la comparativa (requisito de la guía: "diferentes técnicas")
- [ ] Decidir formato final de la memoria (DOCX recomendado para control de páginas)
- [ ] Recopilar gráficos clave de los notebooks para embeber en la memoria

---

## Estimación de páginas

| Sección | Páginas estimadas |
|---|---|
| 1. Introducción | 1,5 |
| 2. Dataset y auditoría | 2,0 |
| 3. EDA | 3,0 |
| 4. Metodología | 2,0 |
| 5. Pipeline Spark | 1,5 |
| 6. Modelado comparativo | 4,0 |
| 7. SHAP | 2,0 |
| 8. Conclusiones | 1,5 |
| 9. Bibliografía | 0,5 |
| **Total** | **~18 páginas** |

Margen de 2 páginas para ajustes y figuras que ocupen más de lo previsto.
