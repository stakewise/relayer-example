from fastapi import APIRouter
from web3 import Web3

from src.common.app_state import AppState
from src.common.contracts import VaultContract, validators_registry_contract
from src.validators import schema
from src.validators.validators import (
    generate_validators_from_keystore,
    generate_validators_in_place,
    get_validators_for_funding,
)
from src.validators.validators_manager import (
    get_validators_manager_signature_with_nonce,
    get_validators_manager_signature_with_registry_root,
)

router = APIRouter()


@router.post('/validators')
async def register_validators(
    request: schema.ValidatorsRegisterRequest,
) -> schema.ValidatorsRegisterResponse:
    validator_items = []
    app_state = AppState()
    if app_state.keystore:
        validators = generate_validators_from_keystore(
            keystore=app_state.keystore,
            vault_address=request.vault,
            start_index=request.validators_start_index,
            amounts=request.amounts,
            validator_type=request.validator_type,
        )
    else:
        validators = generate_validators_in_place(
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

    validators_manager_signature = get_validators_manager_signature_with_registry_root(
        Web3.to_checksum_address(request.vault),
        Web3.to_hex(validators_registry_root),
        validators,
    )

    return schema.ValidatorsRegisterResponse(
        validators=validator_items,
        validators_manager_signature=validators_manager_signature,
    )


@router.post('/fund')
async def fund_validators(
    request: schema.ValidatorsFundRequest,
) -> schema.ValidatorsFundResponse:
    validator_items = []
    app_state = AppState()
    if not app_state.keystore:
        raise ValueError('Keystore is required for funding validators')

    validators = get_validators_for_funding(
        keystore=app_state.keystore,
        vault_address=request.vault,
        public_keys=request.public_keys,
        amounts=request.amounts,
    )

    for validator in validators:
        validator_items.append(
            schema.ValidatorsFundResponseItem(
                public_key=validator.public_key,
                deposit_signature=validator.deposit_signature,
                amount=validator.amount,
            )
        )

    vault_contact = VaultContract(request.vault)
    validators_manager_nonce = await vault_contact.validators_manager_nonce()
    validators_manager_signature = get_validators_manager_signature_with_nonce(
        Web3.to_checksum_address(request.vault),
        validators_manager_nonce,
        validators,
    )

    return schema.ValidatorsFundResponse(
        validators=validator_items,
        validators_manager_signature=validators_manager_signature,
    )
