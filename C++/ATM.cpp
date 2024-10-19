#include <iostream>
#include <string>
using namespace std;

// Database dummy
string namaNasabah[] = {"Rajwaa", "Rega", "Bimo"};
int saldoNasabah[] = {50000, 75000, 100000};
const int jumlahNasabah = 3;

// Function untuk mencari index nasabah berdasarkan nama
int cariNasabah(string nama)
{
    for (int i = 0; i < jumlahNasabah; i++)
    {
        if (namaNasabah[i] == nama)
        {
            return i;
        }
    }
    return -1; // Jika tidak ditemukan
}

// Function untuk mengecek saldo
void cekSaldo(int index)
{
    cout << "Saldo Anda: Rp " << saldoNasabah[index] << endl;
}

// Function untuk penarikan uang
void tarikUang(int index, int jumlah)
{
    if (saldoNasabah[index] >= jumlah)
    {
        saldoNasabah[index] -= jumlah;
        cout << "Penarikan berhasil! Anda menarik Rp " << jumlah << ". Sisa saldo: Rp " << saldoNasabah[index] << endl;
    }
    else
    {
        cout << "Saldo tidak mencukupi" << endl;
    }
}

// Function utama ATM
void atm()
{
    string nama;
    cout << "Selamat datang!" << endl;
    cout << "Masukkan nama nasabah: ";
    cin >> nama;

    // Mencari index nasabah berdasarkan nama
    int index = cariNasabah(nama);

    if (index == -1)
    {
        cout << "Nama nasabah tidak ditemukan" << endl;
    }
    else
    {
        cout << "Halo " << namaNasabah[index] << "!" << endl;
        cekSaldo(index);

        int jumlahTarik;
        cout << "Masukkan jumlah uang yang ingin diambil: ";
        cin >> jumlahTarik;

        if (jumlahTarik > 0)
        {
            tarikUang(index, jumlahTarik);
        }
        else
        {
            cout << "Jumlah penarikan harus lebih besar dari 0" << endl;
        }
    }
}

int main()
{
    atm();
    return 0;
}