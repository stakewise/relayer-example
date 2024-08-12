from eth_typing import ChecksumAddress, HexStr
from pydantic import BaseModel


class ValidatorsRequest(BaseModel):
    vault: ChecksumAddress
    validators_start_index: int
    validators_batch_size: int
    validators_total: int | None


class ValidatorsResponseItem(BaseModel):
    public_key: HexStr
    deposit_signature: HexStr
    amount_gwei: int
    exit_signature: HexStr


class ValidatorsResponse(BaseModel):
    validators: list[ValidatorsResponseItem]
    validators_manager_signature: HexStr
