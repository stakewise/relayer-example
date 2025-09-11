from dataclasses import dataclass
from enum import Enum
from typing import NewType

from eth_typing import BLSSignature, HexStr
from web3.types import Gwei

BLSPrivkey = NewType('BLSPrivkey', bytes)


class ValidatorType(Enum):
    V1 = 'V1'
    V2 = 'V2'


@dataclass
class Validator:
    public_key: HexStr
    deposit_data_root: HexStr
    deposit_signature: HexStr
    amount: Gwei
    exit_signature: BLSSignature
    validator_type: ValidatorType
