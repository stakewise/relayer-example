from sw_utils import get_execution_client

import src
from src.config import settings

OPERATOR_USER_AGENT = f'StakeWise Relayer {src.__version__}'


execution_client = get_execution_client(
    [settings.execution_endpoint],
    timeout=settings.execution_timeout,
    retry_timeout=settings.execution_retry_timeout,
    user_agent=OPERATOR_USER_AGENT,
)
