# Kora AI

## Project Overview

Kora AI is an artificial intelligence system focused on the nutritional domain. It provides personalized recommendations based on the user's nutritional information and generates feedback based on their food consumption.

## Project Structure

```text
kora-ai/
├── svc-management/
├── svc-agent/
├── svc-ingestion/
├── frontend/
└── docs/
```

* `kora-ai/`: Root directory of the project.
* `svc-management/`: Management microservice.
* `svc-agent/`: Intelligent agent microservice responsible for AI-based reasoning and orchestration.
* `svc-ingestion/`: Data ingestion microservice responsible for processing and preparing knowledge for the vector database.
* `frontend/`: User interface of the system.
* `docs/`: Project and technical documentation.

## Prerequisites

The following tools are required to work with the project:

* **Git** — Used to clone and manage the project repository.
* **Python** — Required for the development of the backend services.

The use of a specific IDE or code editor is optional and can be chosen according to each developer's preferences.

## Installation

### 1\. Clone the repository

Clone the Kora AI repository:

```bash
git clone <repository-url>
```

### 2\. Enter the project directory

```bash
cd kora-ai
```

### 3\. Create a virtual environment

Each Python-based service should have its own virtual environment to keep its dependencies isolated.

For example, to create a virtual environment for `svc-management`:

```bash
cd svc-management
python -m venv .venv
```

The same process should be followed for the other Python-based services when their development begins.

### 4\. Activate the virtual environment

On Windows:

```bash
.venv\\Scripts\\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 5\. Configure the environment

Each service contains its own `.env.example` file. Create the corresponding `.env` file based on the provided example.

Do not commit `.env` files or real credentials to the repository.

### 6\. Verify the project structure

Make sure the repository contains the expected directories:

```text
kora-ai/
├── svc-management/
├── svc-agent/
├── svc-ingestion/
├── frontend/
└── docs/
```

The project is now ready for local development.

## Environment Configuration

Each service manages its own environment variables through a local `.env` file.

The repository provides an `.env.example` file for each service as a template:

```text
kora-ai/
├── svc-management/
│   └── .env.example
├── svc-agent/
│   └── .env.example
├── svc-ingestion/
│   └── .env.example
├── frontend/
└── docs/
```

To configure a service:

1. Navigate to the corresponding service directory.
2. Create a `.env` file based on `.env.example`.
3. Provide the required local configuration values.
4. Keep credentials and other sensitive information only in the local `.env` file.

Example:

```bash
cd svc-management
cp .env.example .env
```

The same process applies to the other services that contain an `.env.example` file.

### Security

* Never commit `.env` files to the repository.
* Never include real credentials in `.env.example`.
* Use `.env.example` only to document the required environment variable names.

## Running the Project

The project is currently in its initial development stage. The application services and their execution environment will be implemented in subsequent development tasks.

Instructions for running the services locally will be added to this section as the corresponding components are implemented.

Once the local execution environment is available, this section will include the required commands and configuration to start the complete system.

## Development Guidelines

Development and collaboration conventions are documented in `CONTRIBUTING.md`.

All contributors should review this document before starting development.

