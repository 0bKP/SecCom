from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json


def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    return private_key, public_key


def generate_aes_key(size=32):
    return get_random_bytes(size)


def encrypt_aes_key_with_rsa(aes_key, public_key):
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key


def decrypt_aes_key_with_rsa(encrypted_key, private_key):
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return aes_key


def encrypt_message_with_aes(message, aes_key):
    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(message.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()


def decrypt_message_with_aes(encrypted_message, aes_key):
    data = base64.b64decode(encrypted_message)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    message = cipher.decrypt_and_verify(ciphertext, tag)
    return message.decode()


def exchange_key(finc, *args):
    if finc == "recv":
        recv_rsa_key = args[0]
        aes_key = generate_aes_key()
        encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, recv_rsa_key)


def send_rsa_key(conn):
    private_key, public_key = generate_rsa_keys()
    try:
        serialized_key = json.dumps({
            'key': public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode(),
            'MID': "M0000-000"
        })
        conn.sendall(serialized_key.encode())
    except Exception as e:
        print(f"Error sending key: {e}")


def receive_key(key):
    try:
        public_key = serialization.load_pem_public_key(key.encode())
        return public_key
    except Exception as e:
        print(f"Error receiving key: {e}")
        return None


"""
if __name__ == "__main__":
    # Generowanie kluczy RSA
    private_key, public_key = generate_rsa_keys()

    # Generowanie klucza AES
    aes_key = get_random_bytes(32)  # 256-bitowy klucz AES

    # Szyfrowanie klucza AES kluczem publicznym RSA
    encrypted_aes_key = encrypt_aes_key_with_rsa(aes_key, public_key)

    # Deszyfrowanie klucza AES kluczem prywatnym RSA
    decrypted_aes_key = decrypt_aes_key_with_rsa(encrypted_aes_key, private_key)

    # Szyfrowanie wiadomości
    original_message = "Cześć! To jest zaszyfrowana wiadomość."
    encrypted_message = encrypt_message_with_aes(original_message, aes_key)

    # Deszyfrowanie wiadomości
    decrypted_message = decrypt_message_with_aes(encrypted_message, decrypted_aes_key)

    # Wyświetlenie wyników
    print(f"Oryginalna wiadomość: {original_message}")
    print(f"Zaszyfrowana wiadomość: {encrypted_message}")
    print(f"Odszyfrowana wiadomość: {decrypted_message}")
"""
