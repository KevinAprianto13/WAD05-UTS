<script setup>
import { ref, computed, onMounted } from 'vue'

// ============================================================================
// KONFIGURASI API & STATE UTAMA
// ============================================================================
const API_BASE_URL = 'http://localhost:8000'

// 3.1: Data dari backend disimpan sebagai ref
const barangList = ref([])

// Status Pengambilan Data (Loading, Error, Berhasil)
const isLoading = ref(true)
const errorMessage = ref('')

// State Kontrol Filter & Urutan
const searchQuery = ref('')
const sortOrder = ref('asc') // 'asc' = A-Z, 'desc' = Z-A

// State Toast Notifikasi
const toast = ref({
  show: false,
  message: '',
  type: 'success' // 'success' | 'error'
})

let toastTimeout = null
const showToast = (message, type = 'success') => {
  if (toastTimeout) clearTimeout(toastTimeout)
  toast.value = { show: true, message, type }
  toastTimeout = setTimeout(() => {
    toast.value.show = false
  }, 3500)
}

// State Modal Tambah Barang
const isAddModalOpen = ref(false)
const isSubmittingAdd = ref(false)
const addForm = ref({
  nama: '',
  kategori: '',
  jumlah_stok: 0,
  lokasi_gudang: ''
})

// State Modal Edit Barang (Fitur Bonus)
const isEditModalOpen = ref(false)
const isSubmittingEdit = ref(false)
const editForm = ref({
  id: null,
  nama: '',
  kategori: '',
  jumlah_stok: 0,
  lokasi_gudang: ''
})

// Kategori umum yang disarankan
const suggestedCategories = [
  'Elektronik & IT',
  'Kabel & Aksesoris',
  'Jaringan & Server',
  'Alat Tulis Kantor',
  'Peralatan Cetak',
  'Perabot & Furniture',
  'Logistik & Packaging',
  'Peralatan Gudang',
  'Keselamatan & K3'
]

// ============================================================================
// 3.3 & 3.2: FETCH API DENGAN ASYNC/AWAIT & TRY/CATCH
// ============================================================================

// Mengambil seluruh data barang dari backend
const fetchBarangList = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await fetch(`${API_BASE_URL}/api/barang`)
    if (!response.ok) {
      throw new Error(`Gagal mengambil data inventaris (HTTP ${response.status})`)
    }
    const data = await response.json()
    barangList.value = data
  } catch (err) {
    console.error('Error saat fetch barang:', err)
    errorMessage.value = err.message || 'Tidak dapat terhubung ke server backend'
  } finally {
    isLoading.value = false
  }
}

// Menambahkan data barang baru (POST)
const handleCreateBarang = async () => {
  if (!addForm.value.nama.trim() || !addForm.value.kategori.trim() || !addForm.value.lokasi_gudang.trim()) {
    showToast('Semua field wajib diisi!', 'error')
    return
  }

  isSubmittingAdd.value = true
  try {
    const payload = {
      nama: addForm.value.nama.trim(),
      kategori: addForm.value.kategori.trim(),
      jumlah_stok: Number(addForm.value.jumlah_stok),
      lokasi_gudang: addForm.value.lokasi_gudang.trim()
    }

    const response = await fetch(`${API_BASE_URL}/api/barang`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menambahkan barang')
    }

    const createdItem = await response.json()
    // Refresh daftar dari backend
    await fetchBarangList()
    showToast(`Barang "${createdItem.nama}" berhasil ditambahkan!`, 'success')
    closeAddModal()
  } catch (err) {
    showToast(err.message || 'Gagal menambahkan barang ke backend', 'error')
  } finally {
    isSubmittingAdd.value = false
  }
}

