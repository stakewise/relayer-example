from dataclasses import dataclass

from eth_account.signers.local import LocalAccount
from eth_typing import BLSSignature, HexStr

from src.common.typings import Singleton


@dataclass
class Validator:
    public_key: HexStr
    deposit_data_root: HexStr
    deposit_signature: HexStr
    amount_gwei: int
    exit_signature: BLSSignature


class AppState(metaclass=Singleton):
    validators_manager_account: LocalAccount
