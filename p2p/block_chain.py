import time
import hashlib
import rsa

import sys
import pickle
import socket
import threading

from utils import generate_address

ENCODE_FORMAT = "utf-8"

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


class BlockChain():
    
    def __init__(self) -> None:
        self.adjust_difficulty_blocks = 10
        self.difficulty = 1
        self.block_time = 30
        self.miner_rewards = 10
        self.block_limitation = 32
        self.chain = []
        self.pending_transactions = []

        # For P2P connection
        self.socket_host = "127.0.0.1"
        self.socket_port = int(sys.argv[1])
        self.start_socket_server()

    # def generate_address(self):
    #     public, private = rsa.newkeys(512)
    #     public_key = public.save_pkcs1()
    #     private_key = private.save_pkcs1()
    #     return self.get_address_from_public(public_key), private_key

    # def get_address_from_public(self, public_key):
    #     address = str(public_key).replace('\\n', '')
    #     address = address.replace("b'-----BEGIN RSA PUBLIC KEY-----", "")
    #     address = address.replace("-----END RSA PUBLIC KEY-----'", "")
    #     address = address.replace(' ', '')
    #     print('Address: ', address)
    #     return address

    def create_genesis_block(self):

        print("===== Create genesis block...")

        new_block = Block.from_dict({
            'previous_hash': 'Hello First Block!',
            'difficulty': self.difficulty,
            'miner': 'super-smurf',
            'miner_rewards': self.miner_rewards
        })
        new_block.hash = self.get_hash(new_block, 0)
        self.chain.append(new_block)
    
    # def initialize_transaction(self, transaction_dict: dict):
    #     """transaction_dict : {
    #         'sender': sender,
    #         'receiver': receiver,
    #         'amounts': amounts,
    #         'fee': fee,
    #         'message': message
    #     }
    #     """
    #     sender = transaction_dict.get('sender')
    #     amounts = transaction_dict.get('amounts')
    #     fee = transaction_dict.get('fee')
    #     if self.get_balance(sender) < amounts + fee:
    #         print("Balance not enough!")
    #         return False
    #     #
    #     new_transaction = Transaction.from_dict(transaction_dict)
    #     return new_transaction
    
    # def sign_transaction(self, transaction, private_key):
    #     private_key_pkcs = rsa.PrivateKey.load_pkcs1(private_key)
    #     transaction_str = transaction.to_string()
    #     signature = rsa.sign(transaction_str.encode(ENCODE_FORMAT), private_key_pkcs, 'SHA-1')
    #     return signature
    
    def add_transaction(self, transaction, signature):
        #
        public_key = '-----BEGIN RSA PUBLIC KEY-----\n'
        public_key += transaction.sender
        public_key += '\n-----END RSA PUBLIC KEY-----'
        public_key_pkcs = rsa.PublicKey.load_pkcs1(public_key.encode(ENCODE_FORMAT))

        transaction_str = transaction.to_string()
        if transaction.fee + transaction.amounts > self.get_balance(transaction.sender):
            print("Balance not enough!")
            return False
        
        try:
            #
            rsa.verify(transaction_str.encode(ENCODE_FORMAT), signature, public_key_pkcs)
            print("Authorized successfully!")
            self.pending_transactions.append(transaction)
            return True
        except Exception:
            print("RSA Verified wrong!")

    def mine_block(self, miner):
        start = time.process_time()

        last_block = self.chain[-1]
        new_block = Block(
            last_block.hash,
            self.difficulty,
            miner,
            self.miner_rewards
        )

        self.add_transaction_to_block(new_block)
        new_block.previous_hash = last_block.hash
        new_block.difficulty = self.difficulty
        new_block.hash = self.get_hash(new_block, new_block.nonce)

        while new_block.hash[0: self.difficulty] != '0' * self.difficulty:
            new_block.nonce += 1
            new_block.hash = self.get_hash(new_block, new_block.nonce)
        
        time_consumed = round(time.process_time() - start, 5)
        print(f"Hash found: {new_block.hash} @ difficulty {self.difficulty}, Time cost: {time_consumed}s")

        self.chain.append(new_block)

    def adjust_difficulty(self):
        if len(self.chain) % self.adjust_difficulty_blocks != 1:
            return self.difficulty
        elif len(self.chain) <= self.adjust_difficulty_blocks:
            return self.difficulty
        else:
            start = self.chain[-1 * self.adjust_difficulty_blocks - 1].timestamp
            finish = self.chain[-1].timestamp
            average_time_consumed = round((finish-start) / (self.adjust_difficulty_blocks), 2)

            if average_time_consumed > self.block_time:
                print(f"Average block time: {average_time_consumed}s. Lower the difficulty...")
                self.difficulty -= 1
            else:
                print(f"Average block time: {average_time_consumed}s. High up the difficulty...")
                self.difficulty += 1

