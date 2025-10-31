"""
Database connection management with context managers.
Provides secure and automated database connection handling.
"""
import psycopg2
import logging
from contextlib import contextmanager
from config import DB_CONFIG

logger = logging.getLogger(__name__)

def get_connection():
    """
    Get database connection using psycopg2
    Returns connection object with proper error handling
    """
    try:
        # Validate config before connecting
        required_keys = ['host', 'database', 'port', 'user', 'password']
        for key in required_keys:
            if not DB_CONFIG.get(key):
                raise ValueError(f"Missing database configuration: {key}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        logger.debug("Successfully connected to database")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to database: {e}")
        raise

@contextmanager
def db_connection():
    """Context manager for database connections with automatic cleanup"""
    conn = None
    try:
        conn = get_connection()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
            logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

@contextmanager 
def db_cursor():
    """Context manager for database operations with automatic commit/rollback"""
    with db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor, conn
            conn.commit()
            logger.debug("Database transaction committed successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Database transaction rolled back: {e}")
            raise
        finally:
            cursor.close()
            logger.debug("Database cursor closed")

@contextmanager
def db_cursor_readonly():
    """Context manager for read-only database operations"""
    with db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()
            logger.debug("Read-only database cursor closed")


