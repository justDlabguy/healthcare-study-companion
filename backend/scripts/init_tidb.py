import os
import pymysql
from pymysql.constants import CLIENT
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('local.env')

def create_database_if_not_exists():
    """Create the database if it doesn't exist."""
    try:
        # Connect to MySQL without specifying a database
        connection = pymysql.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', '4000')),
            user=os.getenv('DATABASE_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        
        db_name = os.getenv('DATABASE_NAME', 'healthcare_study')
        
        with connection.cursor() as cursor:
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"Database '{db_name}' created or already exists.")
            
        connection.commit()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def test_connection():
    """Test the database connection."""
    try:
        # Get database URL from environment
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = f"mysql+pymysql://{os.getenv('DATABASE_USER', 'root')}:{os.getenv('DATABASE_PASSWORD', '')}@{os.getenv('DATABASE_HOST', 'localhost')}:{os.getenv('DATABASE_PORT', '4000')}/{os.getenv('DATABASE_NAME', 'healthcare_study')}"
        
        # Test connection
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result = connection.execute("SELECT VERSION()")
            version = result.scalar()
            print(f"Successfully connected to TiDB version: {version}")
            return True
            
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("Initializing TiDB Database...")
    
    # Create database if it doesn't exist
    if create_database_if_not_exists():
        print("Testing database connection...")
        test_connection()
    else:
        print("Failed to initialize database.")
