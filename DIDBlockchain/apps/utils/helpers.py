import json
from datetime import datetime
import time
import base64

class BlockchainHelpers:
    @staticmethod
    def serialize_datetime(dt):
        """Convert datetime object to ISO format string"""
        return dt.isoformat() if isinstance(dt, datetime) else dt

    @staticmethod
    def deserialize_datetime(dt_str):
        """Convert ISO format string to datetime object"""
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def encode_base64(data):
        """Encode data to base64"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def decode_base64(data):
        """Decode base64 data"""
        try:
            return base64.b64decode(data).decode('utf-8')
        except:
            return None

    @staticmethod
    def json_serialize(obj):
        """Serialize object to JSON string with datetime handling"""
        def default(o):
            if isinstance(o, datetime):
                return o.isoformat()
            return str(o)
        return json.dumps(obj, default=default)

    @staticmethod
    def json_deserialize(json_str):
        """Deserialize JSON string to object"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def validate_address(address):
        """Validate blockchain address format"""
        if not isinstance(address, str):
            return False
        if not len(address) == 64:  # Assuming SHA256 hex string format
            return False
        try:
            int(address, 16)  # Check if it's a valid hex string
            return True
        except ValueError:
            return False

    @staticmethod
    def timestamp():
        """Get current timestamp in milliseconds"""
        return int(time.time() * 1000)

    @staticmethod
    def format_timestamp(timestamp):
        """Format timestamp to human-readable format"""
        dt = datetime.fromtimestamp(timestamp / 1000)
        return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    @staticmethod
    def chunk_list(lst, chunk_size):
        """Split list into chunks of specified size"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

    @staticmethod
    def validate_transaction_format(transaction):
        """Validate transaction data format"""
        required_fields = ['sender', 'recipient', 'amount', 'timestamp', 'signature']
        return all(field in transaction for field in required_fields)

    @staticmethod
    def calculate_fee(amount, fee_rate=0.001):
        """Calculate transaction fee"""
        return amount * fee_rate

    @staticmethod
    def format_amount(amount, decimals=8):
        """Format amount with specified decimal places"""
        return f"{amount:.{decimals}f}"