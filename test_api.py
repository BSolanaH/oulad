import requests

URL = "http://127.0.0.1:5000/api/v01/predice"

estudiante_bajo_riesgo = {
    "gender": "F",
    "region":"South East Region",
    "highest_education": "HE Qualification",
    "imd_band": "60-70%",
    "age_band": "35-55",
    "num_of_prev_attempts": 0,
    "studied_credits": 60,
    "disability": "N",
    "total_clics": 350,
    "clics_semana_1": 80,
    "clics_semana_2": 90,
    "clics_semana_3": 100,
    "clics_semana_4": 80,
    "dias_activo": 20,
    "tipos_actividad": 5,
    "clics_precurso": 50,
    "n_entregas_ventana": 2,
    "nota_media_ventana": 78.0,
    "nota_min_ventana": 72.0
}

estudiante_alto_riesgo = {
    "gender": "M",
    "region":"East Midlands Region",
    "highest_education": "No Formal quals",
    "imd_band": "0-10%",
    "age_band": "0-35",
    "num_of_prev_attempts": 2,
    "studied_credits": 60,
    "disability": "N",
    "total_clics": 25,
    "clics_semana_1": 15,
    "clics_semana_2": 10,
    "clics_semana_3": 0,
    "clics_semana_4": 0,
    "dias_activo": 3,
    "tipos_actividad": 1,
    "clics_precurso": 0,
    "n_entregas_ventana": 0,
    "nota_media_ventana": None,
    "nota_min_ventana": None
}

for nombre, caso in [("BAJO RIESGO", estudiante_bajo_riesgo), ("ALTO RIESGO", estudiante_alto_riesgo)]:
    r = requests.post(URL, json=caso)
    print(f"\n--- {nombre} ---")
    print(r.json())



