# Estado TFM — Resumen de sesión para continuidad

> Archivo de traspaso entre sesiones. Leer esto antes de cualquier sesión de trabajo en el TFM.
> Última actualización: 15 agosto 2026 (Flask API completada — GitHub + Gradio pendientes).

---

## 1. Dónde estamos

**H1 (Setup + EDA): COMPLETADO** — notebook limpiado y validado el 3 agosto.
**Auditoría de calidad de datos (cierre de H1): COMPLETA, 7 de 7 tablas perfiladas.** Ver sección 3.8 para todos los hallazgos — incluye un hallazgo importante (duplicados reales en studentVle.csv) que afecta directamente al pipeline de H2.
**H2 (Feature engineering + pipeline): COMPLETADO el 3 agosto.**
**H3 (Modelado baseline + comparativa): COMPLETADO el 14 agosto.**
**Flask API: COMPLETADA el 15 agosto.** Ver sección 14.

**H2 — Feature engineering (3 agosto):**
- Notebook: `02_features.ipynb`
- Output: `019_TFM/datos/df_modelo.csv` (27.553 filas, 25 columnas)
- Pipeline: dedup exacta student_vle → features VLE → features assessment → ensamblado → checks leakage → export
- Hallazgo crítico resuelto: `student_vle` tiene dos tipos de duplicados distintos. Exactos (787.170, error del dataset): eliminados con `drop_duplicates()`. Misma clave 5 cols con sum_click distinto (1.179.074 claves): sesiones legítimas del mismo día, se suman con `groupby().sum()`. El enfoque anterior de drop por 5 cols habría perdido 358.960 registros legítimos en la ventana.
- `vle_ventana` definida como días 0–27 exclusivamente; `vle_precurso` para días negativos. Features de comportamiento y pre-curso son señales no solapadas.
- Leakage verificado: `final_result` y `date_unregistration` excluidas. Solo NaN permitidos en `nota_media_ventana` y `nota_min_ventana` (EEE/GGG + no entregaron). Todos los asserts pasan.

**Limpieza de notebook EDA (3 agosto):**
- Notebook reordenado: Sección 1 = Auditoría (tablas crudas), Sección 2 = EDA analítico.
- Celdas 15a+15b+16 de evaluaciones unificadas en una sola celda limpia (filtro is_banked=0, denominador correcto con df_con_eval).
- Celda 17 (markdown suelto) eliminada.
- 18 headers markdown añadidos para estructurar secciones.
- Ejecutado limpio de arriba abajo con Restart & Run All.

Notebook activo: `019_TFM/notebooks/01_EDA.ipynb`
Datos en: `019_TFM/datos/OULAD/`

---

## 2. Decisiones de diseño cerradas

No reabrir sin motivo técnico sólido. Cada una tiene justificación documentada.

| Decisión | Valor elegido | Justificación |
|---|---|---|
| Variable objetivo | Binaria: riesgo=1 si final_result ∈ {Fail, Withdrawn}; 0 si {Pass, Distinction} | Accionable, limpia, balance 44/56 |
| Ventana de predicción | Días 0–27 (4 semanas) | Suficiente señal; explorar también 2 y 3 semanas |
| Filtro de activos | Excluir date_unregistration ≤ 27 | Estudiantes ya idos no son predicables en producción |\
| Leakage — date_unregistration | EXCLUIDA de features | Define el target, no puede ser predictor |
| Leakage — studentVle | Filtrar date ≤ 27 | Solo actividad dentro de la ventana |
| Leakage — studentAssessment | Filtrar date_submitted ≤ 27 y is_banked = 0 | Solo entregas nuevas en ventana |
| is_banked | Excluir de features de comportamiento; posible feature propio separado | No representa comportamiento actual |
| Split validación | TRAIN = 2013B + 2013J + 2014B → TEST = 2014J | Cronológico; TEST tiene los 7 módulos |
| Spark | Pipeline ingestión + feature engineering; entrenamiento en sklearn/CatBoost | Justificación: arquitectura escalable para producción, NO "por volumen del CSV" |
| Solapamiento de estudiantes TRAIN/TEST | No se rediseña el split. Se añade en H3 una métrica de robustez: AUC/F1 en TEST completo vs. TEST restringido a estudiantes que no aparecen en TRAIN | 14.2% del TEST activo (1.263 de 8.869) también está en TRAIN — no es testimonial, pero rediseñar el split rompe la lógica cronológica. Se mide el impacto en vez de asumirlo. |
| Duplicados en studentVle.csv | `drop_duplicates()` sin subset (solo exactos, 6 cols) antes de agregar; luego `groupby().sum()` para clics y `.nunique()` para días/sitios | Duplicados exactos reales: 787.170. Adicionalmente, 1.179.074 claves (5 cols) tienen sum_click distinto entre filas — sesiones legítimas del mismo día, se suman con groupby. El drop por 5 cols habría perdido 358.960 registros legítimos solo en la ventana. |
| Exclusión de code_module y code_presentation del modelo | EXCLUIDAS del feature set del modelo entrenado | No fue una decisión explícita en H3 — quedaron fuera por omisión. Se documenta en la memoria como elección de diseño: un modelo independiente del módulo generaliza a asignaturas no vistas en entrenamiento. Frase para memoria: "La exclusión de code_module como predictor permite que el modelo generalice a módulos no presentes en el entrenamiento, a costa de no capturar el riesgo base diferencial entre asignaturas." |
| API: features de entrada | 19 features (excluye regularidad y entrego_algo) | La API deriva regularidad = dias_activo/28 y entrego_algo = 1 if n_entregas_ventana > 0 else 0 internamente. |

