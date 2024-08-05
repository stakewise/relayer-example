import milagro_bls_binding as bls
from eth_typing import BLSSignature, HexAddress
from sw_utils import ConsensusFork, get_exit_message_signing_root
from web3 import Web3

from src.config import settings
from src.validators.credentials import (
    DEPOSIT_AMOUNT_GWEI,
    Credential,
    CredentialManager,
)
from src.validators.typings import Validator


def generate_validators(
    withdrawal_address: HexAddress, start_index: int, count: int
) -> list[Validator]:
    """
    `_generate_validators` generates validator keystores, but does not save keystores on disk.
    todo: You should save keystores on disk to be able to exit validator manually.
    """
    res = []
    credentials = CredentialManager.generate_credentials(
        count=count,
        start_index=0,
        network=settings.network,
        withdrawal_address=withdrawal_address,
    )
    validator_indexes = range(start_index, start_index + count)

    for validator_index, credential in zip(validator_indexes, credentials):
        deposit_datum_dict = credential.deposit_datum_dict()
        exit_signature = _get_exit_signature(validator_index=validator_index, credential=credential)
        res.append(
            Validator(
                public_key=credential.public_key,
                deposit_data_root=Web3.to_hex(deposit_datum_dict['deposit_data_root']),
                deposit_signature=Web3.to_hex(deposit_datum_dict['signature']),
                amount_gwei=DEPOSIT_AMOUNT_GWEI,
                exit_signature=exit_signature,
            )
        )
    return res


def _get_exit_signature(
    validator_index: int, credential: Credential, fork: ConsensusFork | None = None
) -> BLSSignature:
    fork = fork or settings.network_config.SHAPELLA_FORK

    message = get_exit_message_signing_root(
        validator_index=validator_index,
        genesis_validators_root=settings.network_config.GENESIS_VALIDATORS_ROOT,
        fork=fork,
    )

    return bls.Sign(Web3.to_bytes(credential.private_key), message)
