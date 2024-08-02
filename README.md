# Relayer example

The Relayer example for Stakewise v3-operator service

Relayer-Operator api communication is described in [Operator docs](https://docs.stakewise.io/for-operators/operator-service/running-as-api-service).

In this example keystores and deposit-data file were not created in advance. 
Relayer generates validator credentials on the fly.

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

### Folders structure

```text
src/                            # sources root
|-- common/                     # 
|   |-- abi/                    # contracts ABI
|   |-- clients.py              # execution client
|   |-- contracts.py            # validators registry contract
|   |-- credentials.py          # Credential and CredentialManager used to generate keystores
|-- config/
|   |-- networks.py             # network configs
|   |-- settings.py             # app settings
|-- validators/                 #
|   |-- endpoints.py            # api endpoints
|   |-- schema.py               # api request/response schema
|   |-- validators_manager.py   # functions for working with validators manager
|   |-- typings.py              # dataclasses
```
