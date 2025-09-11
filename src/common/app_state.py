from eth_account.signers.local import LocalAccount

from src.common.typings import Singleton
from src.validators.keystore import LocalKeystore


class AppState(metaclass=Singleton):
    validators_manager_account: LocalAccount
    keystore: LocalKeystore | None = None
