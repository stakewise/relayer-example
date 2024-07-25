from dataclasses import dataclass

from eth_typing import HexStr
from web3 import Web3

MAINNET = 'mainnet'
GNOSIS = 'gnosis'
HOLESKY = 'holesky'
CHIADO = 'chiado'

GNO_NETWORKS = [GNOSIS, CHIADO]


@dataclass
class NetworkConfig:
    CHAIN_ID: int
    GENESIS_FORK_VERSION: bytes


NETWORKS = {
    MAINNET: NetworkConfig(
        CHAIN_ID=1,
        GENESIS_FORK_VERSION=Web3.to_bytes(hexstr=HexStr('0x00000000')),
    ),
    HOLESKY: NetworkConfig(
        CHAIN_ID=17000,
        GENESIS_FORK_VERSION=Web3.to_bytes(hexstr=HexStr('0x01017000')),
    ),
    GNOSIS: NetworkConfig(
        CHAIN_ID=100,
        GENESIS_FORK_VERSION=Web3.to_bytes(hexstr=HexStr('0x00000064')),
    ),
    CHIADO: NetworkConfig(
        CHAIN_ID=10200,
        GENESIS_FORK_VERSION=Web3.to_bytes(hexstr=HexStr('0x0000006f')),
    ),
}
