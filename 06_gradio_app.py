"""
06_gradio_app.py — Demo visual: detección de riesgo de abandono (OULAD)
Desplegado como segundo Web Service en Render (start command: python 06_gradio_app.py).

Diseño: 19 features de entrada (igual que la Flask API).
Las features derivadas 'regularidad' y 'entrego_algo' se calculan internamente.
Si n_entregas_ventana == 0, las notas se pasan como NaN (no como 0) al modelo,
que es el comportamiento correcto para módulos sin evaluaciones en ventana (EEE, GGG).
"""
import os
import joblib
import pandas as pd
import gradio as gr

# ── Carga del modelo ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "datos", "modelo_catboost.joblib")
modelo = joblib.load(MODEL_PATH)
UMBRAL = 0.34

# ── Catálogos de categorías (valores exactos del dataset OULAD) ───────────────
REGIONES = sorted([
    "East Anglian Region", "East Midlands Region", "Ireland",
    "London Region", "North Region", "North Western Region",
    "Scotland", "South East Region", "South Region",
    "South West Region", "Wales", "West Midlands Region", "Yorkshire Region"
])
EDUCACION = [
    "No Formal Quals",
    "Lower Than A Level",
    "A Level or Equivalent",
    "HE Qualification",
    "Post Graduate Qualification",
]
IMD_BAND = [
    "0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
    "50-60%", "60-70%", "70-80%", "80-90%", "90-100%", "Missing",
]


# ── Función de predicción ─────────────────────────────────────────────────────
def predice(
    gender, region, highest_education, imd_band, age_band,
    num_of_prev_attempts, studied_credits, disability,
    total_clics, clics_semana_1, clics_semana_2, clics_semana_3, clics_semana_4,
    dias_activo, tipos_actividad, clics_precurso,
    n_entregas_ventana, nota_media_ventana, nota_min_ventana,
):
    n_entregas = int(n_entregas_ventana)

    # Si no hay entregas, las notas deben ser NaN (no 0) — son distintas señales
    nota_media = (
        None if n_entregas == 0
        else (float(nota_media_ventana) if nota_media_ventana is not None else None)
    )
    nota_min = (
        None if n_entregas == 0
        else (float(nota_min_ventana) if nota_min_ventana is not None else None)
    )

    fila = {
        "gender": gender,
        "region": region,
        "highest_education": highest_education,
        "imd_band": imd_band,
        "age_band": age_band,
        "num_of_prev_attempts": int(num_of_prev_attempts),
        "studied_credits": int(studied_credits),
        "disability": disability,
        "total_clics": int(total_clics),
        "clics_semana_1": int(clics_semana_1),
        "clics_semana_2": int(clics_semana_2),
        "clics_semana_3": int(clics_semana_3),
        "clics_semana_4": int(clics_semana_4),
        "dias_activo": int(dias_activo),
        "tipos_actividad": int(tipos_actividad),
        "clics_precurso": int(clics_precurso),
        "n_entregas_ventana": n_entregas,
        "nota_media_ventana": nota_media,
        "nota_min_ventana": nota_min,
        # Features derivadas (misma lógica que Flask API)
        "regularidad": int(dias_activo) / 28,
        "entrego_algo": 1 if n_entregas > 0 else 0,
    }

    df = pd.DataFrame([fila])[modelo.feature_names_]
    prob = float(modelo.predict_proba(df)[0, 1])
    riesgo = int(prob >= UMBRAL)

    if riesgo == 1:
        etiqueta = f"🔴  RIESGO ALTO  —  probabilidad de abandono/suspenso: {prob:.1%}"
        accion = "Se recomienda contacto proactivo con el estudiante antes de la semana 5."
    else:
        etiqueta = f"🟢  SIN RIESGO DETECTADO  —  probabilidad: {prob:.1%}"
        accion = "Seguimiento estándar. Revisar si la probabilidad supera el 25% en próximas semanas."

    return etiqueta, accion


