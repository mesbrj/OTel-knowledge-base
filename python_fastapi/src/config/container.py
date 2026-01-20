
from ports.inbound.data_manager import DataManager
from ports.repository.data_base import DbAccess
from adapter.sql.data_access import DbAccessImpl
from adapter.sql.data_base import DatabaseManager
from core.data_manager.use_cases import DataManagerImpl, PublicCrud


class DependencyContainer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DependencyContainer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._db_manager: DatabaseManager | None = None
        self._db_access: DbAccess | None = None
        self._data_manager: DataManager | None = None
        self._public_crud: DataManager | None = None
        self._initialized = False

    def initialize(self) -> None:
        if self._initialized:
            return
        # Data layer
        self._db_manager = DatabaseManager
        self._db_access = DbAccessImpl(db_manager=self._db_manager)
        self._data_manager = DataManagerImpl(repository=self._db_access)
        self._public_crud = PublicCrud(data_manager=self._data_manager)

        self._initialized = True

    def reset(self) -> None:
        self._db_access = None
        self._data_manager = None
        self._public_crud = None
        self._permission_checker = None
        self._authorization_use_case = None
        self._initialized = False

    def db_manager(self) -> DatabaseManager:
        if self._db_manager is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._db_manager

    def db_access(self) -> DbAccess:
        if self._db_access is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._db_access

    def data_manager(self) -> DataManager:
        if self._data_manager is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._data_manager

    def public_crud(self) -> DataManager:
        if self._public_crud is None:
            raise RuntimeError("Dependencies not initialized. Call container.initialize() first.")
        return self._public_crud

container = DependencyContainer()
