from dataclasses import asdict, dataclass

from sw_utils.networks import NETWORKS as BASE_NETWORKS
from sw_utils.networks import BaseNetworkConfig

MAINNET = 'mainnet'
GNOSIS = 'gnosis'
HOODI = 'hoodi'
CHIADO = 'chiado'

GNO_NETWORKS = [GNOSIS, CHIADO]


@dataclass
class NetworkConfig(BaseNetworkConfig):
    pass


NETWORKS = {
    MAINNET: NetworkConfig(**asdict(BASE_NETWORKS[MAINNET])),
    HOODI: NetworkConfig(**asdict(BASE_NETWORKS[HOODI])),
    GNOSIS: NetworkConfig(
        **asdict(BASE_NETWORKS[GNOSIS]),
    ),
    CHIADO: NetworkConfig(
        **asdict(BASE_NETWORKS[CHIADO]),
    ),
}
