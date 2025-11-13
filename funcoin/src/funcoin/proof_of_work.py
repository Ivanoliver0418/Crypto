from hashlib import sha256

email_body_real = "Hey Ethan, I think you should buy some Bitcoins!"

# We will add the arbitrary data here (a nonce)
nonce = 0

def hash_email(body):
    return sha256(body.encode()).hexdigest()

# Proof-of-work requirement:
# Hash must start with "0000"
target = "0000"

while True:
    # Combine real body + arbitrary data
    email_body_with_nonce = email_body_real + f"nonce: {nonce}"
    # Compute hash
    h = hash_email(email_body_with_nonce)

    # Check if it meets requirement
    if h.startswith(target):            # does the hash start with "0000"?
        print("Found valid email!")
        print("Email body:\n", email_body_with_nonce)
        print("Hash:", h)
        break
    
    # if not valid change nonce
    nonce += 1
