from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# Función para obtener el código de moneda basado en el país
def obtener_codigo_moneda(pais: str):
    url = f"https://restcountries.com/v3.1/name/{pais}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Verifica si el país tiene información de moneda
        if 'currencies' in data[0]:
            moneda = list(data[0]['currencies'].keys())[0]  # Obtiene el código de la moneda
            return moneda
        else:
            return None
        
    except requests.exceptions.RequestException:
        return None

# Función para obtener la tasa de cambio
def obtener_tasa_cambio(base_currency: str, target_currency: str):
    api_key = "c7ba844bf9b0c34ad36a66ba"  # Reemplaza con tu API key
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base_currency}/{target_currency}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        tasa = data['conversion_rate']  # Extrae la tasa de cambio
        return tasa
    except requests.exceptions.RequestException:
        return None

# Modelo de datos para la solicitud de conversión
class ConversionRequest(BaseModel):
    pais_origen: str
    pais_destino: str
    amount: float

# Ruta GET para obtener el código de moneda por país
@app.get("/codigo_moneda/{pais}")
def get_codigo_moneda(pais: str):
    codigo = obtener_codigo_moneda(pais)
    if codigo:
        return {"pais": pais, "codigo_moneda": codigo}
    else:
        raise HTTPException(status_code=404, detail="No se pudo obtener el código de moneda")

# Ruta POST para convertir monedas
@app.post("/convertir")
def convertir_monedas(request: ConversionRequest):
    base_currency = obtener_codigo_moneda(request.pais_origen)
    target_currency = obtener_codigo_moneda(request.pais_destino)
    
    if not base_currency or not target_currency:
        raise HTTPException(status_code=404, detail="No se pudo encontrar la moneda de uno o ambos países")
    
    tasa = obtener_tasa_cambio(base_currency, target_currency)
    if tasa:
        resultado = request.amount * tasa
        return {
            "monto": request.amount,
            "Pais_origen": base_currency,
            "Pais_destino": target_currency,
            "resultado": resultado
        }
    else:
        raise HTTPException(status_code=500, detail="No se pudo realizar la conversión")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
