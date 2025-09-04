def tambah(x, y):
    return x + y
def kurang(x, y):
    return x - y
def kali(x, y):
    return x * y
def bagi(x, y):
    if y == 0:
        return print("Tidak bisa dibagi dengan 0")
    else:
        return x / y

def main():
    print("Kalkulator")
    while True:
        pilihan_op = input("Pilih operasi (+, -, *, /): ").strip()
        num1 = float(input("Masukkan angka pertama: ").strip())
        num2 = float(input("Masukkan angka kedua: ").strip())
        if pilihan_op == '+':
            hasil = tambah(num1, num2)
        elif pilihan_op == '-':
            hasil = kurang(num1, num2)
        elif pilihan_op == '*':
            hasil = kali(num1, num2)
        elif pilihan_op == '/':
            hasil = bagi(num1, num2)
        else:
            print("Input invalid")
        print(f"Hasil: {num1} {pilihan_op} {num2} = {hasil}")
    
if __name__ == "__main__":
    main()