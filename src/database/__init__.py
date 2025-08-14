from .sqlite_manager import SQLiteManager

# For now, DatabaseManager is a direct alias for SQLiteManager.
# This can be expanded later to support other database backends.
class DatabaseManager(SQLiteManager):
    pass

__all__ = ["DatabaseManager"]
