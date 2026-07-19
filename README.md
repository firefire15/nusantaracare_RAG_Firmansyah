# NusantaraCare RAG System (Firmansyah)

Sistem RAG (*Retrieval-Augmented Generation*) dirancang untuk mempermudah karyawan dalam mengakses dan memahami dokumen Standar Operasional Prosedur (SOP) internal secara instan, akurat, dan aman.

---

## 1. Problem & Success Criteria

### Tujuan Bisnis
Implementasi RAG pada sistem NusantaraCare ini ditujukan untuk mencapai beberapa objektif bisnis utama:
1. **Efisiensi Waktu Operasional:** Menghemat waktu karyawan dalam mencari dan memahami dokumen SOP yang panjang serta kompleks.
2. **Peningkatan Kualitas Layanan:** Menyediakan jawaban yang konsisten dan akurat terkait prosedur operasional perusahaan.
3. **Mitigasi Risiko:** Memastikan setiap tindakan operasional berjalan sesuai dengan kepatuhan hukum dan regulasi SOP yang berlaku.
4. **Efisiensi Biaya:** Mengurangi beban infrastruktur teknologi dengan metode pencarian berbasis pengetahuan tanpa perlu proses *fine-tuning* model yang mahal.

### Kriteria Sukses
Sistem dinyatakan sukses apabila memenuhi indikator berikut:
* Sistem dapat memberikan jawaban yang **100% berbasis pada konteks** dokumen yang disediakan.
* Sistem sepenuhnya **terhindar dari halusinasi** (tidak mengarang informasi di luar dokumen).
* Sistem wajib **menyertakan referensi/sitasi sumber** asal muasal jawaban tersebut dibentuk agar dapat diverifikasi keabsahannya oleh pengguna.

### Jenis Pertanyaan yang Ditargetkan
1. **Pertanyaan Sesuai SOP Aktif:** Pertanyaan seputar operasional sehari-hari yang jawabannya termaktub dalam dokumen resmi. Sistem diharapkan menjawab dengan presisi.
2. **Pertanyaan SOP Kedaluwarsa:** Pertanyaan yang mengarah pada aturan lama. Sistem harus cerdas memilah dan mengutamakan SOP yang masih berlaku serta mengabaikan yang tidak aktif.
3. **Pertanyaan Bermuatan Ancaman (*Prompt Injection*):** Upaya manipulasi instruksi LLM oleh pengguna. Sistem harus mampu mendeteksi dan menyaringnya sejak awal.

### Batasan Sistem
* Pengetahuan sistem **terbatas hanya pada dokumen SOP** yang dimasukkan ke dalam basis data.
* Kualitas, gaya bahasa, dan ketepatan informasi sangat bergantung pada dokumen asli (*Garbage In, Garbage Out*).
* Sistem tidak memverifikasi keabsahan hukum atau validitas isi dokumen secara otomatis. Tanggung jawab kebenaran konten berada penuh pada otoritas penerbit dokumen.

---

## 2. Knowledge Base Understanding

### Isi dan Struktur Dokumen
Dokumen utama yang digunakan adalah `nusantaracare_panduan_operasional_internal_v2.md`. Dokumen ini tersusun secara terstruktur rapi menggunakan tiga tingkatan header (Header 1, Header 2, dan Header 3). Struktur hirarkis ini dimanfaatkan oleh sistem untuk melacak secara presisi asal-usul bagian dan sub-bagian informasi yang diambil.

### Metadata yang Digunakan
Setiap informasi yang diekstrak akan dilengkapi dengan elemen metadata berikut:
* `doc_id`: Nilai unik pengenal dokumen utama.
* `chunk_id`: Nilai unik pengenal setiap potongan teks (*chunk*).
* `doc_title`: Judul resmi dari dokumen SOP.
* `section_title`: Judul bab utama (Header 2) dari dokumen SOP.
* `section_subtitle`: Judul sub-bab (Header 3) dari dokumen SOP.
* `effective_date`: Tanggal mulai berlakunya dokumen SOP.
* `effective_until`: Tanggal berakhirnya masa berlaku dokumen SOP.
* `doc_version`: Versi dokumen yang sedang diakses.
* `is_active`: Status keaktifan dokumen (`True` / `False`).
* `created_at`: Stempel waktu pembuatan chunk ke dalam database ChromaDB.

