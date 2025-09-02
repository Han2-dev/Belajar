#!/usr/bin/env python3
import os
import struct
import sys
import getpass
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes

# Konstanta format file terenkripsi:
# [MAGIC 5 bytes][salt 16][nonce 12][fname_len 2][fname bytes][ciphertext ...][tag 16]
MAGIC_AES = b'RENC1'
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
PBKDF2_ITERS = 200_000
CHUNK_SIZE = 64 * 1024  # 64KB


def derive_key_pbkdf2(password: str, salt: bytes, key_len: int = 32) -> bytes:
    """Turunkan key dari password menggunakan PBKDF2-SHA256."""
    password_bytes = password.encode('utf-8')
    return PBKDF2(password_bytes, salt, dkLen=key_len, count=PBKDF2_ITERS)


def ensure_enc_extension(name: str) -> str:
    """Pastikan nama keluaran berakhiran .enc"""
    if name.lower().endswith('.enc'):
        return name
    return name + '.enc'


def unique_path_if_exists(path: str) -> str:
    """Jika file sudah ada, tambahkan suffix _1, _2, ..."""
    base, ext = os.path.splitext(path)
    i = 1
    candidate = path
    while os.path.exists(candidate):
        candidate = f"{base}_{i}{ext}"
        i += 1
    return candidate


def encrypt_file(path_in: str, out_name: str, password: str):
    """Enkripsi file: menulis file .enc di folder yang sama."""
    if not os.path.isfile(path_in):
        print("File input tidak ditemukan.")
        return

    dir_in = os.path.dirname(path_in) or '.'
    out_name = ensure_enc_extension(out_name)
    out_path = os.path.join(dir_in, out_name)
    out_path = unique_path_if_exists(out_path)

    original_fname = os.path.basename(path_in).encode('utf-8')
    fname_len = len(original_fname)
    if fname_len > 65535:
        print("Nama file asli terlalu panjang.")
        return

    salt = get_random_bytes(SALT_SIZE)
    key = derive_key_pbkdf2(password, salt, key_len=32)

    nonce = get_random_bytes(NONCE_SIZE)
    header = MAGIC_AES + salt + nonce + struct.pack('>H', fname_len) + original_fname

    try:
        with open(path_in, 'rb') as fin, open(out_path, 'wb') as fout:
            fout.write(header)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            while True:
                chunk = fin.read(CHUNK_SIZE)
                if not chunk:
                    break
                ct_chunk = cipher.encrypt(chunk)
                fout.write(ct_chunk)
            tag = cipher.digest()
            fout.write(tag)
        print(f"Enkripsi selesai. File terenkripsi: {out_path}")
    except Exception as e:
        try:
            if os.path.exists(out_path):
                os.remove(out_path)
        except OSError:
            pass
        print("Terjadi kesalahan saat enkripsi:", str(e))


def decrypt_file(path_in: str, password: str):
    """Dekripsi file .enc; hasil di folder sama dengan nama asli."""
    if not os.path.isfile(path_in):
        print("File input tidak ditemukan.")
        return
    dir_in = os.path.dirname(path_in) or '.'

    try:
        with open(path_in, 'rb') as fin:
            magic = fin.read(5)
            if magic != MAGIC_AES:
                print("File bukan hasil enkripsi skrip ini.")
                return

            salt = fin.read(SALT_SIZE)
            nonce = fin.read(NONCE_SIZE)
            fname_len_bytes = fin.read(2)
            if len(fname_len_bytes) < 2:
                print("Format file rusak.")
                return
            fname_len = struct.unpack('>H', fname_len_bytes)[0]
            original_fname = fin.read(fname_len).decode('utf-8', errors='ignore')
            header_len = 5 + SALT_SIZE + NONCE_SIZE + 2 + fname_len
            total_size = os.path.getsize(path_in)

            if total_size < header_len + TAG_SIZE:
                print("File terenkripsi rusak (size tidak sesuai).")
                return

            ciphertext_len = total_size - header_len - TAG_SIZE
            out_path = os.path.join(dir_in, original_fname)
            out_path = unique_path_if_exists(out_path)

            key = derive_key_pbkdf2(password, salt, key_len=32)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

            try:
                with open(out_path, 'wb') as fout:
                    remaining = ciphertext_len
                    while remaining > 0:
                        read_size = CHUNK_SIZE if remaining >= CHUNK_SIZE else remaining
                        chunk = fin.read(read_size)
                        if not chunk:
                            break
                        pt_chunk = cipher.decrypt(chunk)
                        fout.write(pt_chunk)
                        remaining -= len(chunk)

                    tag = fin.read(TAG_SIZE)
                    cipher.verify(tag)
                    print(f"Dekripsi berhasil. File diletakkan di: {out_path}")
            except Exception as e:
                try:
                    if os.path.exists(out_path):
                        os.remove(out_path)
                except OSError:
                    pass
                print("Password salah atau file rusak (gagal verifikasi).")
    except Exception as e:
        print("Terjadi kesalahan saat membuka file:", str(e))


def ask_password(prompt="Password: "):
    try:
        return getpass.getpass(prompt)
    except Exception:
        print("(Peringatan: input password tidak disembunyikan)")
        return input(prompt)


def main_loop():
    print("=== Simple File Encryptor / Decryptor ===")

    while True:
        print("\nPilih aksi:")
        print("  1) Enkripsi file")
        print("  2) Dekripsi file")
        print("  3) Keluar")
        choice = input("Masukkan pilihan (1/2/3): ").strip()
        if choice == '1':
            path_in = input("Path file yang mau dienkrip: ").strip()
            if not path_in:
                print("Path tidak boleh kosong.")
                continue
            out_name = input("Nama output (tanpa path): ").strip()
            if not out_name:
                print("Nama output tidak boleh kosong.")
                continue
            password = ask_password("Masukkan password untuk enkripsi: ")
            if not password:
                print("Password kosong, batalkan.")
                continue
            encrypt_file(path_in, out_name, password)
        elif choice == '2':
            path_in = input("Path file .enc yang mau didekrip: ").strip()
            if not path_in:
                print("Path tidak boleh kosong.")
                continue
            password = ask_password("Masukkan password untuk dekripsi: ")
            if not password:
                print("Password kosong, batalkan.")
                continue
            decrypt_file(path_in, password)
        elif choice == '3' or choice.lower() in ('q', 'quit', 'exit'):
            print("Keluar.")
            break
        else:
            print("Pilihan tidak valid. Coba lagi.")


if __name__ == '__main__':
    main_loop()
