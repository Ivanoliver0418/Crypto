from hashlib import sha256

alices_message = """Hello Bob, Let's meet at the Kruger National Park on
2020-12-12 at 1pm."""
alices_hash = "0c79c2bd7a88dee596f0ab6d1bc21c1e16d105a5610e65269cd7c20cb58244bf"
hash_message = sha256(("p@55w0rd" + alices_message).encode()).hexdigest()

if hash_message == alices_hash:
    print("Message has not been tampered with")
else:
    print("Someone tampered with the message")
