# DIDBlockchain:  Blockchain System

## Overview

**DIDBlockchain** is a decentralized identity verification system built using Django. It leverages blockchain technology with a Proof of Stake (PoS) consensus mechanism to provide secure and transparent identity management. The project includes a web interface for administrators, an API for external integrations, and blockchain core functionality.

---

## Features

1. **Blockchain Functionality**:  
   - Block and transaction management  
   - Proof of Stake (PoS) consensus  
   - Validator management  
   - Security features like hashing and digital signatures  

2. **Django Integration**:  
   - Modular design for maintainability  
   - Web interface for blockchain management  
   - RESTful API for external interaction  

3. **Web Application**:  
   - Dashboard for blockchain statistics  
   - Blockchain explorer for viewing blocks and transactions  
   - Transaction and validator management  
   - User authentication and registration  

4. **Wallet Management**:  
   - Support for creating and managing digital wallets  

---

## Directory Structure

### Project Root (`DIDBlockchain/`)
- **`__init__.py`**: Marks the directory as a Python package.  
- **`settings.py`**: Django project configuration.  
- **`urls.py`**: Root URL routing for the project.  
- **`wsgi.py` / `asgi.py`**: Deployment entry points for WSGI/ASGI servers.  

### `apps/`
#### `blockchain/`
Core blockchain implementation:
- `blockchain.py`: Main blockchain logic.  
- `block.py`: Defines block structure.  
- `transaction.py`: Handles transaction data.  
- `consensus.py`: Proof of Stake logic.  
- `validator.py`: Validator management.  
- `security.py`: Security functions like hashing and encryption.  

#### `api/`
REST API for interacting with the blockchain:
- `views.py`: API view functions.  
- `urls.py`: API URL routing.  
- `serializers/`: Data serialization for API interactions.  
  - Includes serializers for blocks, transactions, validators, and DID documents.  
- `authentication.py`: User and validator authentication logic.  

#### `utils/`
Shared utilities for the project:
- `config.py`: Configuration settings.  
- `logger.py`: Application-wide logging.  
- `helpers.py`: Miscellaneous helper functions.  

#### `webapp/`
Django-based web interface:
- `views.py`: Handles template rendering for the web app.  
- `urls.py`: URL routing for the web app.  
- `static/`: CSS, JS, and image files.  
- `templates/`: HTML templates for UI.  
  - Includes pages for dashboard, blocks, transactions, validators, and user management.  

#### `tests/`
Unit and integration tests:
- `test_blockchain.py`: Blockchain-related tests.  
- `test_api.py`: API endpoint tests.  
- `test_security.py`: Security feature tests.  

#### `docs/`
Documentation for the project:
- `index.md`: Introduction, setup, and usage instructions.  
- `architecture.md`: Detailed system architecture overview.  
- `api_reference.md`: API endpoint documentation.  

#### `wallet/`
Digital wallet management:
- `models.py`: Wallet models.  
- `views.py`: Wallet-related views.  
- `urls.py`: Routing for wallet features.  
- `serializers.py`: Wallet data serializers.  

---

## Setup Instructions

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/yourusername/DIDBlockchain.git
   cd DIDBlockchain
   ```

2. **Install Dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Migrations**:  
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run the Development Server**:  
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:  
   Open your browser and go to `http://127.0.0.1:8000`.

---

## Usage

- **Admin Dashboard**: Navigate to `/admin` for user and blockchain management.  
- **Blockchain Explorer**: View blocks, transactions, and validators.  
- **API Integration**: Use the provided API endpoints to interact with the blockchain programmatically. See `docs/api_reference.md` for details.  

---

## License
This project is licensed under the terms specified in the `LICENSE` file.

For questions or contributions, please contact the project maintainers.