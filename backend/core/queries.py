# -*- coding: utf-8 -*-
"""
SQL queries for database operations.
Contains all SQL statements used throughout the application.
"""

# Queries for institutions (PAD)
GET_ALL_INSTITUTIONS = """
    SELECT "ID", "Nazwa", "Adres", "Wspolrzedne_X", "Wspolrzedne_Y", "RDLP", "R_PAD", "L_PAD", "Teamviewer", "Nr_kontaktowy"
    FROM "PAD"
    ORDER BY "Nazwa"
"""

INSERT_INSTITUTION = """
INSERT INTO "PAD" ("ID", "Nazwa", "Adres", "Wspolrzedne_X", "Wspolrzedne_Y", "RDLP", "R_PAD", "L_PAD", "Teamviewer", "Nr_kontaktowy")
VALUES (nextval('"PAD_ID_seq"'), %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING "ID", "Nazwa"
"""

UPDATE_INSTITUTION = """
    UPDATE "PAD" 
    SET "Nazwa" = %s 
    WHERE "ID" = %s
    RETURNING "ID", "Nazwa"
"""

DELETE_INSTITUTION = """
    DELETE FROM "PAD" WHERE "ID" = %s
"""

# Cascade delete queries for institution deletion
DELETE_TOWERS_BY_INSTITUTION = """
    DELETE FROM "Wieze" WHERE "Instytucja_ID" = %s
"""

DELETE_DETECTORS_BY_INSTITUTION = """
    DELETE FROM "Detektory" WHERE "Wieza_ID" IN (
        SELECT "ID" FROM "Wieze" WHERE "Instytucja_ID" = %s
    )
"""

# Queries for towers (Wieze)
GET_ALL_TOWERS = """
SELECT 
    w."ID",
    w."Nazwa",
    w."Instytucja_ID",
    w."Wspolrzedne_X",
    w."Wspolrzedne_Y",
    w."Skrypt_od",
    w."Skrypt_do",
    w."Usluga",
    w."Gwarancja",
    w."Serwis",
    w."Wersja_aplikacji",
    w."Instalator",
    w."Instrukcja",
    w."Azymut",
    w."Trasa",
    w."Poziom",
    w."Uwagi",
    p."Nazwa" AS "Nazwa_Instytucji",
    b."serial" AS "Box_serial",
    b."openvpn_ip",
    b."local_ip",
    b."mac_address"
FROM "Wieze" w
LEFT JOIN "PAD" p ON w."Instytucja_ID" = p."ID"
LEFT JOIN "Boxes" b ON w."box" = b."serial"
ORDER BY p."Nazwa", w."Nazwa";
"""
INSERT_TOWER = """
INSERT INTO "Wieze" (
    "Nazwa", "Instytucja_ID", "Wspolrzedne_X", "Wspolrzedne_Y",
    "Skrypt_od", "Skrypt_do", "Usluga",
    "Gwarancja", "Serwis", "Wersja_aplikacji", "Instalator", "Instrukcja",
    "Azymut", "Trasa", "Poziom", "Uwagi", "box"
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING "ID", "Nazwa";
"""

UPDATE_TOWER = """
UPDATE "Wieze"
SET 
    "Nazwa" = %s,
    "Instytucja_ID" = %s,
    "Wspolrzedne_X" = %s,
    "Wspolrzedne_Y" = %s,
    "Skrypt_od" = %s,
    "Skrypt_do" = %s,
    "Usluga" = %s,
    "Gwarancja" = %s,
    "Serwis" = %s,
    "Wersja_aplikacji" = %s,
    "Instalator" = %s,
    "Instrukcja" = %s,
    "Azymut" = %s,
    "Trasa" = %s,
    "Poziom" = %s,
    "Uwagi" = %s,
    "box" = %s
WHERE "ID" = %s
RETURNING "ID", "Nazwa";
"""

DELETE_TOWER = """
    DELETE FROM "Wieze" WHERE "ID" = %s
"""

# Cascade delete for tower deletion
DELETE_DETECTORS_BY_TOWER = """
    DELETE FROM "Detektory" WHERE "Wieza_ID" = %s
"""

# Queries for detectors (Detektory)
GET_ALL_DETECTORS = """
    SELECT
        d."serial",
        d."Wieza_ID",
        COALESCE(d."name", CONCAT(w."Nazwa", '_', d."serial"), d."serial"::text) AS "Nazwa",
        w."Nazwa" AS "Wieza_Nazwa",
        i."Nazwa" AS "Instytucja_Nazwa",
        d."live_view_updated_at"
    FROM "Detektory" d
    INNER JOIN "Wieze" w ON d."Wieza_ID" = w."ID"  -- Zmieniono z LEFT na INNER
    INNER JOIN "PAD" i ON w."Instytucja_ID" = i."ID"  -- Zmieniono z LEFT na INNER
    WHERE d."Wieza_ID" IS NOT NULL  -- Dodano filtr
    ORDER BY i."Nazwa", w."Nazwa", d."serial"
"""