# ── Interfaz Gradio ───────────────────────────────────────────────────────────
with gr.Blocks(title="OULAD — Riesgo de Abandono") as demo:

    gr.Markdown("""
    # 🎓 Detección de Riesgo de Abandono
    **Dataset:** Open University Learning Analytics Dataset (OULAD) · **Modelo:** CatBoostClassifier
    **Ventana de predicción:** días 0–27 (4 primeras semanas) · **Umbral de intervención:** 0.34

    Introduce el perfil del estudiante al cierre de la semana 4.
    > *Si el módulo no tiene evaluaciones en la ventana (EEE, GGG): pon Entregas = 0.
    Las notas se ignorarán automáticamente.*
    """)

    with gr.Row():

        # ── Columna izquierda: perfil demográfico ─────────────────────────────
        with gr.Column(scale=1):
            gr.Markdown("#### 👤 Perfil demográfico")
            gender = gr.Dropdown(["M", "F"], label="Género", value="M")
            region = gr.Dropdown(REGIONES, label="Región (UK)", value="London Region")
            highest_education = gr.Dropdown(
                EDUCACION, label="Nivel educativo más alto",
                value="A Level or Equivalent"
            )
            imd_band = gr.Dropdown(
                IMD_BAND, label="Nivel socioeconómico del entorno (IMD)",
                value="50-60%"
            )
            age_band = gr.Dropdown(
                ["0-35", "35-55", "55<="], label="Franja de edad", value="0-35"
            )
            disability = gr.Dropdown(
                ["N", "Y"], label="Discapacidad declarada", value="N"
            )
            num_of_prev_attempts = gr.Slider(
                0, 6, value=0, step=1,
                label="Intentos previos en este módulo"
            )
            studied_credits = gr.Slider(
                30, 660, value=60, step=30,
                label="Créditos matriculados este semestre"
            )

        # ── Columna derecha: comportamiento + evaluaciones ────────────────────
        with gr.Column(scale=1):
            gr.Markdown("#### 📊 Comportamiento en el VLE (días 0–27)")
            total_clics = gr.Number(
                value=200, label="Total de clics en la ventana",
                minimum=0, precision=0
            )
            with gr.Row():
                clics_semana_1 = gr.Number(
                    value=50, label="Semana 1 (días 0–6)", minimum=0, precision=0
                )
                clics_semana_2 = gr.Number(
                    value=60, label="Semana 2 (días 7–13)", minimum=0, precision=0
                )
            with gr.Row():
                clics_semana_3 = gr.Number(
                    value=50, label="Semana 3 (días 14–20)", minimum=0, precision=0
                )
                clics_semana_4 = gr.Number(
                    value=40, label="Semana 4 (días 21–27)", minimum=0, precision=0
                )
            dias_activo = gr.Slider(
                0, 28, value=14, step=1,
                label="Días con al menos un clic"
            )
            tipos_actividad = gr.Slider(
                0, 13, value=4, step=1,
                label="Tipos de recurso distintos usados"
            )
            clics_precurso = gr.Number(
                value=0, label="Clics pre-curso (días negativos)",
                minimum=0, precision=0
            )

            gr.Markdown("#### 📝 Evaluaciones en la ventana")
            n_entregas_ventana = gr.Number(
                value=1,
                label="Entregas realizadas (pon 0 si el módulo no tiene evaluaciones en la ventana)",
                minimum=0, precision=0
            )
            nota_media_ventana = gr.Number(
                value=75,
                label="Nota media de entregas (0–100) — ignorado si Entregas = 0",
                minimum=0, maximum=100
            )
            nota_min_ventana = gr.Number(
                value=70,
                label="Nota mínima de entregas (0–100) — ignorado si Entregas = 0",
                minimum=0, maximum=100
            )

    btn = gr.Button("🔍  Predecir riesgo de abandono", variant="primary", size="lg")

    with gr.Row():
        resultado = gr.Textbox(label="Resultado", lines=1, interactive=False)
        accion = gr.Textbox(label="Acción recomendada", lines=2, interactive=False)

    btn.click(
        fn=predice,
        inputs=[
            gender, region, highest_education, imd_band, age_band,
            num_of_prev_attempts, studied_credits, disability,
            total_clics, clics_semana_1, clics_semana_2, clics_semana_3, clics_semana_4,
            dias_activo, tipos_actividad, clics_precurso,
            n_entregas_ventana, nota_media_ventana, nota_min_ventana,
        ],
        outputs=[resultado, accion],
    )

    gr.Markdown("""
    ---
    TFM — Máster en Data Science y Business Intelligence · Universidad Complutense de Madrid
    """)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