// Menghapus data barang (DELETE)
const handleDeleteBarang = async (id, nama) => {
  const confirmDelete = window.confirm(`Apakah Anda yakin ingin menghapus barang "${nama}"?`)
  if (!confirmDelete) return

  try {
    const response = await fetch(`${API_BASE_URL}/api/barang/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal menghapus barang')
    }

    // Refresh daftar dari backend
    await fetchBarangList()
    showToast(`Barang "${nama}" berhasil dihapus`, 'success')
  } catch (err) {
    showToast(err.message || 'Gagal menghapus barang dari backend', 'error')
  }
}

// Mengubah data barang (PUT - Fitur Bonus)
const handleUpdateBarang = async () => {
  if (!editForm.value.nama.trim() || !editForm.value.kategori.trim() || !editForm.value.lokasi_gudang.trim()) {
    showToast('Semua field wajib diisi!', 'error')
    return
  }

  isSubmittingEdit.value = true
  try {
    const payload = {
      nama: editForm.value.nama.trim(),
      kategori: editForm.value.kategori.trim(),
      jumlah_stok: Number(editForm.value.jumlah_stok),
      lokasi_gudang: editForm.value.lokasi_gudang.trim()
    }

    const response = await fetch(`${API_BASE_URL}/api/barang/${editForm.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}))
      throw new Error(errData.detail || 'Gagal mengupdate barang')
    }

    await fetchBarangList()
    showToast(`Barang "${editForm.value.nama}" berhasil diperbarui!`, 'success')
    closeEditModal()
  } catch (err) {
    showToast(err.message || 'Gagal mengupdate data barang', 'error')
  } finally {
    isSubmittingEdit.value = false
  }
}

// Helper Modal
const openAddModal = () => {
  addForm.value = {
    nama: '',
    kategori: suggestedCategories[0],
    jumlah_stok: 1,
    lokasi_gudang: 'Gudang A - Rak 01'
  }
  isAddModalOpen.value = true
}

const closeAddModal = () => {
  isAddModalOpen.value = false
}

const openEditModal = (item) => {
  editForm.value = {
    id: item.id,
    nama: item.nama,
    kategori: item.kategori,
    jumlah_stok: item.jumlah_stok,
    lokasi_gudang: item.lokasi_gudang
  }
  isEditModalOpen.value = true
}

const closeEditModal = () => {
  isEditModalOpen.value = false
}

// ============================================================================
// 3.1 & 3.2: TRANSFORMASI DATA & COMPUTED DENGAN NATIVE ARRAY METHODS
// ============================================================================

// 1. Pencarian menggunakan .filter() native berdasarkan nama atau kategori
const filteredBarang = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    return barangList.value
  }
  return barangList.value.filter((item) => {
    const matchNama = item.nama && item.nama.toLowerCase().includes(query)
    const matchKategori = item.kategori && item.kategori.toLowerCase().includes(query)
    return matchNama || matchKategori
  })
})

// 2. Pengurutan A-Z / Z-A menggunakan computed berantai di atas hasil filter
const sortedAndFilteredBarang = computed(() => {
  const list = [...filteredBarang.value]
  return list.sort((a, b) => {
    const namaA = a.nama.toLowerCase()
    const namaB = b.nama.toLowerCase()
    if (sortOrder.value === 'asc') {
      return namaA.localeCompare(namaB)
    } else {
      return namaB.localeCompare(namaA)
    }
  })
})

// 3. Ambang batas & Status Stok:
//    - Habis: stok === 0
//    - Menipis: stok > 0 && stok <= 10
//    - Aman: stok > 10
const getStockStatus = (stok) => {
  const val = Number(stok)
  if (val === 0) {
    return {
      label: 'Habis',
      className: 'status-habis'
    }
  } else if (val <= 10) {
    return {
      label: 'Menipis',
      className: 'status-menipis'
    }
  } else {
    return {
      label: 'Aman',
      className: 'status-aman'
    }
  }
}

// 4 Tile Statistik Ringkasan (Dihitung MURNI dengan computed dari data barang yang sama)
// Tile 1: Total Barang (jumlah semua barang)
const totalBarang = computed(() => {
  return barangList.value.length
})

// Tile 2: Stok Menipis + Habis (jumlah barang dengan status itu, memakai native .filter())
const totalMenipisDanHabis = computed(() => {
  return barangList.value.filter((item) => Number(item.jumlah_stok) <= 10).length
})

// Tile 3: Jumlah Kategori (kategori unik, memakai native .map() dan Set)
const totalKategori = computed(() => {
  const kategoriArray = barangList.value.map((item) => item.kategori)
  const uniqueKategori = new Set(kategoriArray)
  return uniqueKategori.size
})

// Tile 4: Total Unit (jumlah seluruh angka stok dijumlahkan, memakai native .reduce())
const totalUnitStok = computed(() => {
  return barangList.value.reduce((accum, item) => accum + Number(item.jumlah_stok || 0), 0)
})