INSERT_DETECTOR = """
INSERT INTO "Detektory" ("serial", "Wieza_ID", "name")
SELECT %s, %s, CONCAT(w."Nazwa", '_', %s)
FROM "Wieze" w
WHERE w."ID" = %s
RETURNING "serial", "Wieza_ID", "name" AS "Nazwa"
"""

UPDATE_DETECTOR_NAME = """
    UPDATE "Detektory" 
    SET "Nazwa" = %s 
    WHERE "serial" = %s
    RETURNING "serial", "Nazwa"
"""

DELETE_DETECTOR = """
    DELETE FROM "Detektory" WHERE "serial" = %s
"""

DELETE_DETECTOR_BY_SERIAL = """
    DELETE FROM "Detektory" WHERE "serial" = %s
"""

GET_DETECTOR_TOWER_ID = """
    SELECT "Wieza_ID" FROM "Detektory" WHERE "serial" = %s
"""

# Query for map data
GET_TOWERS_WITH_INSTITUTIONS = """
SELECT 
    w."ID", 
    w."Nazwa" AS "Wieza", 
    w."Wspolrzedne_X", 
    w."Wspolrzedne_Y",
    w."Skrypt_od",
    w."Skrypt_do",
    w."Usluga",
    w."Gwarancja",
    w."Serwis",
    w."Wersja_aplikacji",
    w."Instalator",
    w."Instrukcja",
    w."Azymut",
    w."Trasa",
    w."Poziom",
    w."Uwagi",
    p."Nazwa" AS "Nadlesnictwo",
    CASE 
        WHEN COUNT(b."serial") > 0 THEN 'TAK'
        ELSE 'NIE'
    END AS "Detektory",
    ARRAY_AGG(
        JSON_BUILD_OBJECT(
            'serial', b."serial",
            'openvpn_ip', b."openvpn_ip",
            'local_ip', b."local_ip",
            'mac_address', b."mac_address"
        )
    ) FILTER (WHERE b."serial" IS NOT NULL) AS "Boxes"
FROM "Wieze" w
LEFT JOIN "PAD" p ON w."Instytucja_ID" = p."ID"
LEFT JOIN "Boxes" b ON b."serial" = w."ID"
WHERE w."Wspolrzedne_X" IS NOT NULL AND w."Wspolrzedne_Y" IS NOT NULL
GROUP BY 
    w."ID", w."Nazwa", w."Wspolrzedne_X", w."Wspolrzedne_Y",
    w."Skrypt_od", w."Skrypt_do",
    w."Usluga", w."Gwarancja", w."Serwis", w."Wersja_aplikacji",
    w."Instalator", w."Instrukcja", w."Azymut", w."Trasa", w."Poziom",
    w."Uwagi",
    p."Nazwa"
ORDER BY p."Nazwa", w."Nazwa";
"""


UPDATE_ALL_DETECTOR_NAMES = '''
UPDATE "Detektory"
SET "name" = CONCAT(w."Nazwa", '_', "Detektory"."serial")
FROM "Wieze" w
WHERE "Detektory"."Wieza_ID" = w."ID"
AND ("Detektory"."name" IS NULL OR "Detektory"."name" = '');
'''

INSERT_DETECTOR_HISTORY = """
INSERT INTO hist_det (id, serial, typ, id_wiezy, data, godzina)
VALUES (nextval('hist_det_id_seq'), %s, %s, %s, CURRENT_DATE, CURRENT_TIME)
"""

GET_DETECTOR_HISTORY = """
SELECT 
    h.id,
    h.serial,
    h.typ,
    h.data,
    h.godzina,
    h.id_wiezy,
    w."Nazwa" AS tower_name,
    h.slack,
    h.nazwa,
    h.nazwastara,
    h.pokrycie,
    h.parametry,
    h.azymut,
    h.horyzont,
    h.dziennik,
    h.boxy,
    h.boxystare,
    h.desktop,
    h.winbox,
    h.monday,
    h.usluga,
    h.upublicznienie,
    h.sponsor,
    h.priv,
    h.skrypt
FROM hist_det h
LEFT JOIN "Wieze" w ON h.id_wiezy = w."ID"
WHERE h.serial = %s
ORDER BY h.data DESC, h.godzina DESC
"""

GET_NEW_DETECTORS = """
SELECT latest.*, w."Nazwa" as name
FROM (
    SELECT DISTINCT ON (serial) *
    FROM hist_det
    ORDER BY serial, data DESC, godzina DESC
) AS latest
JOIN "Detektory" d ON latest.serial = d.serial
JOIN "Wieze" w ON d."Wieza_ID" = w."ID"
WHERE latest.typ = 'dodanie';
"""

