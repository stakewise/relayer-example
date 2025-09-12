import secrets

import milagro_bls_binding as bls
from eth_typing import BLSPrivateKey, BLSSignature, ChecksumAddress, HexStr
from py_ecc.optimized_bls12_381.optimized_curve import curve_order
from sw_utils import ConsensusFork, get_exit_message_signing_root
from web3 import Web3
from web3.types import Gwei

from src.config import settings
from src.validators.credentials import CredentialManager
from src.validators.keystore import LocalKeystore
from src.validators.typings import Validator, ValidatorType


def generate_validators_in_place(
    vault_address: ChecksumAddress,
    start_index: int,
    amounts: list[Gwei],
    validator_type: ValidatorType,
) -> list[Validator]:
    """
    `_generate_validators` generates validator keystores, but does not save keystores on disk.
    todo: You should save keystores on disk to be able to exit validator manually.
    """
    validators = []
    count = len(amounts)

    private_key = BLSPrivateKey(secrets.randbelow(curve_order))

    validator_indexes = range(start_index, start_index + count)

    for validator_index, amount in zip(validator_indexes, amounts):
        credential = CredentialManager.generate_credential(
            private_key=private_key,
            index=validator_index,
            network=settings.network,
            vault=vault_address,
            validator_type=validator_type,
        )

        deposit_datum_dict = credential.get_deposit_datum_dict(amount=amount)
        exit_signature = _get_exit_signature(
            validator_index=validator_index, private_key=credential.private_key
        )
        validators.append(
            Validator(
                public_key=credential.public_key,
                deposit_data_root=Web3.to_hex(deposit_datum_dict['deposit_data_root']),
                deposit_signature=Web3.to_hex(deposit_datum_dict['signature']),
                amount=amount,
                exit_signature=exit_signature,
                validator_type=validator_type,
            )
        )
    return validators


def generate_validators_from_keystore(
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


def _get_exit_signature(
    validator_index: int, private_key: BLSPrivateKey, fork: ConsensusFork | None = None
) -> BLSSignature:
    fork = fork or settings.network_config.SHAPELLA_FORK

    message = get_exit_message_signing_root(
        validator_index=validator_index,
        genesis_validators_root=settings.network_config.GENESIS_VALIDATORS_ROOT,
        fork=fork,
    )

    return bls.Sign(Web3.to_bytes(private_key), message)
