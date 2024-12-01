import pytest
from .blockchain import Blockchain
from .block import Block
from .transaction import Transaction
from .exceptions import InvalidBlockError, InvalidTransactionError
import time

@pytest.fixture
def blockchain():
    return Blockchain()

def test_add_valid_transaction(blockchain):
    transaction = Transaction(sender="address1", identity_data={"name": "Alice"}, 
                              timestamp=time(), fee=0.01)
    blockchain.add_transaction(transaction)
    assert len(blockchain.pending_transactions) == 1

def test_invalid_transaction_signature(blockchain):
    transaction = Transaction(sender="address1", identity_data={"name": "Alice"}, 
                              timestamp=time(), fee=0.01)
    transaction.signature = "invalid_signature"
    
    with pytest.raises(InvalidTransactionError):
        blockchain.add_transaction(transaction)
        
def test_add_block(blockchain):
    valid_block = Block(index=1, transactions=[], timestamp=time(),
                        previous_hash="0" * 64, validator="validator_address")
    blockchain.add_block(valid_block, proof="proof", validator_signature="signature")
    assert len(blockchain.chain) == 2
