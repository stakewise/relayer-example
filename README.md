# Relayer example

The Relayer example for Stakewise v3-operator service

Relayer-Operator api communication is described in [Operator docs](https://docs.stakewise.io/for-operators/operator-service/running-as-api-service).

In this example, keystores are stored in a local folder.

## Running with Docker

```bash
docker run --rm -ti \
-u $(id -u):$(id -g) \
europe-west4-docker.pkg.dev/stakewiselabs/public/relayer-example
```

## Running from sources

### Setup

1. Install [poetry](https://python-poetry.org/)
2. `poetry install`
3. `cp .env.example .env`
4. Fill .env file with appropriate values

### Run

1. `poetry shell`
2. `export PYTHONPATH=.`
3. `python src/app.py`

## App structure

Relayer-example is Python app made with FastAPI.

## API Endpoints

### Register New Validators

**POST** `/validators`
**Request Body**:

```json
{
  "vault": "0x1234...",
  "validators_start_index": int,
  "amounts": int[],
  "validator_type": "ValidatorType"
}
```

- `vault` - Address of the vault contract to which the validators will be registered.
- `validators_start_index` - Validator index for the first validator in the batch.
- `amounts` - List of deposit amounts for each validator. Value provided in Gwei.
- `validator_type` - Type of validator to create. Possible values: `V1` or `V2`.

**Response:**

```json
{
  "validators": [
    {
      "public_key": "string",
      "deposit_signature": "string",
      "amount": int,
      "exit_signature": "string"
    }
  ],
  "validators_manager_signature": "string"
}
```

---

### Fund Compounding Validators

**POST** `/fund`
**Request Body:**

```json
{
  "vault": "0x1234...",
  "public_keys": str[],
  "amounts": int[]
}
```

- `vault` - Address of the vault contract to which the validators will be funded.
- `public_keys` - List of public keys of validators to fund.
- `amounts` - List of amounts to fund into each validator. Value provided in Gwei.

**Response:**

```json
{
  "validators": [
    {
      "public_key": "string",
      "deposit_signature": "string",
      "amount": int
    }
  ],
  "validators_manager_signature": "string"
}
```

---

### Get Signature for Withdraw Funds from Validators Transaction

**POST** `/withdraw`
**Request Body:**

```json
{
  "vault": "0x1234...",
  "public_keys": str[],
  "amounts": int[]
}
```

- `vault` - Address of the vault contract to which the validators will be withdrawn.
- `public_keys` - List of public keys of validators to withdraw from.
- `amounts` - List of amounts to withdraw from each validator. Value provided in Gwei.

**Response:**

```json
{
  "validators_manager_signature": "string"
}
```

---

### Get Signature for Consolidate Validators Transaction

**POST** `/consolidate`
**Request Body:**

```json
{
  "vault": "0x1234...",
  "source_public_keys": str[],
  "target_public_keys": str[]
}
```

- `vault` - Address of the vault contract to which the validators will be consolidated.
- `source_public_keys` - List of public keys of validators to consolidate from.
- `target_public_keys` - List of public keys of validators to consolidate to.

**Response:**

```json
{
  "validators_manager_signature": "string"
}
```

---

### Fetch info about relayer

**Get** `/info`

**Response:**

```json
{
  "network": "string"
}
```

### Folders structure

```text
src/                            # sources root
|-- common/                     #
|   |-- abi/                    # contracts ABI
|   |-- clients.py              # execution client
|   |-- contracts.py            # validators registry contract
|-- config/
|   |-- networks.py             # network configs
|   |-- settings.py             # app settings
|-- validators/                 #
|   |-- credentials.py          # Credential and CredentialManager used to generate keystores
|   |-- endpoints.py            # api endpoints
|   |-- keystore.py             # local keystore storage
|   |-- schema.py               # api request/response schema
|   |-- typings.py              # dataclasses
|   |-- validators.py           # functions for creating validators and exit signatures
|   |-- validators_manager.py   # functions for working with validators manager
```
