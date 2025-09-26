import milagro_bls_binding as bls
from eth_typing import BLSSignature, ChecksumAddress
from sw_utils import ConsensusFork, get_exit_message_signing_root
from web3 import Web3
from web3.types import Gwei

from src.config import settings
from src.validators.credentials import Credential, CredentialManager
from src.validators.typings import Validator, ValidatorType


def generate_validators(
    vault_address: ChecksumAddress,
    start_index: int,
    amounts: list[Gwei],
    validator_type: ValidatorType,
) -> list[Validator]:
    """
    `_generate_validators` generates validator keystores, but does not save keystores on disk.
    todo: You should save keystores on disk to be able to exit validator manually.
    """
    res = []
    count = len(amounts)
    credentials = CredentialManager.generate_credentials(
        count=count,
        start_index=0,
        network=settings.network,
        vault_address=vault_address,
        validator_type=validator_type,
    )
    validator_indexes = range(start_index, start_index + count)

    for validator_index, amount, credential in zip(validator_indexes, amounts, credentials):
        deposit_datum_dict = credential.get_deposit_datum_dict(amount)
        exit_signature = _get_exit_signature(validator_index=validator_index, credential=credential)
        res.append(
            Validator(
                public_key=credential.public_key,
                deposit_data_root=Web3.to_hex(deposit_datum_dict['deposit_data_root']),
                deposit_signature=Web3.to_hex(deposit_datum_dict['signature']),
                amount=amount,
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