# Safe queries for updating detector flags
UPDATE_DETECTOR_FLAG_QUERIES = {
    'slack': "UPDATE hist_det SET slack = %s WHERE id = %s;",
    'pokrycie': "UPDATE hist_det SET pokrycie = %s WHERE id = %s;",
    'parametry': "UPDATE hist_det SET parametry = %s WHERE id = %s;",
    'azymut': "UPDATE hist_det SET azymut = %s WHERE id = %s;",
    'horyzont': "UPDATE hist_det SET horyzont = %s WHERE id = %s;",
    'boxy': "UPDATE hist_det SET boxy = %s WHERE id = %s;",
    'boxystare': "UPDATE hist_det SET boxystare = %s WHERE id = %s;",
    'desktop': "UPDATE hist_det SET desktop = %s WHERE id = %s;",
    'winbox': "UPDATE hist_det SET winbox = %s WHERE id = %s;",
    'monday': "UPDATE hist_det SET monday = %s WHERE id = %s;",
    'usluga': "UPDATE hist_det SET usluga = %s WHERE id = %s;",
    'upublicznienie': "UPDATE hist_det SET upublicznienie = %s WHERE id = %s;",
    'sponsor': "UPDATE hist_det SET sponsor = %s WHERE id = %s;",
    'priv': "UPDATE hist_det SET priv = %s WHERE id = %s;",
    'skrypt': "UPDATE hist_det SET skrypt = %s WHERE id = %s;",
    'nazwa': "UPDATE hist_det SET nazwa = %s WHERE id = %s;"
}

# Additional queries for detectors operations
GET_DETECTOR_BY_SERIAL = """
    SELECT "Wieza_ID", "name" FROM "Detektory" WHERE "serial" = %s
"""

GET_TOWER_NAME_BY_ID = """
    SELECT "Nazwa" FROM "Wieze" WHERE "ID" = %s
"""

UPDATE_DETECTOR_ASSIGNMENT = """
    UPDATE "Detektory" SET "Wieza_ID" = %s, "name" = %s WHERE "serial" = %s RETURNING "serial", "Wieza_ID", "name"
"""

UPDATE_DETECTOR_UNASSIGN = """
    UPDATE "Detektory" SET "Wieza_ID" = NULL, "name" = NULL WHERE "serial" = %s
"""

GET_DETECTOR_WIEZA_ID = """
    SELECT "Wieza_ID" FROM "Detektory" WHERE "serial" = %s
"""

UPDATE_DETECTOR_WIEZA_ID_NULL = """
    UPDATE "Detektory" SET "Wieza_ID" = NULL, "name" = NULL WHERE "serial" = %s
"""

GET_TOWER_INSTITUTION_ID = """
    SELECT "Instytucja_ID" FROM "Wieze" WHERE "ID" = %s
"""

GET_INSTITUTION_BY_ID = """
    SELECT "ID" FROM "PAD" WHERE "ID" = %s
"""

GET_ALL_TICKETS = """
SELECT 
    z.id,
    z.tytul,
    z.data_godzina,
    w."Nazwa" AS nazwa_wiezy, 
    p1.nazwa AS autor,
    p2.nazwa AS oznaczeni,
    z.status,
    z.priorytet,
    z.kategoria,
    z.komentarze
FROM "Zgloszenia" z
LEFT JOIN "Wieze" w ON z.id_wiezy = w."ID"
LEFT JOIN "Pracownicy" p1 ON z.autor = p1.id
LEFT JOIN "Pracownicy" p2 ON z.oznaczeni = p2.id
ORDER BY z.data_godzina DESC;
"""
GET_ALL_CONTRACTS = """
SELECT
    u.id,
    u.instytucja,
    u.typ,
    u.skad_sprzedane,
    u.data_rozpoczecia,
    u.data_zakonczenia,
    u.zalacznik_umowy,
    u.uwagi
FROM "Umowy" u
ORDER BY u.data_rozpoczecia DESC;
"""
GET_ALL_HARDWARE = """
SELECT
    r.id,
    r.name,
    r.elementy_podrzedne,
    r.nadlesnictwo,
    r.wieza,
    r.status,
    r.instalator,
    r.rodzaj,
    r.czas_start,
    r.czas_end,
    r.data_produkcji,
    r.obudowa,
    r.enkoder_katow,
    r.enkoder_obrazu,
    r.driver_silnika,
    r.procesor,
    r.modul,
    r.gniazdo_glowicy,
    r.data_firmware,
    r.wylacznik_glowicy,
    r.adres,
    r.ip_enkodera,
    r.kanal_ch,
    r.ip_moxy
FROM "Rejestr_Kamer" r
ORDER BY r.serial ASC;
"""


