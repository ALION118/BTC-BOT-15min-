#!/usr/bin/env python3

import requests
import time
import csv
from telegram import Bot
import json
from datetime import datetime

TOKEN = "8737427032:AAGx3rwTYONW5eAfIOGkpz4jnKkisLrCmB8"
CHAT_ID = "132352118"

telegram_bot = Bot(token=TOKEN)

precio_anterior = 0
senal_pendiente = None

UMBRAL =200
ESPERA_EVALUACION = 900
INTERVALO = 5

def enviar_telegram(mensaje):
    try:
        telegram_bot.send_message(
            chat_id=CHAT_ID,
            text=mensaje
        )
    except Exception as e:
        print("Error Telegram:", e)

def leer_btc():
    url = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    response = requests.get(url, timeout=5)
    data = response.json()
    return float(data["data"]["amount"])

def leer_polymarket():
    url = "https://gamma-api.polymarket.com/markets"
    response = requests.get(url, timeout=5)
    data = response.json()

    for mercado in data:
        titulo = mercado.get("question", "")

        if "bitcoin" in titulo.lower():
            print("POLYMARKET:", titulo)

            precios = mercado.get("outcomePrices", [])
           
            if isinstance(precios, str):
                precios = json.loads(precios)

            if len(precios) >= 2:
                yes = float(precios[0]) * 100
                no = float(precios[1]) * 100

                print("YES:", round(yes, 2), "%")
                print("NO:", round(no, 2), "%")

            break

def guardar_resultado(hora, senal, precio_entrada, precio_salida, resultado):
    with open("historial.csv", "a", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([hora, senal, precio_entrada, precio_salida, resultado])

print("BOT BTC + POLYMARKET INICIADO")
print("Leyendo cada", INTERVALO, "segundos")
print("----------------")

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
                    enviar_telegram("🚀 ALERTA LONG BTC")

                    senal_pendiente = {
                        "tipo": "LONG",
                        "precio": precio,
                        "timestamp": time.time(),
                        "hora": ahora.strftime("%Y-%m-%d %H:%M:%S")
                    }

                elif diferencia < -UMBRAL:
                    print("BAJADA FUERTE 🔻")
                    print("ALERTA SHORT")
                    enviar_telegram("📉 ALERTA SHORT BTC")

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
