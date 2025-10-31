"""
Monday.com API integration.
Fetches project management data for map visualization and inserts into PostgreSQL.
"""
import json
import requests
import psycopg2
import pandas as pd
from database.queries import INSERT_HARDWARE
from config import MONDAY_API_KEY, DB_CONFIG


def get_monday_data():
    """
    Pobiera dane biletów z Monday.com (do wizualizacji mapy).
    """
    url = 'https://api.monday.com/v2'
    headers = {'Authorization': MONDAY_API_KEY, 'Content-Type': 'application/json'}

    with open('static/queries/tickets.graphql', 'r') as file:
        graphql_query = file.read()

    items_response = requests.post(url, json={'query': graphql_query}, headers=headers)
    labels_map = {}
    items_list = []

    if items_response.status_code == 200:
        raw_json = items_response.json()
        items = raw_json['data']['boards'][0]['groups'][0]['items_page']['items']
        for item in items:
            row = {'id': item['id'], 'name': item['name']}
            for col in item['column_values']:
                col_id = col['id']
                if col_id in labels_map:
                    dropdown_values = col['value']
                    if dropdown_values:
                        value_ids = json.loads(dropdown_values).get('ids', [])
                        row[col_id] = ', '.join(
                            [labels_map[col_id].get(str(v_id), str(v_id)) for v_id in value_ids]
                        )
                    else:
                        row[col_id] = col['text']
                else:
                    row[col_id] = col['text']
            items_list.append(row)

    return pd.DataFrame(items_list)


def get_monday_hardware():
    """
    Pobiera dane hardware z Monday.com (surowe items).
    """
    url = 'https://api.monday.com/v2'
    headers = {'Authorization': MONDAY_API_KEY, 'Content-Type': 'application/json'}

    with open('static/queries/hardware.graphql', 'r') as file:
        graphql_query = file.read()

    items_response = requests.post(url, json={'query': graphql_query}, headers=headers)
    print("Status code:", items_response.status_code)

    try:
        raw_json = items_response.json()
        items = raw_json['data']['boards'][0]['groups'][0]['items_page']['items']
        return items
    except Exception as e:
        print("Błąd przy wyciąganiu items:", e)
        print("Odpowiedź tekstowa:", items_response.text[:500])
        return []


def map_item_to_record(item: dict) -> dict:
    """
    Mapuje pojedynczy item z Monday API na rekord SQL.
    """
    cols = {c["id"]: c["text"] for c in item.get("column_values", [])}
    serial = int(item.get("name", "0").lstrip("0") or 0)

    return {
        "serial": serial,
        "nadlesnictwo": cols.get("tekst__1", ""),
        "wieza": cols.get("tekst7__1", ""),
        "status": cols.get("status9", ""),
        "instalator": cols.get("status_1__1", ""),
        "rodzaj": cols.get("label4__1", ""),
        "data_produkcji": cols.get("data", None),
        "obudowa": cols.get("label8__1", ""),
        "enkoder_katow": cols.get("label3__1", ""),
        "enkoder_obrazu": cols.get("label0__1", ""),
        "driver_silnika": cols.get("label6__1", ""),
        "procesor": cols.get("label5__1", ""),
        "modul": cols.get("label7__1", ""),
        "data_firmware": cols.get("data6__1", None),
        "wylacznik_glowicy": cols.get("sprawd___1", ""),
        "adres": cols.get("tekst_mknaq1qa", ""),
        "ip_enkodera": cols.get("tekst_mknat611", ""),
        "kanal_CH": cols.get("tekst_mknawgmc", ""),
        "ip_moxy": cols.get("tekst_mknaz218", ""),
        "uwagi": cols.get("tekst8__1", "")
    }


def map_items_to_records(items: list) -> list[dict]:
    """
    Mapuje listę items na listę rekordów SQL.
    """
    return [map_item_to_record(item) for item in items]


def insert_to_postgres(records: list[dict]):
    """
    Wstawia rekordy do bazy PostgreSQL.
    """
    if not records:
        print("Brak rekordów do wstawienia.")
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for record in records:
        cur.execute(INSERT_HARDWARE, record)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Wstawiono/zaaktualizowano {len(records)} rekordów.")


if __name__ == "__main__":
    items = get_monday_hardware()
    records = map_items_to_records(items)

    # opcjonalnie debug w Pandas
    df = pd.DataFrame(records)
    print(df.head())

    insert_to_postgres(records)
