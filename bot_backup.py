#!/usr/bin/env python3

import requests
import time
import json
import csv
from datetime import datetime

precio_anterior = 0
senal_pendiente = None

UMBRAL = 30
ESPERA_EVALUACION = 300  # 5 minutos
INTERVALO = 5

print("BOT BTC INICIADO")
print("Leyendo BTC cada", INTERVALO, "segundos")
print("----------------")

def leer_btc():

    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

    response = requests.get(url, timeout=5)

    data = response.json()

    return float(data["data"]["amount"])


def leer_polymarket():

    url = "https://gamma-api.polymarket.com/markets"

    response = requests.get(url, timeout=5)

    data = response.json()

    encontrados = 0

    for mercado in data:

        titulo = mercado.get("question", "")

        if "bitcoin" in titulo.lower():

            print("POLYMARKET:", titulo)

            encontrados = encontrados + 1

            if encontrados >= 3:
                break

    url = "https://gamma-api.polymarket.com/markets"

    response = requests.get(url, timeout=5)

    data = response.json()

    for mercado in data:

        titulo = mercado.get("question", "")

        if "bitcoin" in titulo.lower():

            print("POLYMARKET:", titulo)

            break
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    response = requests.get(url, timeout=5)
    data = response.json()
    return float(data["data"]["amount"])

def guardar_resultado(hora, senal, precio_entrada, precio_salida, resultado):
    with open("historial.csv", "a", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([hora, senal, precio_entrada, precio_salida, resultado])

while True:
    try:
        precio = leer_btc()
        leer_polymarket()
        ahora = datetime.now()

        if precio_anterior != 0:
            diferencia = precio - precio_anterior

            print("BTC:", precio)
            print("Cambio:", round(diferencia, 2))

            if senal_pendiente:
                tiempo_pasado = time.time() - senal_pendiente["timestamp"]

                if tiempo_pasado >= ESPERA_EVALUACION:
                    entrada = senal_pendiente["precio"]
                    tipo = senal_pendiente["tipo"]

                    if tipo == "LONG":
                        resultado = "WIN" if precio > entrada else "LOSS"
                    else:
                        resultado = "WIN" if precio < entrada else "LOSS"

                    print("RESULTADO", tipo, resultado)

                    guardar_resultado(
                        senal_pendiente["hora"],
                        tipo,
                        entrada,
                        precio,
                        resultado
                    )

                    senal_pendiente = None

            if senal_pendiente is None:
                if diferencia > UMBRAL:
                    print("SUBIDA FUERTE 🚀")
                    print("ALERTA LONG")

                    senal_pendiente = {
                        "tipo": "LONG",
                        "precio": precio,
                        "timestamp": time.time(),
                        "hora": ahora.strftime("%Y-%m-%d %H:%M:%S")
                    }

                elif diferencia < -UMBRAL:
                    print("BAJADA FUERTE 🔻")
                    print("ALERTA SHORT")

                    senal_pendiente = {
                        "tipo": "SHORT",
                        "precio": precio,
                        "timestamp": time.time(),
                        "hora": ahora.strftime("%Y-%m-%d %H:%M:%S")
                    }

                else:
                    print("Movimiento normal")

            print("----------------")

        precio_anterior = precio

    except Exception as e:
        print("Error:", e)

    time.sleep(INTERVALO)
