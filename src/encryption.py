from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
import sys


def clean_line():
    sys.stdout.write("\033[2K")
    sys.stdout.write("\r")
    sys.stdout.flush()


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


def send_rsa_key(conn, key=None):
    if not key:
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

        clean_line()
        print("[*] Successfully sent RSA key!")
        return private_key
    except Exception as e:
        print(f"[!] Error sending key: {e}")


def send_aes_key(conn, key=None):
    if not key:
        aes_key = generate_aes_key()
    try:
        data = json.dumps({
            'key': key.hex(),
            'MID': "M0000-001"
        })
        conn.sendall(data.encode())

        clean_line()
        print("[*] Successfully sent AES key!")
    except Exception as e:
        print(f"[!] Error sending AES key: {e}")


def receive_rsa_key(key):
    try:
        public_key = serialization.load_pem_public_key(key.encode())

        clean_line()
        print("[*] Received RSA key successfully!")
        return public_key
    except Exception as e:
        print(f"[!] Error receiving key: {e}")
        return None


def receive_aes_key(key, rsa_private_key):
    try:
        aes_key_dehexify = bytes.fromhex(key)
        decrypted_aes_key = decrypt_aes_key_with_rsa(aes_key_dehexify, rsa_private_key)

        clean_line()
        print(f"[*] Received AES key successfully!")
        return decrypted_aes_key
    except Exception as e:
        print(f"[!] Error receiving key: {e}")
        return None

