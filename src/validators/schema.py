from eth_typing import ChecksumAddress, HexStr
from pydantic import BaseModel
from web3.types import Gwei

from src.validators.typings import ValidatorType


class ValidatorsRegisterRequest(BaseModel):
    vault: ChecksumAddress
    validators_start_index: int
    amounts: list[Gwei]
    validator_type: ValidatorType


class ValidatorsRegisterResponseItem(BaseModel):
    public_key: HexStr
    deposit_signature: HexStr
    amount: Gwei
    exit_signature: HexStr


class ValidatorsRegisterResponse(BaseModel):
    validators: list[ValidatorsRegisterResponseItem]
    validators_manager_signature: HexStr
