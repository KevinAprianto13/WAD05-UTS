import json
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from models import Barang, BarangCreate, BarangUpdate

app = FastAPI(
    title="Dashboard Inventaris API",
    description="API RESTful untuk UTS Web Application Development (Soal B - Inventaris Barang). "
                "Menyediakan fitur CRUD in-memory dengan data seed awal.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Konfigurasi CORS agar frontend Vue lokal dapat mengakses API tanpa batasan
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Penyimpanan data in-memory (list Python)
barang_db: List[dict] = []

def seed_database():
    """Memuat data awal dari file JSON saat server pertama kali dijalankan."""
    global barang_db
    json_path = Path(__file__).parent / "seed_barang.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            barang_db = json.load(f)
        print(f"[SEED] Berhasil memuat {len(barang_db)} data barang dari {json_path.name}")
    else:
        print(f"[WARN] File seed {json_path.name} tidak ditemukan. Database in-memory kosong.")

# Jalankan seeding saat aplikasi startup
@app.on_event("startup")
def on_startup():
    seed_database()

@app.get(
    "/api/barang",
    response_model=List[Barang],
    summary="Ambil Semua Barang",
    description="Mengembalikan seluruh daftar barang inventaris yang tersimpan di memori.",
    tags=["Inventaris"]
)
def get_all_barang():
    return barang_db

@app.get(
    "/api/barang/{barang_id}",
    response_model=Barang,
    summary="Ambil Detail Barang",
    description="Mengambil satu item barang berdasarkan ID yang diberikan.",
    tags=["Inventaris"]
)
def get_barang_by_id(barang_id: int):
    for item in barang_db:
        if item["id"] == barang_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Barang dengan ID {barang_id} tidak ditemukan")

@app.post(
    "/api/barang",
    response_model=Barang,
    status_code=status.HTTP_201_CREATED,
    summary="Tambah Barang Baru",
    description="Menambahkan data barang inventaris baru dengan validasi skema Pydantic.",
    tags=["Inventaris"]
)
def create_barang(payload: BarangCreate):
    # Buat ID unik baru secara otomatis (ID maksimum + 1 atau 1 jika kosong)
    new_id = (max([b["id"] for b in barang_db]) + 1) if barang_db else 1
    new_barang = {
        "id": new_id,
        "nama": payload.nama.strip(),
        "kategori": payload.kategori.strip(),
        "jumlah_stok": payload.jumlah_stok,
        "lokasi_gudang": payload.lokasi_gudang.strip(),
    }
    barang_db.append(new_barang)
    return new_barang

@app.put(
    "/api/barang/{barang_id}",
    response_model=Barang,
    summary="Update Data Barang (Fitur Bonus)",
    description="Memperbarui data atribut atau jumlah stok barang inventaris berdasarkan ID.",
    tags=["Inventaris"]
)
def update_barang(barang_id: int, payload: BarangUpdate):
    for idx, item in enumerate(barang_db):
        if item["id"] == barang_id:
            updated_data = item.copy()
            if payload.nama is not None:
                updated_data["nama"] = payload.nama.strip()
            if payload.kategori is not None:
                updated_data["kategori"] = payload.kategori.strip()
            if payload.jumlah_stok is not None:
                updated_data["jumlah_stok"] = payload.jumlah_stok
            if payload.lokasi_gudang is not None:
                updated_data["lokasi_gudang"] = payload.lokasi_gudang.strip()
            
            barang_db[idx] = updated_data
            return updated_data
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Barang dengan ID {barang_id} tidak ditemukan")

@app.delete(
    "/api/barang/{barang_id}",
    status_code=status.HTTP_200_OK,
    summary="Hapus Barang",
    description="Menghapus satu data barang dari inventaris berdasarkan ID.",
    tags=["Inventaris"]
)
def delete_barang(barang_id: int):
    for idx, item in enumerate(barang_db):
        if item["id"] == barang_id:
            removed = barang_db.pop(idx)
            return {"status": "success", "message": f"Barang '{removed['nama']}' berhasil dihapus", "id": barang_id}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Barang dengan ID {barang_id} tidak ditemukan")
