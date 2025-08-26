from logging.config import fileConfig
import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import application metadata and settings
from app.models import Base
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url() -> str:
    # Load environment variables from local.env
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / 'local.env')
    
    # First try to get from environment variables
    db_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL")
    
    # If not in environment, try to construct from individual settings
    if not db_url:
        db_host = os.getenv("DATABASE_HOST", "localhost")
        db_port = os.getenv("DATABASE_PORT", "4000")
        db_user = os.getenv("DATABASE_USER", "root")
        db_password = os.getenv("DATABASE_PASSWORD", "")
        db_name = os.getenv("DATABASE_NAME", "healthcare_study")
        
            # Construct the URL
        db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
        
        # Add SSL parameters if not in development
        if os.getenv("ENVIRONMENT") != "development":
            db_url += "&ssl_verify_cert=true&ssl_verify_identity=true"
    
    # Ensure the URL is in the correct format for SQLAlchemy
    if db_url and db_url.startswith("mysql:"):
        db_url = db_url.replace("mysql:", "mysql+pymysql:", 1)
    
    print(f"Using database URL: {db_url}")
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine.
    By skipping the Engine creation, we don't even need a DBAPI to be available.
    """
    def include_object(object, name, type_, reflected, compare_to):
        """
        Filter out system tables and schemas that we don't want to track.
        """
        # Skip all mysql schema tables (system tables)
        if hasattr(object, 'schema') and object.schema == 'mysql':
            return False
        
        # Skip system tables in the main schema
        if type_ == "table" and name in [
            'mysql', 'information_schema', 'performance_schema', 'sys'
        ]:
            return False
            
        return True

    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_object=include_object,  # Filter out system objects
        # Skip foreign key comparisons to avoid TiDB naming issues
        compare_foreign_keys=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        {"sqlalchemy.url": get_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    def include_object(object, name, type_, reflected, compare_to):
        """
        Filter out system tables and schemas that we don't want to track.
        """
        # Skip all mysql schema tables (system tables)
        if hasattr(object, 'schema') and object.schema == 'mysql':
            return False
        
        # Skip system tables in the main schema
        if type_ == "table" and name in [
            'mysql', 'information_schema', 'performance_schema', 'sys'
        ]:
            return False
            
        return True

    def compare_foreign_keys(autogen_context, upgrade_ops, schemas):
        """
        Custom comparison for foreign keys to handle TiDB naming issues.
        TiDB creates foreign keys with auto-generated names that change,
        so we need to compare by structure rather than name.
        """
        return []  # Skip foreign key comparisons for now

    def process_revision_directives(context, revision, directives):
        """
        Process revision directives to filter out foreign key changes.
        This is a more comprehensive way to handle TiDB foreign key naming issues.
        """
        if directives[0].upgrade_ops:
            # Filter out foreign key operations
            filtered_ops = []
            for op in directives[0].upgrade_ops.ops:
                if hasattr(op, 'ops'):  # BatchAlterTableOp
                    filtered_batch_ops = []
                    for batch_op in op.ops:
                        if not (hasattr(batch_op, 'constraint_name') and 
                               (batch_op.__class__.__name__ in ['DropConstraintOp', 'CreateForeignKeyOp'])):
                            filtered_batch_ops.append(batch_op)
                    if filtered_batch_ops:
                        op.ops = filtered_batch_ops
                        filtered_ops.append(op)
                elif not (batch_op.__class__.__name__ in ['DropConstraintOp', 'CreateForeignKeyOp']):
                    filtered_ops.append(op)
            
            directives[0].upgrade_ops.ops = filtered_ops
            
            # If no operations remain, mark as no changes
            if not directives[0].upgrade_ops.ops:
                directives[:] = []

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            include_schemas=False,  # Don't include other schemas
            render_as_batch=True,  # Enable batch mode for SQLite
            include_object=include_object,  # Filter out system objects
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

