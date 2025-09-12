from dataclasses import dataclass
from functools import cached_property

import milagro_bls_binding as bls
from eth_typing import BLSPrivateKey, ChecksumAddress, HexStr
from py_ecc.bls import G2ProofOfPossession
from staking_deposit.settings import DEPOSIT_CLI_VERSION
from sw_utils import get_v1_withdrawal_credentials, get_v2_withdrawal_credentials
from sw_utils.signing import (
    DepositData,
    DepositMessage,
    compute_deposit_domain,
    compute_signing_root,
)
from sw_utils.typings import Bytes32
from web3 import Web3

from src.config.networks import NETWORKS
from src.validators.typings import ValidatorType


@dataclass
class Credential:
    private_key: BLSPrivateKey
    network: str
    vault: ChecksumAddress

    # used only for deposit data generation
    validator_type: ValidatorType = ValidatorType.V2

    path: str | None = None
    amount: int | None = None

    @cached_property
    def public_key(self) -> HexStr:
        return Web3.to_hex(G2ProofOfPossession.SkToPk(self.private_key))

    @cached_property
    def private_key_bytes(self) -> bytes:
        return self.private_key.to_bytes(32, 'big')

    @cached_property
    def withdrawal_credentials(self) -> Bytes32:
        if self.validator_type == ValidatorType.V1:
            return get_v1_withdrawal_credentials(self.vault)
        return get_v2_withdrawal_credentials(self.vault)

    def get_deposit_message(self, amount: int) -> DepositMessage:
        return DepositMessage(
            pubkey=Web3.to_bytes(hexstr=self.public_key),
            withdrawal_credentials=self.withdrawal_credentials,
            amount=amount,
        )

    def get_deposit_datum_dict(self, amount: int) -> dict[str, bytes]:
        signed_deposit_datum = self.get_signed_deposit(amount)
        fork_version = NETWORKS[self.network].GENESIS_FORK_VERSION
        datum_dict = signed_deposit_datum.as_dict()
        deposit_message = self.get_deposit_message(amount)
        datum_dict.update({'deposit_message_root': deposit_message.hash_tree_root})
        datum_dict.update({'deposit_data_root': signed_deposit_datum.hash_tree_root})
        datum_dict.update({'fork_version': fork_version})
        datum_dict.update({'network_name': self.network})
        datum_dict.update({'deposit_cli_version': DEPOSIT_CLI_VERSION})
        return datum_dict

    def get_signed_deposit(self, amount: int) -> DepositData:
        fork_version = NETWORKS[self.network].GENESIS_FORK_VERSION
        domain = compute_deposit_domain(fork_version)
        deposit_message = self.get_deposit_message(amount)
        signing_root = compute_signing_root(deposit_message, domain)
        signed_deposit = DepositData(
            **deposit_message.as_dict(),
            # pylint: disable-next=no-member
            signature=bls.Sign(self.private_key_bytes, signing_root),
        )
        return signed_deposit
