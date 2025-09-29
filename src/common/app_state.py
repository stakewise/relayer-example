from eth_account.signers.local import LocalAccount

from src.common.typings import Singleton


class AppState(metaclass=Singleton):
    validators_manager_account: LocalAccount
