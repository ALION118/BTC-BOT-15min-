import pandas as pd

archivo = "historial.csv"

try:
    df = pd.read_csv(
        archivo,
        names=["hora", "senal", "entrada", "salida", "resultado"]
    )

    total = len(df)
    wins = len(df[df["resultado"] == "WIN"])
    loss = len(df[df["resultado"] == "LOSS"])
    winrate = (wins / total) * 100 if total > 0 else 0

    print("RESUMEN DEL BOT")
    print("----------------")
    print("Total operaciones:", total)
    print("WIN:", wins)
    print("LOSS:", loss)
    print("Winrate:", round(winrate, 2), "%")

    print("\nLONG:")
    print(df[df["senal"] == "LONG"]["resultado"].value_counts())

    print("\nSHORT:")
    print(df[df["senal"] == "SHORT"]["resultado"].value_counts())

except FileNotFoundError:
    print("Todavía no existe historial.csv")
    print("Deja correr el bot hasta que genere señales.")
