from pydantic import BaseModel, Field
from typing import Optional

class BarangBase(BaseModel):
    nama: str = Field(..., min_length=1, max_length=100, description="Nama barang inventaris")
    kategori: str = Field(..., min_length=1, max_length=50, description="Kategori barang")
    jumlah_stok: int = Field(..., ge=0, description="Jumlah stok fisik barang (harus angka >= 0)")
    lokasi_gudang: str = Field(..., min_length=1, max_length=100, description="Lokasi penempatan barang di gudang")

class BarangCreate(BarangBase):
    pass

class BarangUpdate(BaseModel):
    nama: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama barang inventaris")
    kategori: Optional[str] = Field(None, min_length=1, max_length=50, description="Kategori barang")
    jumlah_stok: Optional[int] = Field(None, ge=0, description="Jumlah stok fisik barang (harus angka >= 0)")
    lokasi_gudang: Optional[str] = Field(None, min_length=1, max_length=100, description="Lokasi penempatan barang di gudang")

class Barang(BarangBase):
    id: int = Field(..., description="ID unik untuk setiap barang inventaris")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nama": "Monitor LED 24 Inchi UltraSharp",
                "kategori": "Elektronik & IT",
                "jumlah_stok": 18,
                "lokasi_gudang": "Gudang A - Rak 01"
            }
        }
