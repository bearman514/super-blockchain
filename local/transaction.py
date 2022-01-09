import rsa


class Transaction():

    @classmethod
    def from_dict(cls, transaction_dict):
        return cls(
            transaction_dict.get('sender'),
            transaction_dict.get('receiver'),
            transaction_dict.get('amounts'),
            transaction_dict.get('fee'),
            transaction_dict.get('message')
        )

    def __init__(self, sender, receiver, amounts, fee, message) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amounts = amounts
        self.fee = fee
        self.message = message
    
    def to_string(self):
        transaction_dict = {
            'sender': str(self.sender),
            'receiver': str(self.receiver),
            'amounts': self.amounts,
            'fee': self.fee,
            'message': self.message
        }
        return str(transaction_dict)      

    def sign_transaction(self, private):
        private_key = '-----BEGIN RSA PRIVATE KEY-----\n'
        private_key += private
        private_key += '\n-----END RSA PRIVATE KEY-----\n'
        private_key_pkcs = rsa.PrivateKey.load_pkcs1(private_key.encode('utf-8'))
        transaction_str = self.to_string()
        signature = rsa.sign(transaction_str.encode('utf-8'), private_key_pkcs, 'SHA-1')
        return signature 

    
def initialize_transaction(transaction_dict: dict):
    """transaction_dict : {
        'sender': sender,
        'receiver': receiver,
        'amounts': amounts,
        'fee': fee,
        'message': message
    }
    """
    # No need to check balance
    new_transaction = Transaction.from_dict(transaction_dict)
    return new_transaction

