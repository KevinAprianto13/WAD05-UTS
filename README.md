# InventaHub — Mini Dashboard Inventaris Gudang
**Ujian Tengah Semester (UTS) — Web Application Development**

---

### Identitas Mahasiswa
- **Nama**: Kevin Aprianto
- **NIM**: 25120300004
- **Digit Terakhir**: 4 (GENAP)
- **Soal UTS**: Soal B — Dashboard Inventaris
- **Entitas**: `Barang` (`id`, `nama`, `kategori`, `jumlah_stok`, `lokasi_gudang`)

---

## 1. Deskripsi Proyek
**InventaHub** adalah aplikasi mini dashboard *full-stack* modern yang dibangun untuk mengelola data inventaris barang gudang secara *real-time*. Proyek ini memadukan **FastAPI** di sisi *backend* dan **Vue 3 (Composition API)** di sisi *frontend* dengan standar arsitektur *client-server*, validasi skema Pydantic, operasi RESTful, serta tampilan antarmuka responsif berbasis tema gelap modern (*dark glassmorphism*).

---

## 2. Penjelasan Ambang Batas (*Threshold*) Status Stok
Sesuai dengan ketentuan Soal B, ambang batas status stok ditentukan berdasarkan skenario operasional pergudangan logistik nyata:

| Status Stok | Ambang Batas (*Threshold*) | Indikator Visual | Penjelasan Operasional |
| :--- | :--- | :--- | :--- |
| **Aman** | `jumlah_stok > 10` | Badge Hijau (`status-aman`) | Stok fisik di gudang mencukupi untuk memenuhi kebutuhan pengiriman operasional harian tanpa perlu *restock* darurat. |
| **Menipis** | `1 <= jumlah_stok <= 10` | Badge Kuning (`status-menipis`) | Jumlah stok telah mendekati *reorder point* (titik pemesanan ulang). Manajer gudang harus segera membuat *Purchase Order* pengadaan baru. |
| **Habis** | `jumlah_stok == 0` | Badge Merah (`status-habis`) | Barang tidak lagi memiliki sisa unit fisik di gudang (*out of stock*). Pengiriman untuk barang ini ditangguhkan sampai pasokan tiba. |

---

## 3. Fitur Utama & Kepatuhan Spesifikasi Teknis

### A. Frontend — Vue 3 (Composition API)
1. **Penyimpanan State Backend**: Data barang dari API disimpan ke dalam state reaktif menggunakan `ref(barangList)`.
2. **Pencarian Reaktif**: Menggunakan `computed(filteredBarang)` dengan method *native* `Array.prototype.filter()` untuk mencocokkan kata kunci pada field `nama` atau `kategori`.
3. **Pengurutan Berantai**: Tombol urutkan A-Z / Z-A menggunakan `computed(sortedAndFilteredBarang)` berantai di atas hasil filter pencarian dengan method *native* `Array.prototype.sort()`.
4. **Conditional Class Binding**: Badge status stok berganti warna dan kelas secara otomatis (`status-aman`, `status-menipis`, `status-habis`) berdasarkan nilai numerik stok yang diterima dari server.
5. **Form Tambah Data Baru**: Menggunakan state lokal (`ref(addForm)`), mengirimkan `POST` via Fetch API, merespons sukses dengan *toast notification*, dan me-*refresh* data tabel secara instan.
6. **Hapus Data**: Memanggil endpoint `DELETE /api/barang/{id}` dengan konfirmasi keamanan, lalu memperbarui tampilan secara reaktif.
7. **4 Tile Statistik Ringkasan (Computed Murni)**:
   - **Total Barang**: Dihitung dari `barangList.value.length`.
   - **Stok Menipis + Habis**: Dihitung memakai `barangList.value.filter(b => b.jumlah_stok <= 10).length`.
   - **Jumlah Kategori**: Menghitung kategori unik memakai `new Set(barangList.value.map(b => b.kategori)).size`.
   - **Total Unit**: Menghitung total seluruh stok fisik memakai `barangList.value.reduce((acc, b) => acc + Number(b.jumlah_stok), 0)`.
8. **Pengambilan Data Asinkron & Penanganan Status UI**:
   - Seluruh pemanggilan HTTP menggunakan `fetch` bawaan browser dengan pola `async/await` dan `try/catch`.
   - Menampilkan status transparan di UI:
     - **Loading**: Animasi spinner saat request sedang berlangsung.
     - **Error**: Pesan kegagalan koneksi backend disertai tombol *Coba Lagi* (*retry*).
     - **Kosong**: Menampilkan ilustrasi pencarian nihil bila filter tidak menemukan data.
     - **Berhasil**: Menampilkan tabel data yang interaktif.

