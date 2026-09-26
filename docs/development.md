# Local Development

## Prerequisites

The following tools are required to run the Kora AI development environment:

* Docker
* Docker Compose

## Environment Setup

Each service uses its own environment configuration.

Create the required `.env` files from their corresponding `.env.example` templates:

* `svc-management/.env`
* `svc-agent/.env`
* `.env.postgres`

The `.env` files contain local configuration and secrets and must not be committed to the repository.

## Run the Environment

From the project root, run:

```bash
docker compose up --build
```

This starts the following services:

* `svc-management`
* `svc-agent`
* `postgres`

The first execution builds the application images and creates the required Docker network and PostgreSQL volume.

## Service Access

|Service|Host Port|Container Port|
|-|-:|-:|
|`svc-agent`|8000|8000|
|`svc-management`|8001|8000|
|`postgres`|5432|5432|

The `svc-agent` API documentation is available at:

```text
http://localhost:8000/docs
```

## Stop the Environment

To stop the running containers:

```bash
Ctrl+C
```

To stop and remove the containers and Docker network:

```bash
docker compose down
```

The PostgreSQL data volume is preserved when using `docker compose down`.

## Configuration Validation

Before starting the environment, the Docker Compose configuration can be validated with:

```bash
docker compose config
```

