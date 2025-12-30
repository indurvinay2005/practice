# Encryption of String Program

import random              # imports the random module so we can shuffle the key list
import string              # imports the string module which contains letters, digits, punctuation

# create a string 'chars' that includes:
# - space character
# - punctuation symbols
# - digits 0-9
# - lowercase + uppercase letters
chars = " " + string.punctuation + string.digits + string.ascii_letters

chars = list(chars)        # convert the whole string into a list (each character becomes one list item)
key = chars.copy()         # make a copy of chars (this will become the shuffled encryption key)

random.shuffle(key)        # randomly shuffle the key list to generate secret mapping

print(f"chars: {chars}")   # print original list of characters
print(f"key: {key}")       # print shuffled version (encryption key)


# ------------------- ENCRYPTION -------------------

plain_text = input("Enter a msg to encrypt: ")  # user enters message to encrypt
cipher_text = ""                                 # empty string to store encrypted message

# loop through each letter in the input text
for letter in plain_text:
    index = chars.index(letter)                  # find the index of the letter in chars list
    cipher_text += key[index]                    # take character from key list at same index

print(f"Orginal message: {plain_text}")          # show original message
print(f"Encrypted Message:{cipher_text}")         # show encrypted output


# ------------------- DECRYPTION -------------------

cipher_text = input("Enter encrypted msg to decrypt: ")  # encrypted text from user
plain_text = ""                                           # empty string to store decrypted result

# loop through each encrypted character
for letter in cipher_text:
    index = key.index(letter)                 # find letter's index in key list (reverse mapping)
    plain_text += chars[index]                # take character from chars list at same index

print(f"Encrypted Message: {cipher_text}")    # print encrypted input
print(f"Orginal message: {plain_text}")       # print decrypted original message
