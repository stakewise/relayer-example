import secrets
from dataclasses import dataclass
from functools import cached_property

import milagro_bls_binding as bls
from eth_typing import BLSPrivateKey, HexAddress, HexStr
from py_ecc.bls import G2ProofOfPossession
from py_ecc.optimized_bls12_381.optimized_curve import curve_order
from staking_deposit.key_handling.key_derivation.path import path_to_nodes
from staking_deposit.key_handling.key_derivation.tree import derive_child_SK
from staking_deposit.settings import DEPOSIT_CLI_VERSION
from sw_utils import get_v1_withdrawal_credentials
from sw_utils.signing import (
    DepositData,
    DepositMessage,
    compute_deposit_domain,
    compute_signing_root,
)
from sw_utils.typings import Bytes32
from web3 import Web3

from src.config.networks import NETWORKS

# Set path as EIP-2334 format
# https://eips.ethereum.org/EIPS/eip-2334
PURPOSE = '12381'
COIN_TYPE = '3600'

DEPOSIT_AMOUNT = Web3.to_wei(32, 'ether')
DEPOSIT_AMOUNT_GWEI = int(Web3.from_wei(DEPOSIT_AMOUNT, 'gwei'))


@dataclass
class Credential:
    private_key: BLSPrivateKey
    path: str
    network: str
    withdrawal_address: HexAddress

    @cached_property
    def public_key(self) -> HexStr:
        return Web3.to_hex(G2ProofOfPossession.SkToPk(self.private_key))

    @cached_property
    def private_key_bytes(self) -> bytes:
        return self.private_key.to_bytes(32, 'big')

    @cached_property
    def amount(self) -> int:
        return DEPOSIT_AMOUNT_GWEI

    @cached_property
    def withdrawal_credentials(self) -> Bytes32:
        return get_v1_withdrawal_credentials(self.withdrawal_address)

    @property
    def deposit_message(self) -> DepositMessage:
        return DepositMessage(
            pubkey=Web3.to_bytes(hexstr=self.public_key),
            withdrawal_credentials=self.withdrawal_credentials,
            amount=self.amount,
        )

    @property
    def signed_deposit(self) -> DepositData:
        fork_version = NETWORKS[self.network].GENESIS_FORK_VERSION
        domain = compute_deposit_domain(fork_version)
        signing_root = compute_signing_root(self.deposit_message, domain)
        signed_deposit = DepositData(
            **self.deposit_message.as_dict(),
            # pylint: disable-next=no-member
            signature=bls.Sign(self.private_key_bytes, signing_root),
        )
        return signed_deposit

    def deposit_datum_dict(self) -> dict[str, bytes]:
        signed_deposit_datum = self.signed_deposit
        fork_version = NETWORKS[self.network].GENESIS_FORK_VERSION
        datum_dict = signed_deposit_datum.as_dict()
        datum_dict.update({'deposit_message_root': self.deposit_message.hash_tree_root})
        datum_dict.update({'deposit_data_root': signed_deposit_datum.hash_tree_root})
        datum_dict.update({'fork_version': fork_version})
        datum_dict.update({'network_name': self.network})
        datum_dict.update({'deposit_cli_version': DEPOSIT_CLI_VERSION})
        return datum_dict


class CredentialManager:
    @staticmethod
    def generate_credentials(
        count: int,
        start_index: int,
        network: str,
        withdrawal_address: HexAddress,
    ) -> list[Credential]:
        credentials = []
        private_key = BLSPrivateKey(secrets.randbelow(curve_order))
        for index in range(start_index, start_index + count):
            credential = CredentialManager._generate_credential(
                network, withdrawal_address, private_key, index
            )
            credentials.append(credential)
        return credentials

    @staticmethod
    def _generate_credential(
        network: str, vault: HexAddress, private_key: BLSPrivateKey, index: int
    ) -> Credential:
        signing_key_path = f'm/{PURPOSE}/{COIN_TYPE}/{index}/0/0'
        nodes = path_to_nodes(signing_key_path)

        for node in nodes:
            private_key = BLSPrivateKey(derive_child_SK(parent_SK=private_key, index=node))

        return Credential(
            private_key=private_key,
            path=signing_key_path,
            network=network,
            withdrawal_address=vault,
        )
