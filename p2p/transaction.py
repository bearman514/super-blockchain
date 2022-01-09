import time


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


class Block():

    @classmethod
    def from_dict(cls, block_dict):
        return cls(
            block_dict.get('previous_hash'),
            block_dict.get('difficulty'),
            block_dict.get('miner'),
            block_dict.get('miner_rewards')
        )

    def __init__(self, previous_hash, difficulty, miner, miner_rewards) -> None:
        self.previous_hash = previous_hash
        self.hash = ""
        self.difficulty = difficulty
        self.nonce = 0
        self.timestamp = int(time.time())
        self.transactions = []
        self.miner = miner
        self.miner_rewards = miner_rewards
    
    def __str__(self):
        string = f"TimeStamp: {self.timestamp}, Miner: {self.miner}"
        return string