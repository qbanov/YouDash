"""
SmokeD System API integration.
Handles authentication and data fetching from SmokeD Web.
"""
import requests
import logging
from datetime import datetime, timezone
from django.conf import settings
#from database.connection import db_cursor, db_connection
from psycopg2.extras import execute_values
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def create_session():
    """Create requests session with proper timeout and retry configuration"""
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session

# Global session for connection pooling
api_session = create_session()

def get_jwt_token(login_url, payload):
    """
    Get JWT token from SmokedSystem API for authentication.

    Args:
        login_url: API login endpoint URL
        payload: Login credentials dict

    Returns:
        str: JWT token for authenticated requests
    """
    try:
        response = api_session.post(
            login_url,
            json=payload,
            timeout=30,
            verify=True
        )
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            raise ValueError("No token received from API")
        logger.info("Successfully obtained JWT token")
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get JWT token: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting JWT token: {e}")
        raise

def make_authenticated_request(api_url, token):
    """
    Make authenticated request to SmokedSystem API.

    Args:
        api_url: API endpoint URL
        token: JWT authentication token

    Returns:
        dict: JSON response from API
    """
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "mantaMap/1.0"
        }

        response = api_session.get(
            api_url,
            headers=headers,
            timeout=30,
            verify=True
        )
        response.raise_for_status()
        logger.info(f"Successfully made request to {api_url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to make authenticated request to {api_url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in authenticated request: {e}")
        raise

login_payload = settings.SMOKED_CREDENTIALS

def normalize_serial_to_db_format(s: str | int | None) -> str | None:
    """
    Convert serial number to database format (removes leading zeros).
    Preserves None when no value provided.
    """
    if s is None:
        return None
    return str(int(s))

def sync_detectors_and_live_view():
    """
    Batch synchronization function that processes all detectors at once.
    """
    start_time = datetime.now()
    try:
        token = get_jwt_token(settings.LOGIN_URL, login_payload)
        api_response = make_authenticated_request(settings.DETECTORS_URL, token)
        api_detectors = api_response.get('data', [])

        if not api_detectors:
            logger.warning("No detectors received from API")
            return 0, 0

        # Process all data in memory
        api_data = []
        for api_detector in api_detectors:
            serial = normalize_serial_to_db_format(api_detector.get('serial'))
            if serial:
                live_view_data = api_detector.get('live_view_updated_at')
                api_data.append((serial, live_view_data))

        if not api_data:
            logger.warning("No valid detector data from API")
            return 0, 0

        # Single batch operation for all detectors
        with db_connection() as conn:
            cursor = conn.cursor()

            query = '''
                INSERT INTO public."Detektory" (serial, "live_view_updated_at", name)
                VALUES %s
                ON CONFLICT (serial) 
                DO UPDATE SET 
                    "live_view_updated_at" = EXCLUDED."live_view_updated_at"
                RETURNING 
                    serial,
                    (xmax = 0) AS was_inserted
            '''

            upsert_data = [(serial, live_view, None) for serial, live_view in api_data]

            execute_values(
                cursor,
                query,
                upsert_data,
                template=None,
                page_size=1000
            )

            results = cursor.fetchall()
            added_count = sum(1 for row in results if row[1])
            updated_count = len(results) - added_count

            conn.commit()
            cursor.close()

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Detectors sync completed in {duration:.2f}s: {added_count} new, {updated_count} updated")
        return added_count, updated_count

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Detectors sync failed after {duration:.2f}s: {e}")
        raise

def sync_boxes_to_db():
    """
    Synchronizuje dane boxów z API do tabeli 'Boxes'.
    Upsertuje rekordy: wstawia nowe, aktualizuje tylko zmienione pola.
    """
    start_time = datetime.now()
    try:
        # --- Pobranie danych z API ---
        token = get_jwt_token(settings.LOGIN_URL, login_payload)
        api_response = make_authenticated_request(settings.BOXES_URL, token)
        api_boxes = api_response.get('data', [])

        if not api_boxes:
            logger.warning("Brak danych z API — tabela Boxes nie została zmieniona.")
            return 0, 0

        # --- Normalizacja danych ---
        upsert_data = []
        for box in api_boxes:
            serial = normalize_serial_to_db_format(box.get('serial'))
            if not serial:
                continue
            upsert_data.append((
                serial,
                box.get('openvpn_ip'),
                box.get('local_ip'),
                box.get('mac_address')
            ))

        if not upsert_data:
            logger.warning("Brak prawidłowych rekordów do synchronizacji.")
            return 0, 0

        # --- Batch upsert w bazie ---
        with db_connection() as conn:
            cursor = conn.cursor()

            query = '''
                INSERT INTO "Boxes" ("serial", "openvpn_ip", "local_ip", "mac_address")
                VALUES %s
                ON CONFLICT ("serial") DO UPDATE SET
                    "openvpn_ip" = EXCLUDED."openvpn_ip",
                    "local_ip" = EXCLUDED."local_ip",
                    "mac_address" = EXCLUDED."mac_address"
                RETURNING serial, (xmax = 0) AS was_inserted
            '''

            execute_values(
                cursor,
                query,
                upsert_data,
                template=None,
                page_size=1000
            )

            results = cursor.fetchall()
            added_count = sum(1 for row in results if row[1])
            updated_count = len(results) - added_count

            conn.commit()
            cursor.close()

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Boxes sync completed in {duration:.2f}s: {added_count} new, {updated_count} updated")
        return added_count, updated_count

    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        logger.error(f"Boxes sync failed after {duration:.2f}s: {e}")
        raise

def get_sync_status():
    """
    Get current synchronization status and statistics.
    """
    try:
        with db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM public.\"Detektory\"")
            total_detectors = cursor.fetchone()[0]

            cursor.execute("""
                SELECT MAX(\"live_view_updated_at\") 
                FROM public.\"Detektory\" 
                WHERE \"live_view_updated_at\" IS NOT NULL
            """)
            last_sync = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) 
                FROM public.\"Detektory\" 
                WHERE \"live_view_updated_at\" IS NULL
            """)
            missing_live_view = cursor.fetchone()[0]
            cursor.close()

        return {
            "total_detectors": total_detectors,
            "last_sync": last_sync.isoformat() if last_sync else None,
            "missing_live_view": missing_live_view,
            "sync_status": "up_to_date" if missing_live_view == 0 else "needs_sync"
        }

    except Exception as e:
        logger.error(f"Failed to get sync status: {e}")
        raise
