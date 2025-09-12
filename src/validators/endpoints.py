from fastapi import APIRouter
from web3 import Web3

from src.common.app_state import AppState
from src.common.contracts import validators_registry_contract
from src.validators import schema
from src.validators.validators import generate_validators
from src.validators.validators_manager import get_validators_manager_signature

router = APIRouter()


@router.post('/validators')
async def register_validators(
    request: schema.ValidatorsRegisterRequest,
) -> schema.ValidatorsRegisterResponse:
    validator_items = []
    app_state = AppState()
    validators = generate_validators(
        keystore=app_state.keystore,
        vault_address=request.vault,
        start_index=request.validators_start_index,
        amounts=request.amounts,
        validator_type=request.validator_type,
    )

    for validator in validators:
        validator_items.append(
            schema.ValidatorsRegisterResponseItem(
                public_key=validator.public_key,
                deposit_signature=validator.deposit_signature,
                amount=validator.amount,
                exit_signature=Web3.to_hex(validator.exit_signature),
            )
        )

    validators_registry_root = await validators_registry_contract.get_registry_root()

    validators_manager_signature = get_validators_manager_signature(
        Web3.to_checksum_address(request.vault),
        Web3.to_hex(validators_registry_root),
        validators,
    )

    return schema.ValidatorsRegisterResponse(
        validators=validator_items,
        validators_manager_signature=validators_manager_signature,
    )