### Perbedaan Versi Dokumen
Perbedaan versi aturan lama dan baru ditandai secara eksplisit pada bagian `section_subtitle` (Header 3). Jika di dalam judul sub-bab tersebut mengandung kata **"Nonaktif"**, maka secara otomatis sistem mengklasifikasikan bahwa aturan di dalam cakupan tersebut sudah tidak berlaku lagi.

---

## 3. RAG Design & Data Preparation

### Chunking Strategy
* **Chunk Size:** 400 karakter.
* **Chunk Overlap:** 50 karakter.
* **Rasionalisasi:** Konfigurasi ini dipilih agar potongan teks tetap efisien dalam proses pemadatan makna (vektor) namun tidak kehilangan keterkaitan informasi antar-kalimat berkat adanya irisan (overlap).

### Vector Database
Sistem menggunakan **ChromaDB** sebagai basis data vektor dengan alasan:
1. Integrasi yang sangat fleksibel dan *native* dengan bahasa pemrograman Python.
2. Ringan (*embedded*) sehingga meminimalkan biaya infrastruktur server.
3. Mendukung penyaringan data (*filtering*) berbasis metadata secara efisien sebelum pencarian semantik dilakukan.

---

## 4. Retrieval & Prompt Strategy

### Parameter Retrieval
* **Top-K:** `3` (Mengambil 3 potongan dokumen paling relevan).
* **Threshold (Distance):** `0.9` (Maksimum batas jarak vektor yang ditoleransi).
* **Tingkat Relevansi (Distance Filtering):**
  * `0.00` s.d. `0.33`: **High Relevance**
  * `0.33` s.d. `0.67`: **Medium Relevance**
  * `0.67` s.d. `0.90`: **Low Relevance**

### Proteksi Prompt Injection (Saringan Kata Kunci)
Untuk mengamankan instruksi LLM, kueri pengguna akan disaring terlebih dahulu dari kata/frasa mencurigakan berikut:
> *"abaikan perintah", "ignore previous", "lupakan aturan", "batalkan perintah", "kamu sekarang adalah", "jailbreak", "ignore", "forget", "forget the rule", "abaikan aturan"*

### Instruksi Prompt (System Prompt)

> *Anda adalah sistem yang berfungsi untuk membantu menjawab pertanyaan karyawan mengenai SOP yang berlaku.
Tugas Anda menjawab pertanyaan HANYA berdasarkan KONTEKS yang disediakan.*
> *Aturan yang bersifat mutlak:*
> *1. JAWAB HANYA dari teks yang ada di dalam KONTEKS.*
> *2. Jika jawabannya tidak ada di dalam konteks, Anda WAJIB menjawab: "Maaf, informasi tidak ditemukan dalam dokumen resmi."*
> *3. Jangan berasumsi sendiri, jangan menyimpulkan di luar konteks yang diberikan, dan jangan gunakan pengetahuan luar Anda.*
> *4. Jika konteks memuat informasi yang berbeda atau bertolak belakang, jelaskan perbedaannya.*

### 5. Kesimpulan
Secara keseluruhan, performa sistem RAG NusantaraCare ini menunjukkan hasil yang cukup baik dan presisi dalam merespons pertanyaan operasional seputar dokumen SOP.

Meskipun nilai parameter temperature pada LLM telah dikunci di angka 0.0 guna memastikan respon bersifat deterministik, proses pengawasan kualitas jawaban (output monitoring) secara berkala tetap direkomendasikan untuk menjamin kebersihan sistem dari halusinasi mikro. Implementasi penyaringan kata kunci di tingkat hulu (pre-retrieval filtering) juga terbukti efektif meminimalisasi ancaman siber berbasis prompt injection.