### B. Fitur Bonus (Nilai Tambah)
- **Edit Data Barang (PUT)**: Disediakan endpoint `PUT /api/barang/{id}` dan modal interaktif di frontend untuk memperbarui nama, kategori, jumlah stok, maupun lokasi gudang.
- **Visualisasi Distribusi Stok per Kategori**: Progress bar berbasis CSS murni tanpa library chart eksternal. Lebar bar dihitung secara proporsional via `computed` terhadap total stok.
- **Dokumentasi OpenAPI Bersih**: Tersedia di `/docs` dengan tag, ringkasan, dan skema request/response terperinci.

### C. Responsivitas Layar (3 Breakpoint)
- **Desktop (>= 1024px)**: Grid 4 kolom untuk ringkasan statistik, tabel lengkap dengan aksi.
- **Tablet (768px - 1023px)**: Grid 2 kolom untuk ringkasan statistik, toolbar fleksibel.
- **Mobile (< 768px & 375px)**: Tata letak bertumpuk (*single column*), scroll horizontal pada tabel yang mulus tanpa merusak margin layar atau menimbulkan scroll horizontal yang tidak disengaja.

---

## 4. Struktur Proyek
```text
WAD05/
├── backend/
│   ├── main.py              # Server FastAPI, routing, CORS, CRUD in-memory
│   ├── models.py            # Validasi skema Pydantic (BarangBase, BarangCreate, BarangUpdate, Barang)
│   ├── seed_barang.json     # Data seed awal inventaris (22 item unik buatan sendiri)
│   └── requirements.txt     # Dependensi backend (fastapi, uvicorn, pydantic)
├── frontend/
│   ├── src/
│   │   ├── App.vue          # Komponen utama Vue 3 Composition API
│   │   ├── main.js          # Entrypoint frontend
│   │   └── style.css        # Sistem desain CSS kustom, glassmorphism & responsive media queries
│   ├── index.html           # HTML5 template dengan Google Font Plus Jakarta Sans
│   ├── package.json         # Dependensi frontend Vue 3 & Vite
│   └── vite.config.js       # Konfigurasi Vite dev server
├── .gitignore               # Konfigurasi pengabaian file build & venv
├── README.md                # Panduan instalasi dan dokumentasi teknis
└── WAD05-UTS-WebApplicationDevelopment.pdf # Soal acuan UTS
```

---

## 5. Cara Menjalankan Aplikasi

### Persyaratan Awal
- **Python** (versi 3.10 ke atas)
- **Node.js** (versi 18 ke atas) & **npm**

---

### Langkah 1: Menjalankan Backend (FastAPI)
Buka terminal baru di folder proyek `WAD05`:

1. Masuk ke direktori `backend`:
   ```bash
   cd backend
   ```

2. Buat dan aktifkan *virtual environment* (opsional tapi sangat disarankan):
   - **Windows**:
     ```powershell
     py -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instal dependensi backend:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan server FastAPI:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

Backend akan berjalan pada:
- **API Base URL**: `http://localhost:8000`
- **Dokumentasi Interaktif Swagger UI**: `http://localhost:8000/docs`
- **Dokumentasi ReDoc**: `http://localhost:8000/redoc`

---

### Langkah 2: Menjalankan Frontend (Vue 3 + Vite)
Buka terminal kedua di folder proyek `WAD05`:

1. Masuk ke direktori `frontend`:
   ```bash
   cd frontend
   ```

2. Instal dependensi npm:
   ```bash
   npm install
   ```

3. Jalankan server pengembangan Vite:
   ```bash
   npm run dev
   ```

4. Buka peramban (*browser*) pada alamat yang tertera (biasanya `http://localhost:5173`).

---

## 6. Daftar Endpoint REST API (FastAPI)

| Method | Endpoint | Deskripsi | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/barang` | Mengambil seluruh data barang inventaris | `200 OK` |
| `GET` | `/api/barang/{id}` | Mengambil data satu barang berdasarkan ID | `200 OK` / `404 Not Found` |
| `POST` | `/api/barang` | Menambahkan barang baru (validasi Pydantic) | `201 Created` / `422 Unprocessable Entity` |
| `PUT` | `/api/barang/{id}` | Mengubah data barang / update stok (*Fitur Bonus*) | `200 OK` / `404 Not Found` |
| `DELETE` | `/api/barang/{id}` | Menghapus barang dari memori server | `200 OK` / `404 Not Found` |

---

## 7. Data Seed Awal
Data awal terdiri dari **22 entitas barang** yang bervariasi dari segi kategori, kuantitas stok (mencakup status Aman, Menipis, dan Habis), serta lokasi penempatan gudang untuk menguji seluruh aspek visualisasi dan filter data. Data tersimpan di file `backend/seed_barang.json` dan dimuat otomatis ke memori saat server FastAPI pertama kali dijalankan.