**Aclaración crítica sobre B/J:**
- B = febrero, J = octubre
- Orden cronológico: 2013B → 2013J → 2014B → 2014J
- TEST = 2014J

---

## 3. Hallazgos del EDA

### Dataset tras filtro
- Estudiantes totales en OULAD: 32.593
- Estudiantes activos en día 27 (muestra de modelado): **27.553**
- Excluidos (baja ≤ día 27): 5.040 — usar con cautela, pico concentrado en cohortes antiguas (2013B), no patrón institucional general.
- Balance de clases: **44.2% riesgo / 55.8% no riesgo** — manejable sin oversampling

### Estructura del dataset
- 7 módulos: AAA, BBB, CCC, DDD, EEE, FFF, GGG
- EEE y GGG **no tienen evaluaciones en los primeros 27 días**
- CCC solo existe desde 2014; AAA es el más pequeño (718 estudiantes activos)

### Riesgo por módulo (de mayor a menor)
CCC 62.2% → DDD 58.4% → FFF 53.0% → BBB 52.5% → EEE 43.8% → GGG 40.3% → AAA 29.0%

### Riesgo por presentación
TEST (2014J) = 51.5% → similar a la media global. Sin distributional shift relevante.

### Predictores demográficos (de mayor a menor señal)
1. `num_of_prev_attempts`: 0→41.8%, 1→58.8%, 2→65.3%, 3→71.2%. A partir de 4 muestra insuficiente — no citar.
2. `highest_education`: gradiente de 36pp. No Formal 70.3% → Postgrad 34.5%
3. `imd_band`: gradiente socioeconómico. "Missing" → 34.3% (probablemente internacionales).
4. `disability`: Y → 61.9% vs N → 51.8%
5. `age_band`: 0-35 → 55%; 35-55 → 47.8%; 55+ → 38.4%
6. `gender`: diferencia mínima (2pp)

### Señal de comportamiento (studentVle)
- Estudiantes SIN ningún clic en ventana: 940 (3.4%) → **82.1% son riesgo=1**
- Mediana de clics: no riesgo = 297, riesgo = 166 (ratio ~1.8)
- Actividad pre-curso (días negativos): ratio 1.74 — la motivación pre-inicio ya diferencia grupos

### Señal de evaluaciones (studentAssessment)
- No riesgo: 97.9% entregaron algo; Riesgo: 78.4% entregaron algo
- is_banked: 1.839 entregas bancadas — excluir de features de comportamiento

---

## 3.8 Auditoría de calidad de datos (cierre H1) — COMPLETA, 7/7 tablas

Ver versión completa en el proyecto de Claude para todos los hallazgos detallados.
Puntos clave:
- `student_vle`: 1.43M duplicados exactos confirmados en CSV crudo. Fix: drop_duplicates() + groupby().sum()
- Solapamiento TRAIN/TEST: 14.2% del TEST (1.263 de 8.869) también está en TRAIN — medido, no ignorado.
- 93 Withdrawn sin date_unregistration concentrados en 2014J (TEST) — asimetría de calidad, documentar como limitación.
- GGG: TMA/CMA con weight=0 estructuralmente — sin señal de evaluación incluso fuera de ventana.

---

## 4. Features construidas en H2

VLE (9): total_clics, dias_activo, clics_semana_1-4, clics_precurso, regularidad, tipos_actividad
Assessment (4): n_entregas_ventana, entrego_algo, nota_media_ventana, nota_min_ventana
Demográficas (10): code_module, code_presentation, gender, region, highest_education, imd_band, age_band, num_of_prev_attempts, studied_credits, disability

---

## 7. Terminología acordada