// Visualisasi Bonus: Ringkasan Stok per Kategori (CSS Bar Chart dihitung dari computed)
const categoryStockDistribution = computed(() => {
  if (barangList.value.length === 0) return []
  
  const categoryMap = {}
  barangList.value.forEach((item) => {
    const kat = item.kategori || 'Lain-lain'
    categoryMap[kat] = (categoryMap[kat] || 0) + Number(item.jumlah_stok)
  })

  const total = totalUnitStok.value || 1
  return Object.entries(categoryMap)
    .map(([kategori, totalStok]) => ({
      kategori,
      totalStok,
      percentage: Math.min(100, Math.round((totalStok / total) * 100))
    }))
    .sort((a, b) => b.totalStok - a.totalStok)
})

// Lifecycle: Ambil data saat komponen dipasang
onMounted(() => {
  fetchBarangList()
})
</script>

<template>
  <div class="app-wrapper">
    <!-- Top Navigation Header -->
    <header class="app-header">
      <div class="header-container">
        <div class="brand-wrapper">
          <div class="brand-logo">
            <svg viewBox="0 0 24 24">
              <path d="M4 4h7v7H4V4zm9 0h7v7h-7V4zm-9 9h7v7H4v-7zm9 0h7v7h-7v-7z"/>
            </svg>
          </div>
          <div>
            <h1 class="brand-title">InventaHub</h1>
            <p class="brand-subtitle">Dashboard Inventaris Gudang • UTS Web Application Development</p>
          </div>
        </div>
        <div class="user-badge">
          <span>Soal B (Genap)</span>
          <span class="nim-tag">NIM: 25120300004</span>
        </div>
      </div>
    </header>

    <!-- Main Content Container -->
    <main class="main-content">
      <!-- Ambang Batas Info Box -->
      <div class="threshold-info">
        <span><strong>Kriteria Ambang Batas Stok:</strong></span>
        <div class="threshold-tags">
          <span class="badge-status status-aman"><span class="badge-dot"></span>Aman: &gt; 10 Unit</span>
          <span class="badge-status status-menipis"><span class="badge-dot"></span>Menipis: 1 - 10 Unit</span>
          <span class="badge-status status-habis"><span class="badge-dot"></span>Habis: 0 Unit</span>
        </div>
      </div>

      <!-- 4 Tile Ringkasan Statistik (Dihitung dari computed murni) -->
      <section class="stats-grid" id="summary-tiles" aria-label="Ringkasan Statistik Inventaris">
        <!-- Tile 1: Total Barang -->
        <div class="stat-card" id="stat-total-barang">
          <div class="stat-info">
            <span class="stat-label">Total Barang</span>
            <span class="stat-value">{{ totalBarang }}</span>
          </div>
          <div class="stat-icon primary">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
          </div>
        </div>

        <!-- Tile 2: Stok Menipis + Habis -->
        <div class="stat-card" id="stat-menipis-habis">
          <div class="stat-info">
            <span class="stat-label">Menipis + Habis</span>
            <span class="stat-value">{{ totalMenipisDanHabis }}</span>
          </div>
          <div class="stat-icon warning">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
              <line x1="12" y1="9" x2="12" y2="13"></line>
              <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
          </div>
        </div>

        <!-- Tile 3: Jumlah Kategori -->
        <div class="stat-card" id="stat-jumlah-kategori">
          <div class="stat-info">
            <span class="stat-label">Jumlah Kategori</span>
            <span class="stat-value">{{ totalKategori }}</span>
          </div>
          <div class="stat-icon info">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
          </div>
        </div>

        <!-- Tile 4: Total Unit -->
        <div class="stat-card" id="stat-total-unit">
          <div class="stat-info">
            <span class="stat-label">Total Unit Fisik</span>
            <span class="stat-value">{{ totalUnitStok.toLocaleString('id-ID') }}</span>
          </div>
          <div class="stat-icon success">
            <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
          </div>
        </div>
      </section>

      <!-- Fitur Bonus: Visualisasi Bar Ringkasan Stok per Kategori -->
      <section v-if="!isLoading && !errorMessage && categoryStockDistribution.length > 0" class="category-summary-card">
        <div class="card-header-flex">
          <h2 class="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
            Distribusi Stok Berdasarkan Kategori
          </h2>
          <span class="section-badge">Fitur Bonus • Bar CSS Native</span>
        </div>
        <div class="category-bars-grid">
          <div v-for="cat in categoryStockDistribution" :key="cat.kategori" class="category-bar-item">
            <div class="bar-labels">
              <span class="bar-name">{{ cat.kategori }}</span>
              <span class="bar-count">{{ cat.totalStok }} unit ({{ cat.percentage }}%)</span>
            </div>
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: cat.percentage + '%' }"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Toolbar Interaktif: Pencarian, Pengurutan A-Z/Z-A, dan Tambah Data -->
      <section class="toolbar-card" aria-label="Toolbar Pengendali">
        <div class="search-input-wrapper">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input
            id="search-input"
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="Cari berdasarkan nama atau kategori barang..."
            autocomplete="off"
          />
        </div>

        <div class="toolbar-actions">
          <!-- Tombol Urutkan A-Z -->
          <button
            id="btn-sort-asc"
            :class="['btn', 'btn-outline', { 'btn-active': sortOrder === 'asc' }]"
            @click="sortOrder = 'asc'"
            title="Urutkan Nama A ke Z"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M3 12h12M3 18h6"/>
            </svg>
            Urutkan A-Z
          </button>

          <!-- Tombol Urutkan Z-A -->
          <button
            id="btn-sort-desc"
            :class="['btn', 'btn-outline', { 'btn-active': sortOrder === 'desc' }]"
            @click="sortOrder = 'desc'"
            title="Urutkan Nama Z ke A"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 18h18M3 12h12M3 6h6"/>
            </svg>
            Urutkan Z-A
          </button>

          <!-- Tombol Tambah Barang Baru -->
          <button id="btn-tambah-barang" class="btn btn-primary" @click="openAddModal">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Tambah Barang
          </button>
        </div>
      </section>

      <!-- Status Pengambilan Data: 1. Loading -->
      <div v-if="isLoading" class="table-card state-box" id="state-loading">
        <div class="spinner"></div>
        <h3 class="state-title">Memuat Data Inventaris...</h3>
        <p class="state-desc">Menghubungkan ke backend FastAPI dan mengambil data barang.</p>
      </div>

      <!-- Status Pengambilan Data: 2. Error -->
      <div v-else-if="errorMessage" class="table-card state-box" id="state-error">
        <svg class="state-icon-large error" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <h3 class="state-title">Gagal Mengambil Data</h3>
        <p class="state-desc">{{ errorMessage }}</p>
        <button id="btn-retry" class="btn btn-primary" @click="fetchBarangList">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
          </svg>
          Coba Lagi
        </button>
      </div>

      <!-- Status Pengambilan Data: 3. Kosong (Hasil pencarian tidak ada atau data kosong) -->
      <div v-else-if="sortedAndFilteredBarang.length === 0" class="table-card state-box" id="state-empty">
        <svg class="state-icon-large" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
        <h3 class="state-title">Data Tidak Ditemukan</h3>
        <p class="state-desc">
          Tidak ada barang inventaris yang sesuai dengan kata kunci "<strong>{{ searchQuery }}</strong>".
        </p>
        <button v-if="searchQuery" class="btn btn-outline" @click="searchQuery = ''">
          Reset Pencarian
        </button>
      </div>

      <!-- Status Pengambilan Data: 4. Berhasil (Tabel Daftar Barang) -->
      <div v-else class="table-card" id="state-success">
        <div class="table-responsive">
          <table class="data-table" id="table-barang">
            <thead>
              <tr>
                <th style="width: 70px;">ID</th>
                <th>Nama Barang</th>
                <th>Kategori</th>
                <th style="width: 130px;">Jumlah Stok</th>
                <th>Status Stok</th>
                <th>Lokasi Gudang</th>
                <th style="width: 140px; text-align: center;">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in sortedAndFilteredBarang" :key="item.id" :id="'row-barang-' + item.id">
                <td class="col-id">#{{ item.id }}</td>
                <td>
                  <span class="item-name">{{ item.nama }}</span>
                </td>
                <td>
                  <span class="item-category-tag">{{ item.kategori }}</span>
                </td>
                <td>
                  <span class="stock-value">{{ item.jumlah_stok }}</span>
                  <small style="color: var(--text-muted); margin-left: 4px;">unit</small>
                </td>
                <td>
                  <!-- 3.1: Badge status stok dengan conditional class binding -->
                  <span :class="['badge-status', getStockStatus(item.jumlah_stok).className]">
                    <span class="badge-dot"></span>
                    {{ getStockStatus(item.jumlah_stok).label }}
                  </span>
                </td>
                <td>
                  <span class="location-tag">
                    <svg viewBox="0 0 24 24" fill="none" stroke-width="2">
                      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                      <circle cx="12" cy="10" r="3"></circle>
                    </svg>
                    {{ item.lokasi_gudang }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons" style="justify-content: center;">
                    <!-- Tombol Edit (Fitur Bonus) -->
                    <button
                      class="btn btn-outline btn-sm"
                      @click="openEditModal(item)"
                      :id="'btn-edit-' + item.id"
                      title="Edit Data Barang"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                      Edit
                    </button>

                    <!-- Tombol Hapus (DELETE ke backend) -->
                    <button
                      class="btn btn-danger-outline btn-sm"
                      @click="handleDeleteBarang(item.id, item.nama)"
                      :id="'btn-delete-' + item.id"
                      title="Hapus Data Barang"
                    >
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      </svg>
                      Hapus
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>

    <!-- Modal Form Tambah Data Baru -->
    <div v-if="isAddModalOpen" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-add-title">
        <div class="modal-header">
          <h3 id="modal-add-title" class="modal-title">Tambah Barang Inventaris Baru</h3>
          <button class="modal-close-btn" @click="closeAddModal" aria-label="Tutup modal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="handleCreateBarang">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="add-nama">Nama Barang <span class="required">*</span></label>
              <input
                id="add-nama"
                v-model="addForm.nama"
                type="text"
                class="form-control"
                placeholder="Contoh: Rak Server 42U Rackmount"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="add-kategori">Kategori <span class="required">*</span></label>
              <select id="add-kategori" v-model="addForm.kategori" class="form-control" required>
                <option v-for="cat in suggestedCategories" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="add-stok">Jumlah Stok Fisik <span class="required">*</span></label>
              <input
                id="add-stok"
                v-model.number="addForm.jumlah_stok"
                type="number"
                min="0"
                class="form-control"
                placeholder="0"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="add-lokasi">Lokasi Gudang <span class="required">*</span></label>
              <input
                id="add-lokasi"
                v-model="addForm.lokasi_gudang"
                type="text"
                class="form-control"
                placeholder="Contoh: Gudang B - Blok C4"
                required
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="closeAddModal" :disabled="isSubmittingAdd">
              Batal
            </button>
            <button id="btn-submit-tambah" type="submit" class="btn btn-primary" :disabled="isSubmittingAdd">
              {{ isSubmittingAdd ? 'Menyimpan...' : 'Simpan Barang' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Form Edit Barang (Fitur Bonus) -->
    <div v-if="isEditModalOpen" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-edit-title">
        <div class="modal-header">
          <h3 id="modal-edit-title" class="modal-title">Edit Data Barang #{{ editForm.id }}</h3>
          <button class="modal-close-btn" @click="closeEditModal" aria-label="Tutup modal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <form @submit.prevent="handleUpdateBarang">
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label" for="edit-nama">Nama Barang <span class="required">*</span></label>
              <input
                id="edit-nama"
                v-model="editForm.nama"
                type="text"
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-kategori">Kategori <span class="required">*</span></label>
              <select id="edit-kategori" v-model="editForm.kategori" class="form-control" required>
                <option v-for="cat in suggestedCategories" :key="cat" :value="cat">
                  {{ cat }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-stok">Jumlah Stok Fisik <span class="required">*</span></label>
              <input
                id="edit-stok"
                v-model.number="editForm.jumlah_stok"
                type="number"
                min="0"
                class="form-control"
                required
              />
            </div>

            <div class="form-group">
              <label class="form-label" for="edit-lokasi">Lokasi Gudang <span class="required">*</span></label>
              <input
                id="edit-lokasi"
                v-model="editForm.lokasi_gudang"
                type="text"
                class="form-control"
                required
              />
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-outline" @click="closeEditModal" :disabled="isSubmittingEdit">
              Batal
            </button>
            <button id="btn-submit-edit" type="submit" class="btn btn-primary" :disabled="isSubmittingEdit">
              {{ isSubmittingEdit ? 'Memperbarui...' : 'Simpan Perubahan' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Toast Notification Floating -->
    <div v-if="toast.show" class="toast-container">
      <div :class="['toast', toast.type]">
        <svg v-if="toast.type === 'success'" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span>{{ toast.message }}</span>
      </div>
    </div>

    <!-- Footer -->
    <footer class="app-footer">
      <p>InventaHub Mini Dashboard Full-Stack • UTS Web Application Development 2026 • NIM: 25120300004</p>
    </footer>
  </div>
</template>