####
    def get_hash(self, block, nonce):
        s = hashlib.sha1()
        s.update(
            (
                block.previous_hash
                + str(block.timestamp)
                + self.get_transactions_string(block)
                + str(nonce)
            ).encode(ENCODE_FORMAT)
        )
        h = s.hexdigest()
        return h

    def get_transactions_string(self, block):
        transaction_str = ""
        for transaction in block.transactions:
            transaction_str += transaction.to_string()
        return transaction_str

    def get_balance(self, account: str):
        balance = 0
        for block in self.chain:
            # Check miner reward
            miner = False
            if block.miner == account:
                miner = True
                balance += block.miner_rewards

            for transaction in block.transactions:
                if miner:
                    balance += transaction.fee
                if transaction.sender == account:
                    balance -= transaction.amounts
                    balance -= transaction.fee
                elif transaction.receiver == account:
                    balance += transaction.amounts
        return balance

    def add_transaction_to_block(self, block):
        # Get transaction with highest fee by block_limitation
        self.pending_transactions.sort(key=lambda x: x.fee, reverse=True)

        if len(self.pending_transactions) > self.block_limitation:
            transaction_accepted = self.pending_transactions[:self.block_limitation]
            self.pending_transactions = self.pending_transactions[self.block_limitation:]
        else:
            transaction_accepted = self.pending_transactions
            self.pending_transactions = []

        block.transactions = transaction_accepted

    def verify_blockchain(self):
        previous_hash = ""
        for idx, block in enumerate(self.chain):
            if self.get_hash(block, block.nonce) != block.hash:
                print("Error: Hash not matched!")
                return False
            elif previous_hash != block.previous_hash and idx:
                print("Error: Hash not matched to previous_hash!")
                return False
            previous_hash = block.hash
        print("Hash correct!")
        return True
    
    def start(self):
        address, private = generate_address()
        print(f'Miner address: {address}')
        print(f'Miner private: {private}')
        self.create_genesis_block()
        while True:
            self.mine_block(address)
            self.adjust_difficulty()

    # For P2P
    def start_socket_server(self):
        t = threading.Thread(target=self.wait_for_socket_connection)
        t.start()
    
    def wait_for_socket_connection(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host_port = (self.socket_host, self.socket_port)
            s.bind(host_port)
            s.listen
            while True:
                conn, address = s.accept()
                client_handler = threading.Thread(
                    target=self.receive_socket_message,
                    args=(conn, address)
                )
                client_handler.start()
    
    def receive_socket_message(self, connection, address):
        with connection:
            print(f'Connected by: {address}')
            while True:
                message = connection.recv(1024)
                print(f'[*] Received: {message}')
                try:
                    parsed_message = pickle.loads(message)
                except Exception:
                    print(f'{message} cannot be parsed.')
                if message:
                    if parsed_message['request'] == 'balance':
                        print('Start to get the balance for client...')
                        address = parsed_message['address']
                        balance = self.get_balance(address)
                        response = {
                            "address": address,
                            "balance": balance
                        }
                    elif parsed_message['request'] == 'transaction':
                        print('Start to transaction for client...')
                        new_transaction = parsed_message['data']
                        result, result_message = self.add_transaction(
                            new_transaction,
                            parsed_message['signature']
                        )
                        response = {
                            "result": result,
                            "result_message": result_message
                        }
                    else:
                        response = {
                            "message": "Unknown command."
                        }
                    response_bytes = str(response).encode(ENCODE_FORMAT)
                    connection.sendall(response_bytes)


if __name__ == "__main__":

    block = BlockChain()
    block.start()