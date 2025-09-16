from eth_typing import ChecksumAddress, HexStr
from web3 import Web3
from web3.types import Gwei

from src.validators.keystore import LocalKeystore
from src.validators.typings import Validator, ValidatorType


def generate_validators(
    keystore: LocalKeystore,
    vault_address: ChecksumAddress,
    start_index: int,
    amounts: list[Gwei],
    validator_type: ValidatorType,
) -> list[Validator]:
    validators = []
    count = len(amounts)
    validator_indexes = range(start_index, start_index + count)
    available_public_keys = keystore.public_keys[:count]  # todo: filter non-registered
    for validator_index, amount, public_key in zip(
        validator_indexes, amounts, available_public_keys
    ):
        deposit_data = keystore.get_deposit_data(
            public_key=public_key,
            amount=amount,
            vault_address=vault_address,
            validator_type=validator_type,
        )
        exit_signature = keystore.get_exit_signature(
            validator_index=validator_index, public_key=Web3.to_hex(deposit_data['pubkey'])
        )
        validators.append(
            Validator(
                public_key=Web3.to_hex(deposit_data['pubkey']),
                deposit_signature=Web3.to_hex(deposit_data['signature']),
                deposit_data_root=Web3.to_hex(deposit_data['deposit_data_root']),
                amount=Gwei(int(deposit_data['amount'])),
                exit_signature=exit_signature,
                validator_type=validator_type,
            )
        )

    return validators


def get_validators_for_funding(
    keystore: LocalKeystore,
    vault_address: ChecksumAddress,
    public_keys: list[HexStr],
    amounts: list[Gwei],
) -> list[Validator]:
    validators = []
    for public_key, amount in zip(public_keys, amounts):
        if public_key not in keystore:
            raise RuntimeError(f'Public key {public_key} not found in keystores')
        deposit_data = keystore.get_deposit_data(
            public_key=public_key,
            amount=amount,
            vault_address=vault_address,
            validator_type=ValidatorType.V2,
        )
        validators.append(
            Validator(
                public_key=Web3.to_hex(deposit_data['pubkey']),
                deposit_signature=Web3.to_hex(deposit_data['signature']),
                amount=amount,
                deposit_data_root=Web3.to_hex(deposit_data['deposit_data_root']),
            )
        )
    return validators
