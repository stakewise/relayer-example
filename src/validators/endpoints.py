from fastapi import APIRouter
from web3 import Web3

from src.common.contracts import validators_registry_contract
from src.validators.schema import (
    ValidatorsRequest,
    ValidatorsResponse,
    ValidatorsResponseItem,
)
from src.validators.signing import get_validators_manager_signature
from src.validators.typings import Validator

router = APIRouter()


@router.post('/validators')
async def create_validators(
    request: ValidatorsRequest,
) -> ValidatorsResponse:
    validator_items = []

    validators = _generate_validators(request.validators_count)

    for validator in validators:
        validator_items.append(
            ValidatorsResponseItem(
                public_key=validator.public_key,
                deposit_signature=validator.deposit_signature,
                amount_gwei=validator.amount_gwei,
                exit_signature=Web3.to_hex(validator.exit_signature),
            )
        )

    validators_registry_root = await validators_registry_contract.get_registry_root()

    validators_manager_signature = get_validators_manager_signature(
        Web3.to_checksum_address(request.vault),
        Web3.to_hex(validators_registry_root),
        validators,
    )

    return ValidatorsResponse(
        validators=validator_items,
        validators_manager_signature=validators_manager_signature,
    )


def _generate_validators(validators_count: int) -> list[Validator]:
    res = []
    return res