- ✅ "nivel socioeconómico del entorno del estudiante" — NO "deprivación económica"
- ✅ Spark se justifica por "arquitectura escalable para producción real" — NO "por volumen del CSV"
- ⚠️ "período de desistimiento contractual" — usar con matiz, pico concentrado en cohortes antiguas
- ✅ "unidad de análisis = matrícula (estudiante × módulo × presentación)"

---

## 8. Forma de trabajo

- Belén ejecuta. Claude guía paso a paso, explica el por qué antes de cada celda.
- No se hacen cosas del tirón: el objetivo es que Belén pueda defender cada decisión.
- Si hay que acelerar, Belén lo pide explícitamente.
- Errores: se señalan, se explican, se corrigen. No se maquillan.

---

## 9. Próximos pasos

1. ~~Limpiar notebook EDA~~ ✅
2. ~~Crear `02_features.ipynb`~~ ✅
3. ~~Construir pipeline de features~~ ✅
4. ~~Ensamblar df_modelo~~ ✅
5. ~~Verificar leakage~~ ✅
6. ~~H3 baseline~~ ✅
7. ~~Pipeline Spark~~ ✅
8. ~~Comparativa LR/RF/CatBoost~~ ✅
9. ~~Serializar modelo con joblib~~ ✅
10. ~~Flask API (`05_flask_api.py` + `test_api.py`)~~ ✅ 15 agosto.

**Pendiente:**
- [ ] **PRÓXIMA TAREA** `requirements.txt` + `.gitignore` → subir a GitHub
- [ ] Deploy Flask API en Render → URL pública REST
- [ ] `06_gradio_app.py` → Hugging Face Spaces → URL pública con formulario
- [ ] Decidir formato final memoria (DOCX recomendado)
- [ ] Recopilar gráficos clave de los notebooks para la memoria

---

## 10. Resultados H3 — Modelado baseline (14 agosto)

**Modelo:** CatBoostClassifier, 163 iteraciones, depth=6, lr=0.05.
**Split:** TRAIN 18.334 / TEST 9.219. Balance: TRAIN 45.8% / TEST 40.8% riesgo.

**Métricas umbral 0.34:** AUC 0.7375 | F1 0.64 | Recall 0.78
**Número honesto (sin solapamiento):** AUC 0.730 | F1 0.617

**SHAP:** nota_media y nota_min dominan. studied_credits patrón no monótono. entrego_algo redundante.

**Rendimiento por módulo (umbral 0.34):**
AAA: AUC 0.686, F1 0.487 | BBB: AUC 0.657, F1 0.538 | CCC: AUC 0.791, F1 0.733
DDD: AUC 0.775, F1 0.701 | EEE: AUC 0.763, F1 0.575 | FFF: AUC 0.789, F1 0.672 | GGG: AUC 0.690, F1 0.587

**Tuning:** AUC CV 0.706–0.714. Modelo tuned peor → se mantiene baseline.

---

## 11. Spark — COMPLETADO (14 agosto)

Notebook: `04_spark_features.ipynb`. Output: `df_modelo_spark.csv` en Databricks Workspace.

---

## 12. Productivización — plan completo

1. ~~`05_flask_api.py`~~ ✅
2. GitHub — repo público (próxima sesión)
3. Render — deploy Flask API → URL pública REST
4. `06_gradio_app.py` → Hugging Face Spaces → URL con formulario visual

---

## 13. Comparativa de modelos (14 agosto)

| Modelo | AUC | F1 (u=0.34) |
|---|---|---|
| Regresión Logística | 0,7068 | 0,6329 |
| Random Forest | 0,7294 | 0,6383 |
| CatBoost | **0,7375** | **0,6426** |

---

## 14. Flask API — COMPLETADA (15 agosto)

**Archivos:** `019_TFM/05_flask_api.py` + `019_TFM/test_api.py`

**Diseño:**
- 19 features de entrada (regularidad y entrego_algo se derivan internamente)
- `GET /health` → `{"status": "ok"}`
- `POST /api/v01/predice` → `{"riesgo": 0/1, "probabilidad": 0.xxxx}`
- Umbral: 0.34 | `use_reloader=False` (evita bucle por checkpoints Jupyter)

**Validación:**
- Estudiante bajo riesgo → `{"riesgo": 0, "probabilidad": 0.1456}` ✅
- Estudiante alto riesgo → `{"riesgo": 1, "probabilidad": 0.9165}` ✅

**Para arrancar:**
```
# Terminal 1 (envtfm activado, desde 019_TFM/)
python 05_flask_api.py

# Terminal 2 (envtfm activado, desde 019_TFM/)
python test_api.py
```

**Activar entorno virtual en PowerShell:**
```
# Desde Master_busines_intelligence_data_analyst/
envtfm\.venv\Scripts\Activate.ps1
# Si da error de política:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
