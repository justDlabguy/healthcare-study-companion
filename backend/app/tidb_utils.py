from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
from sqlalchemy.orm import Session
import pymysql
from pymysql.constants import CLIENT
import logging
from .config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TiDBUtils:
    """Utility class for TiDB-specific operations."""
    
    @staticmethod
    def parse_db_url(db_url: str) -> Dict[str, Any]:
        """Parse database URL into connection parameters."""
        parsed = urlparse(db_url)
        query = parse_qs(parsed.query)
        
        # Extract connection parameters
        connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 4000,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.strip('/'),
            'client_flag': CLIENT.MULTI_STATEMENTS,
            'charset': 'utf8mb4',
            'cursorclass': pymysql.cursors.DictCursor,
        }
        
        # Add SSL parameters if present
        if 'ssl_ca' in query:
            connection_params['ssl_ca'] = query['ssl_ca'][0]
        if 'ssl_verify_cert' in query:
            connection_params['ssl_verify_cert'] = query['ssl_verify_cert'][0].lower() == 'true'
        if 'ssl_verify_identity' in query:
            connection_params['ssl_verify_identity'] = query['ssl_verify_identity'][0].lower() == 'true'
            
        return connection_params
    
    @classmethod
    def get_connection_params(cls) -> Dict[str, Any]:
        """Get connection parameters for TiDB."""
        if not settings.database_url:
            raise ValueError("Database URL is not configured")
        return cls.parse_db_url(settings.database_url)
    
    @classmethod
    def get_connection(cls):
        """Get a raw PyMySQL connection to TiDB."""
        try:
            return pymysql.connect(**cls.get_connection_params())
        except pymysql.Error as e:
            logger.error(f"Failed to connect to TiDB: {e}")
            raise
    
    @staticmethod
    def execute_sql(sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute raw SQL and return results as dictionaries."""
        try:
            with TiDBUtils.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, params or ())
                    if cursor.description:
                        return cursor.fetchall()
                    return []
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            raise
    
    @staticmethod
    def get_table_info(table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a specific table."""
        return TiDBUtils.execute_sql(
            """
            SELECT column_name, data_type, is_nullable, column_key, column_default, extra
            FROM information_schema.columns
            WHERE table_schema = DATABASE() AND table_name = %s
            ORDER BY ordinal_position
            """,
            (table_name,)
        )
    
    @staticmethod
    def get_database_size() -> Dict[str, Any]:
        """Get database size information."""
        result = TiDBUtils.execute_sql(
            """
            SELECT 
                table_schema as db_name,
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb,
                COUNT(*) as table_count
            FROM information_schema.tables
            WHERE table_schema = DATABASE()
            GROUP BY table_schema
            """
        )
        return result[0] if result else {}
    
    @staticmethod
    def get_tidb_version() -> str:
        """Get TiDB version information."""
        result = TiDBUtils.execute_sql("SELECT VERSION() as version")
        return result[0]['version'] if result else "Unknown"
    
    @staticmethod
    def check_connection() -> bool:
        """Check if connection to TiDB is working."""
        try:
            with TiDBUtils.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return True
        except Exception as e:
            logger.error(f"TiDB connection check failed: {e}")
            return False
    
    @staticmethod
    def optimize_tables() -> Dict[str, Any]:
        """Optimize all tables in the database."""
        tables = TiDBUtils.execute_sql(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE'"
        )
        
        results = {}
        for table in tables:
            table_name = table['table_name']
            try:
                TiDBUtils.execute_sql(f"ANALYZE TABLE `{table_name}`")
                results[table_name] = "optimized"
            except Exception as e:
                results[table_name] = f"error: {str(e)}"
        
        return results
