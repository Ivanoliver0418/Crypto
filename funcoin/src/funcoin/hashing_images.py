from hashlib import sha256

file = open("image1.jpg", "rb")
hash = sha256(file.read()).hexdigest()
file.close()

print(f"The hash of the file is: {hash}")
