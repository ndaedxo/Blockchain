import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

class DIDBlockchainLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.setup_loggers()

    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def setup_loggers(self):
        """Setup different loggers for various components"""
        # Main application logger
        self.setup_logger('blockchain', 'blockchain.log')
        # Transaction logger
        self.setup_logger('transactions', 'transactions.log')
        # Security logger
        self.setup_logger('security', 'security.log')
        # API logger
        self.setup_logger('api', 'api.log')
        # Consensus logger
        self.setup_logger('consensus', 'consensus.log')

    def setup_logger(self, name, log_file):
        """Setup individual logger with specified configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # Create handlers
        file_handler = RotatingFileHandler(
            os.path.join(self.log_dir, log_file),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        console_handler = logging.StreamHandler()

        # Create formatters and add it to handlers
        file_format = logging.Formatter(
            '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
        )
        console_format = logging.Formatter(
            '%(asctime)s [%(name)s] [%(levelname)s] %(message)s'
        )

        file_handler.setFormatter(file_format)
        console_handler.setFormatter(console_format)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    @staticmethod
    def get_logger(name):
        """Get logger by name"""
        return logging.getLogger(name)

    def log_transaction(self, transaction_data):
        """Log transaction details"""
        logger = self.get_logger('transactions')
        logger.info(f"New transaction: {transaction_data}")

    def log_block_creation(self, block_data):
        """Log block creation"""
        logger = self.get_logger('blockchain')
        logger.info(f"New block created: {block_data}")

    def log_security_event(self, event_type, details):
        """Log security-related events"""
        logger = self.get_logger('security')
        logger.warning(f"Security event - {event_type}: {details}")

    def log_api_request(self, method, endpoint, response_status):
        """Log API requests"""
        logger = self.get_logger('api')
        logger.info(f"API Request - Method: {method}, Endpoint: {endpoint}, Status: {response_status}")

    def log_consensus_event(self, event_type, details):
        """Log consensus-related events"""
        logger = self.get_logger('consensus')
        logger.info(f"Consensus event - {event_type}: {details}")