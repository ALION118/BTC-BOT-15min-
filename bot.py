#!/usr/bin/env python3

import csv
import json
import os
import time
from datetime import datetime
from pathlib import Path

import requests
from telegram import Bot

BASE_DIR = Path(__file__).resolve().parent
HISTORIAL = BASE_DIR / "historial.csv"

precio_anterior = 0
senal_pendiente = None

UMBRAL = 200
ESPERA_EVALUACION = 900
INTERVALO = 5


def crear_bot_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Telegram desactivado: falta TELEGRAM_BOT_TOKEN")
        return None
    return Bot(token=token)


telegram_bot = crear_bot_telegram()
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def enviar_telegram(mensaje):
    if not telegram_bot or not CHAT_ID:
        return

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
    response.raise_for_status()
    data = response.json()
    return float(data["data"]["amount"])


def leer_polymarket():
    url = "https://gamma-api.polymarket.com/markets"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
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
    with HISTORIAL.open("a", newline="") as archivo:
        writer = csv.writer(archivo)
        writer.writerow([hora, senal, precio_entrada, precio_salida, resultado])


def evaluar_senal(precio):
    global senal_pendiente

    tiempo_pasado = time.time() - senal_pendiente["timestamp"]
    if tiempo_pasado < ESPERA_EVALUACION:
        return

    entrada = senal_pendiente["precio"]
    tipo = senal_pendiente["tipo"]

    if tipo == "LONG":
        resultado = "WIN" if precio > entrada else "LOSS"
    else:
        resultado = "WIN" if precio < entrada else "LOSS"

    print("RESULTADO", tipo, resultado)
    guardar_resultado(senal_pendiente["hora"], tipo, entrada, precio, resultado)
    senal_pendiente = None


def crear_senal(tipo, precio, ahora):
    return {
        "tipo": tipo,
        "precio": precio,
        "timestamp": time.time(),
        "hora": ahora.strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    global precio_anterior, senal_pendiente

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
                    evaluar_senal(precio)

                if senal_pendiente is None:
                    if diferencia > UMBRAL:
                        print("SUBIDA FUERTE 🚀")
                        print("ALERTA LONG")
                        enviar_telegram("🚀 ALERTA LONG BTC")
                        senal_pendiente = crear_senal("LONG", precio, ahora)

                    elif diferencia < -UMBRAL:
                        print("BAJADA FUERTE 🔻")
                        print("ALERTA SHORT")
                        enviar_telegram("📉 ALERTA SHORT BTC")
                        senal_pendiente = crear_senal("SHORT", precio, ahora)

                    else:
                        print("Movimiento normal")

                print("----------------")

            precio_anterior = precio

        except requests.RequestException as e:
            print("Error de conexión:", e)
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            print("Error leyendo datos:", e)
        except Exception as e:
            print("Error inesperado:", e)

        time.sleep(INTERVALO)


if __name__ == "__main__":
    main()
