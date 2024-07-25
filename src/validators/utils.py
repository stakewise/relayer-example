import json
import os

from eth_account import Account
from eth_account.signers.local import LocalAccount

from src.config import settings


def load_validators_manager_account() -> LocalAccount:
    keystore_file = settings.validators_manager_key_file
    keystore_password_file = settings.validators_manager_password_file
    if not os.path.isfile(keystore_file):
        raise ValueError(f"Can't open key file. Path: {keystore_file}")
    if not os.path.isfile(keystore_password_file):
        raise ValueError(f"Can't open password file. Path: {keystore_password_file}")

    with open(keystore_file, 'r', encoding='utf-8') as f:
        keyfile_json = json.load(f)
    with open(keystore_password_file, 'r', encoding='utf-8') as f:
        password = f.read().strip()
    key = Account.decrypt(keyfile_json, password)
    return Account().from_key(key)
