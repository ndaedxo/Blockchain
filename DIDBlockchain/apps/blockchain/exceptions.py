class BlockchainError(Exception):
    """Base class for exceptions in the blockchain module."""
    pass

class InvalidBlockError(BlockchainError):
    """Exception raised for invalid blocks."""
    pass

class InvalidTransactionError(BlockchainError):
    """Exception raised for invalid transactions."""
    pass
