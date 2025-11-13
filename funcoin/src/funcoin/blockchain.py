import json

from datetime import datetime
from hashlib import sha256

class Blockchain(object):
    def __init__(self):
        self.chain = []  # holds all the blocks
        self.pending_transactions = []  # stores transaction that are not in
                                        # a block yet
        
        # Create the genesis block
        print("Creating genesis block")
        self.new_block()
            
    def last_block(self):
        # Returns the last block in the chain (if there are blocks) 
        if self.chain:
            return self.chain[-1]
        else:
            return None

    def new_block(self, previous_hash=None):
        # Generate a new block and adds it to the chain
        block = {
            'index': len(self.chain),
            'timestamp': datetime.utcnow().isoformat(),
            'transaction': self.pending_transactions,
            'previous_hash': previous_hash,
        }

        # Get the hash to this new block, and add it to the block
        block_hash = self.hash(block)
        block["hash"] = block_hash  # Add a new key yo the dictionary where
                                    # hash have the whole block hashed

        # Reset the list of pending transactions
        self.pending_transactions = []

        # Add the block to the chain
        self.chain.append(block)
        print(f"Created block {block['index']}")
        return block

    @staticmethod
    def hash(block):
        # Hashes the Block
        # We ensure the dictionary is sorted or we'll have inconsistent hashes

        block_string = json.dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def new_transaction(self, sender, recipient, amount):
        # Adds a new transaction to the list of pending transactions
        self.pending_transactions.append({
            "recipient": recipient,
            "sender": sender,
            "amount": amount,
        })
