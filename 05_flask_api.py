## Sección 1. Imports y constantes
import os
import joblib
import pandas as pd
from flask import Flask, request, jsonify

UMBRAL = 0.34

FEATURES_ENTRADA = [
    "gender", "region", "highest_education", "imd_band", "age_band",
    "num_of_prev_attempts", "studied_credits", "disability",
    "total_clics", "clics_semana_1", "clics_semana_2", "clics_semana_3", "clics_semana_4",
    "dias_activo", "tipos_actividad", "clics_precurso",
    "n_entregas_ventana", "nota_media_ventana", "nota_min_ventana"
]

## Sección 2. Carga del modelo y creación de la app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "datos", "modelo_catboost.joblib")

modelo = joblib.load(MODEL_PATH)

app = Flask(__name__)

## Sección 3. Endpoint /health
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

## Sección 4. Endpoint /api/v01/predice
@app.route("/api/v01/predice", methods=["POST"])
def predice():
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "El cuerpo de la petición debe ser JSON"}), 400

    faltantes = [f for f in FEATURES_ENTRADA if f not in datos]
    if faltantes:
        return jsonify({"error": f"Campos faltantes: {faltantes}"}), 400

    fila = {f: datos[f] for f in FEATURES_ENTRADA}
    fila["regularidad"] = fila["dias_activo"] / 28
    fila["entrego_algo"] = 1 if fila["n_entregas_ventana"] > 0 else 0

    df = pd.DataFrame([fila])[modelo.feature_names_]

    prob = float(modelo.predict_proba(df)[0, 1])
    riesgo = int(prob >= UMBRAL)

    return jsonify({"riesgo": riesgo, "probabilidad": round(prob, 4)})

## Sección 5. Arranque

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)

