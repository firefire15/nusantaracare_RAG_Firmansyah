# nusantaracare_RAG_Firmansyah
## 1. Problem & Success Criteria
      Problem dan success criteria berisi tentang tujuan bisnis, kriteria sukses, jenis pertanyaan yang ditargetkan, dan batasan sistem dari nusantaracare_RAG ini. Adapun penjelasannya adalah sebagai berikut
### Tujuan Bisnis
     beberapa tujuan bisnis yang bisa didapatkan dari penggunaan RAG adalah
     1. Sebagai efisiensi dari operasional karena 
### kriteria sukses, 
### jenis pertanyaan yang ditargetkan
### batasan sistem.

2. Knowledge Base Understanding
Deskripsikan isi dan struktur dokumen NusantaraCare. Catat metadata: doc_id, doc_version, effective_date, is_active, dll. Tunjukkan pemahaman tentang perbedaan v1.4 vs v2.0.

3. RAG Design & Data Preparation (20 poin)
Jelaskan Design RAG yang ingin dibuat, misalnya menjelaskan :

Chunking: ukuran chunk, overlap, dan alasannya
Metadata per chunk: doc_id, chunk_id, doc_title, section_title, doc_version, is_active, dll.
Vector database: pilihan dan justifikasi (FAISS, ChromaDB, dsb.)
Retrieval: top-k, threshold, filtering
Prompt: instruksi “jawab hanya dari konteks”
Dokumen nonaktif/konflik: bagaimana menangani v1.4 vs v2.0
4. Kesimpulan & Dokumentasi (5 poin)
Rangkum performa sistem, rekomendasi perbaikan. Tulis README.md lengkap dengan  seksi: Problem, KB Understanding, RAG Design, Arsitektur, Kontrak API, Cara Menjalankan Lokal, Deployment, Keterbatasan (jika ada)
