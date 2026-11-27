# PO Calculator — Multi Brand & Marketplace

Aplikasi Streamlit untuk menghitung PO unik dari file Excel Jubelio dan Desty, memetakan warehouse ke format Daily Order masing-masing brand, dan mengekspor satu file Excel berisi rekap gabungan, rincian per marketplace, serta audit nomor pesanan.

## Fitur versi pertama

- Upload file Excel Jubelio dan/atau Desty.
- Pilih brand.
- Membaca kolom berdasarkan nama header, bukan posisi kolom yang tetap.
- Menghitung nomor pesanan unik meskipun satu pesanan memiliki banyak baris produk.
- Mengecualikan status Cancel, Return/Retur, Unpaid, dan Belum Bayar.
- Mengikuti tanggal asli dari file transaksi.
- Pemetaan warehouse berdasarkan master Daily Order brand.
- Pemetaan warehouse yang tidak dikenal dapat dipilih manual sebelum ekspor.
- Ekspor satu file Excel: Daily Order gabungan, sheet per marketplace, dan Audit Pesanan Unik.
- BigSeller belum diaktifkan pada versi pertama. Brand yang hanya memakai BigSeller (Bumi Tauhid) dan konfigurasi BigSeller/Shopee (Safwan) belum dapat diproses pada rilis ini.

## Struktur repository

```text
po-calculator/
├── app.py
├── requirements.txt
└── README.md
```

## Menjalankan di komputer

1. Install Python 3.10 atau lebih baru.
2. Download/clone repository.
3. Buka terminal pada folder project.
4. Install dependency:

```bash
pip install -r requirements.txt
```

5. Jalankan:

```bash
streamlit run app.py
```

6. Browser akan membuka aplikasi Streamlit.

## Upload ke GitHub

1. Buat repository baru di GitHub, misalnya `po-calculator`.
2. Upload `app.py`, `requirements.txt`, dan `README.md` ke root repository.
3. Pastikan nama file utama tepat `app.py`.

## Deploy ke Streamlit Community Cloud

1. Buka https://share.streamlit.io/
2. Login menggunakan akun GitHub.
3. Klik **Create app**.
4. Pilih repository `po-calculator`.
5. Branch: `main`.
6. Main file path: `app.py`.
7. Klik **Deploy**.
8. Setelah aplikasi selesai dibangun, buka URL Streamlit yang diberikan.

## Cara menggunakan

1. Pilih brand di sidebar.
2. Upload file sumber sesuai brand:
   - CAVE, Yummys, Essens, BMYT, Hexxa, NDR, dan brand Jubelio lain: upload file Jubelio.
   - Jamu Jago: upload file Desty.
3. Periksa ringkasan data dan contoh transaksi.
4. Periksa tabel pemetaan warehouse. Jika muncul `⚠ Belum dipetakan`, pilih kolom Daily Order yang benar.
5. Ubah Category tanggal jika bukan Daily (Double Date atau Payday).
6. Periksa hasil PO gabungan dan tab marketplace.
7. Klik **Download Excel Hasil PO**.
8. Gunakan sheet Daily Order untuk menyalin angka ke Google Sheets.

## Catatan penting sebelum dipakai operasional

- Master warehouse di `BRAND_CONFIG` pada `app.py` harus disesuaikan dengan header Daily Order terbaru. Nama dan urutan yang dimasukkan mengikuti screenshot yang tersedia. Beberapa teks pada screenshot beresolusi kecil, sehingga cocokkan lagi dengan Google Sheets master sebelum dipakai untuk pelaporan resmi. Brand yang belum memiliki screenshot/template master (misalnya Hanasui, NCO, Fyne, Ultimate U) belum dimasukkan.
- Jika nama toko/brand di file sumber tidak mengandung alias yang terdaftar, tambahkan alias pada `BRAND_CONFIG`.
- Jika status baru muncul, status tersebut akan dihitung selama tidak mengandung kata yang masuk daftar pengecualian. Periksa tab Audit sebelum memakai hasil.
- Untuk Desty, nomor pesanan marketplace digunakan sebagai kunci utama; nomor pesanan Desty menjadi cadangan jika nomor marketplace kosong.
- Untuk Jubelio, `No Pesanan` digunakan sebagai kunci PO.
- Secara default nomor yang sama di marketplace berbeda dihitung terpisah. Opsi deduplikasi lintas marketplace tersedia di sidebar.
- BigSeller belum diproses. Format export BigSeller perlu diperiksa dan ditambahkan sebagai modul tersendiri setelah file contoh BigSeller disediakan.
- Jangan mengunggah file transaksi yang berisi data pribadi ke repository GitHub publik. Upload hanya melalui halaman aplikasi Streamlit yang aksesnya dibatasi sesuai kebijakan perusahaan. Untuk penggunaan internal, pertimbangkan repository private dan pengaturan akses aplikasi.

## Menambah atau mengubah master warehouse

Cari `BRAND_CONFIG` di bagian awal `app.py`.

Contoh:

```python
"Yummys": {
    "aliases": ["yummys", "yummy"],
    "sources": ["Jubelio"],
    "warehouses": [
        "AARON-DEPOK",
        "AARON-GRESIK",
        "AARON-RIAU",
        "AARON-SURABAYA",
        "AARON-YOGYAKARTA",
        "Oxar-Jakarta Timur",
        "Oxar Central Warehouse",
        "OXAR-Makassar",
        "OXAR-Medan",
        "OXAR-Padang",
        "OXAR-Banjarmasin",
        "OXAR-Palembang",
        "OXAR-Bali",
    ],
}
```

Jangan mengubah nama kolom master jika ingin hasil sama persis dengan Google Sheets Daily Order.
