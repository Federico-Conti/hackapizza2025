import sqlite3
import os

def merge_databases(primary_db, secondary_db):
    # Controllo che i file esistano
    if not os.path.exists(primary_db) or not os.path.exists(secondary_db):
        print("Uno o entrambi i file database non esistono nella cartella di lavoro.")
        return

    try:
        # Connessione ai database
        primary_conn = sqlite3.connect(primary_db)
        secondary_conn = sqlite3.connect(secondary_db)

        primary_cursor = primary_conn.cursor()
        secondary_cursor = secondary_conn.cursor()

        # Recupera l'elenco delle tabelle nel database primario
        primary_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in primary_cursor.fetchall()]

        for table in tables:
            print(f"Unendo la tabella: {table}")

            # Copia la struttura della tabella se non esiste
            primary_cursor.execute(f"PRAGMA table_info({table});")
            columns = primary_cursor.fetchall()

            column_definitions = ", ".join([f"{col[1]} {col[2]}" for col in columns])

            create_table_query = f"CREATE TABLE IF NOT EXISTS {table} ({column_definitions});"
            secondary_cursor.execute(create_table_query)

            # Copia i dati
            primary_cursor.execute(f"SELECT * FROM {table};")
            rows = primary_cursor.fetchall()

            placeholders = ", ".join(["?" for _ in columns])
            insert_query = f"INSERT INTO {table} VALUES ({placeholders});"

            secondary_cursor.executemany(insert_query, rows)

        # Commit delle modifiche
        secondary_conn.commit()
        print("Unione completata con successo!")

    except sqlite3.Error as e:
        print(f"Errore durante l'unione dei database: {e}")

    finally:
        primary_conn.close()
        secondary_conn.close()

if __name__ == "__main__":
    primary_db = "restaurants.db"
    secondary_db = "manuale.db"

    merge_databases(primary_db, secondary_db)
