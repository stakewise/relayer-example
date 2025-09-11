import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.common.app_state import AppState
from src.common.endpoints import router as info_router
from src.common.setup_logging import setup_logging
from src.config import settings
from src.validators.endpoints import router
from src.validators.keystore import LocalKeystore
from src.validators.validators_manager import load_validators_manager_account

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_instance: FastAPI) -> AsyncIterator:  # pylint:disable=unused-argument
    app_state = AppState()

    # load validators manager account
    validators_manager = load_validators_manager_account()
    app_state.validators_manager_account = validators_manager
    logger.info('validators manager address: %s', validators_manager.address)

    # load keystore
    if settings.keystores_dir:
        keystore = await LocalKeystore.load()
        app_state.keystore = keystore

    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(  # type: ignore
    CORSMiddleware,  # type: ignore
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(router)
app.include_router(info_router)


if __name__ == '__main__':
    uvicorn.run(app, host=settings.relayer_host, port=settings.relayer_port)
