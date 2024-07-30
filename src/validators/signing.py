from typing import Sequence

from eth_account.messages import encode_typed_data
from eth_typing import ChecksumAddress, HexStr
from web3 import Web3

from src.config import settings
from src.validators.typings import AppState, Validator


def get_validators_manager_signature(
    vault: ChecksumAddress, validators_registry_root: HexStr, validators: Sequence[Validator]
) -> HexStr:
    encoded_validators = [_encode_validator(v) for v in validators]

    full_message = {
        'primaryType': 'VaultValidators',
        'types': {
            'VaultValidators': [
                {'name': 'validatorsRegistryRoot', 'type': 'bytes32'},
                {'name': 'validators', 'type': 'bytes'},
            ],
        },
        'domain': {
            'name': 'VaultValidators',
            'version': '1',
            'chainId': settings.network_config.CHAIN_ID,
            'verifyingContract': vault,
        },
        'message': {
            'validatorsRegistryRoot': Web3.to_bytes(hexstr=validators_registry_root),
            'validators': b''.join(encoded_validators),
        },
    }

    app_state = AppState()
    encoded_message = encode_typed_data(full_message=full_message)
    signed_msg = app_state.validators_manager_account.sign_message(encoded_message)

    return HexStr(signed_msg.signature.hex())


def _encode_validator(v: Validator) -> bytes:
    return b''.join(
        [
            Web3.to_bytes(hexstr=v.public_key),
            Web3.to_bytes(hexstr=v.deposit_signature),
            Web3.to_bytes(hexstr=v.deposit_data_root),
        ]
    )