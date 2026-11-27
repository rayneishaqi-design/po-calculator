PO Calculator — Multi Brand & Marketplace
Aplikasi Streamlit untuk menghitung PO unik dari file ekspor Jubelio dan Desty, memetakan warehouse ke kolom Daily Order per brand, dan mengekspor satu file Excel berisi rekap gabungan, rekap per marketplace, serta audit pesanan.
Source DR per brand
Brand	Sumber	Status aplikasi
CAVE	Jubelio	Aktif
Yummys	Jubelio	Aktif
Bumi Tauhid	BigSeller (Objective dan marketplace)	Belum aktif; parser BigSeller menyusul
Safwan	BigSeller (Shopee)	Belum aktif; parser BigSeller menyusul
NDR	Jubelio	Aktif
Essens	Jubelio	Aktif
BMYT	Jubelio	Aktif
Jamu Jago	Desty	Aktif
Aquila	Jubelio	Aktif
Attaqwa	Belum dikonfirmasi	Belum aktif
Aqshor	Belum dikonfirmasi	Belum aktif
Aplikasi hanya menampilkan uploader sesuai sumber brand yang dipilih. Contoh: CAVE hanya menampilkan uploader Jubelio; Jamu Jago hanya menampilkan uploader Desty. Bumi Tauhid dan Safwan menampilkan keterangan BigSeller tetapi uploader dinonaktifkan sampai parser BigSeller dibuat dan diuji.
Jalankan lokal
```bash
pip install -r requirements.txt
streamlit run app.py
```
Deploy ke Streamlit Community Cloud
Buat repository GitHub.
Upload `app.py`, `requirements.txt`, dan `README.md` ke root repository.
Buka https://share.streamlit.io/ dan login dengan GitHub.
Buat aplikasi baru, pilih repository dan branch `main`.
Isi Main file path dengan `app.py`, lalu deploy.
Aturan perhitungan
Satu nomor pesanan dihitung satu PO meskipun memiliki beberapa baris produk.
Nomor pesanan yang sama di marketplace berbeda dihitung terpisah secara default; opsi deduplikasi lintas marketplace tersedia.
Status yang mengandung Cancel, Return/Retur, Unpaid, atau Belum Bayar dikeluarkan.
Tanggal mengikuti tanggal transaksi dari file sumber.
Warehouse dipetakan ke master Daily Order brand. Nama warehouse tanpa kata "Oxar" tetap dapat dicocokkan berdasarkan nama wilayah jika hasilnya tunggal; jika ambigu, perlu pemetaan manual.
BigSeller belum diproses pada versi ini.
Catatan
Periksa kembali pemetaan warehouse dan hasil audit sebelum angka dipakai sebagai laporan operasional. Jangan mengunggah file transaksi berisi data internal ke repository GitHub publik.