INSERT_HARDWARE = """
INSERT INTO public.Rejestr_Kamer
(serial, nadlesnictwo, wieza, status, instalator, czas_start, czas_end, data_produkcji,
 obudowa, enkoder_katow, enkoder_obrazu, driver_silnika, procesor, modul, gniazdo_glowicy,
 data_firmware, wylacznik_glowicy, adres, ip_enkodera, kanal_ch, ip_moxy, uwagi)
VALUES (%(serial)s, %(nadlesnictwo)s, %(wieza)s, %(status)s, %(instalator)s, %(czas_start)s, %(czas_end)s, %(data_produkcji)s,
        %(obudowa)s, %(enkoder_katow)s, %(enkoder_obrazu)s, %(driver_silnika)s, %(procesor)s, %(modul)s, %(gniazdo_glowicy)s,
        %(data_firmware)s, %(wylacznik_glowicy)s, %(adres)s, %(ip_enkodera)s, %(kanal_ch)s, %(ip_moxy)s, %(uwagi)s)
ON CONFLICT (serial) DO UPDATE SET
    nadlesnictwo = EXCLUDED.nadlesnictwo,
    wieza = EXCLUDED.wieza,
    status = EXCLUDED.status,
    instalator = EXCLUDED.instalator,
    czas_start = EXCLUDED.czas_start,
    czas_end = EXCLUDED.czas_end,
    data_produkcji = EXCLUDED.data_produkcji,
    obudowa = EXCLUDED.obudowa,
    enkoder_katow = EXCLUDED.enkoder_katow,
    enkoder_obrazu = EXCLUDED.enkoder_obrazu,
    driver_silnika = EXCLUDED.driver_silnika,
    procesor = EXCLUDED.procesor,
    modul = EXCLUDED.modul,
    gniazdo_glowicy = EXCLUDED.gniazdo_glowicy,
    data_firmware = EXCLUDED.data_firmware,
    wylacznik_glowicy = EXCLUDED.wylacznik_glowicy,
    adres = EXCLUDED.adres,
    ip_enkodera = EXCLUDED.ip_enkodera,
    kanal_ch = EXCLUDED.kanal_ch,
    ip_moxy = EXCLUDED.ip_moxy,
    uwagi = EXCLUDED.uwagi;
"""
UPDATE_DETECTOR_UNASSIGN = """
    UPDATE "Detektory"
    SET "Wieza_ID" = NULL, "name" = NULL
    WHERE "serial" = %s
"""

GET_DETECTOR_DETAILS_BY_SERIAL = """
    SELECT
        d."serial",
        d."Wieza_ID",
        d."name" AS "Nazwa",
        w."Nazwa" AS "Wieza_Nazwa",
        i."Nazwa" AS "Instytucja_Nazwa",
        w."ID" AS "Wieza_ID",
        i."ID" AS "Instytucja_ID"
    FROM "Detektory" d
    LEFT JOIN "Wieze" w ON d."Wieza_ID" = w."ID"
    LEFT JOIN "PAD" i ON w."Instytucja_ID" = i."ID"
    WHERE d."serial" = %s
"""

UPDATE_INSTITUTION_BASE = """
    UPDATE "PAD"
    SET {fields}
    WHERE "ID" = %s
    RETURNING "ID", "Nazwa", "Adres", "Wspolrzedne_X", "Wspolrzedne_Y", "RDLP", "R_PAD", "L_PAD", "Teamviewer", "Nr_kontaktowy"
"""
LOAD_MAP="""
    SELECT
        "ID",
        "Nazwa" AS "Nadlesnictwo",
        "Adres",
        "Wspolrzedne_X",
        "Wspolrzedne_Y"
    FROM "PAD"
"""
GET_TOWER_DETAILS_BY_ID = """
SELECT 
    w."ID",
    w."Nazwa",
    w."Instytucja_ID",
    w."Wspolrzedne_X",
    w."Wspolrzedne_Y",
    w."Skrypt_od",
    w."Skrypt_do",
    w."Usluga",
    w."Gwarancja",
    w."Serwis",
    w."Wersja_aplikacji",
    w."Instalator",
    w."Instrukcja",
    w."Azymut",
    w."Trasa",
    w."Poziom",
    w."Uwagi",
    p."Nazwa" AS "Nazwa_Instytucji",
    b."serial" AS "Box_serial",
    b."openvpn_ip",
    b."local_ip",
    b."mac_address"
FROM "Wieze" w
LEFT JOIN "PAD" p ON w."Instytucja_ID" = p."ID"
LEFT JOIN "Boxes" b ON w."box" = b."serial"
WHERE w."ID" = %s;
"""