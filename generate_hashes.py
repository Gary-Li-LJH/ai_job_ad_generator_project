# generate_hashes.py
import streamlit_authenticator as stauth

# Passwords to hash
passwords_to_hash = ["optus123", "optushr123"]

# Create a Hasher object without passing arguments to constructor
hasher = stauth.Hasher()

# Generate hashed passwords
hashed_passwords = []
for password in passwords_to_hash:
    hashed_password = hasher.hash(password)
    hashed_passwords.append(hashed_password)

print(hashed_passwords)