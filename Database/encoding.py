from cryptography.fernet import Fernet

# Key for encrypting and decrypting the password
key = b'd6G-mIic2DdbBRAojMU7OZeS_h3B-y2-HUv-0M7DUtQ='


# Creating a cipher object
cipher = Fernet(key)

# Function that will encrypt the password of each user
def encrypt(password):
    # Convert the password to bytes
    encoded_password = password.encode()

    # Encrypt the password to cipher text
    encrypted_password = cipher.encrypt(encoded_password)

    # Returning the encrypted password
    return encrypted_password

# Function that will decrypt an encrypted password
def decrypt(password):
    # Decrypt the password
    decrypted_password = cipher.decrypt(password)

    # Convert decrypted password back to string
    decrypted_password = decrypted_password.decode()

    # Returning the decrypted password
    return decrypted_password

