import os, random, struct
import numpy as np
from Crypto.Cipher import AES
from Crypto import Random
import time


def encrypt_file(key, input_path, chunksize=64*1024, use_aesni=True):
    """ Encrypts a file using AES (CBC mode) with the
        given key.

        key:
            The encryption key - a string that must be
            either 16, 24 or 32 bytes long. Longer keys
            are more secure.

        input_path:
            Name of the input file

        output_path:
            If None, '<input_path>.enc' will be used.

        chunksize:
            Sets the size of the chunk which the function
            uses to read and encrypt the file. Larger chunk
            sizes can be faster for some files and machines.
            chunksize must be divisible by 16.
    """
    output_path = os.path.join(os.path.dirname(input_path), 'encrypted_' + os.path.basename(input_path))
    #iv = Random.new().read(16)
    encryptor = AES.new(key, AES.MODE_CTR, use_aesni=use_aesni)
    filesize = os.path.getsize(input_path)
    encryption_time = []
    with open(input_path, 'rb') as infile:
        with open(output_path, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            # outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                start = time.time()
                crypted_chunk = encryptor.encrypt(chunk)
                encryption_time.append(time.time() - start)

                outfile.write(crypted_chunk)
                
        return output_path, np.sum(np.array(encryption_time))





def decrypt_file(key, input_path, chunksize=64 * 1024, use_aesni = True):
    """ Decrypts a file using AES (CBC mode) with the
        given key. Parameters are similar to encrypt_file,
        with one difference: output_path, if not supplied
        will be input_path without its last extension
        (i.e. if input_path is 'aaa.zip.enc' then
        output_path will be 'aaa.zip')
    """
    output_path = os.path.join(os.path.dirname(input_path), 'decrypted_' + os.path.basename(input_path))
    decryption_time = []
    with open(input_path, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        # iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CTR, use_aesni=use_aesni)

        with open(output_path, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break

                start = time.time()
                decrypted_chunk = decryptor.decrypt(chunk)
                decryption_time.append(time.time() - start)

                outfile.write(decrypted_chunk)

            outfile.truncate(origsize)
    return output_path, np.sum(np.array(decryption_time))


