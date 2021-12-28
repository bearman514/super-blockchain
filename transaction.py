import time


class Transaction():

    def __init__(self, sender, receiver, amounts, fee, message) -> None:
        self.sender = sender
        self.receiver = receiver
        self.amounts = amounts
        self.fee = fee
        self.message = message


class Block():

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