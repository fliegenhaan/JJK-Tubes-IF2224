# Lexical Analyzer Pascal-S

Implementasi Lexical Analyzer untuk bahasa pemrograman Pascal-S menggunakan Deterministic Finite Automaton (DFA).

## 👥 Identitas Kelompok

**Kelompok: JJK (JanganJanganKecompile)**

| Nama | NIM |
|------|-----|
| Muhammad Raihaan Perdana | 13523124 |
| Danendra Shafi Athallah | 13523136 |
| Nathanael Rachmat | 13523142 |
| M. Abizzar Gamadrian | 13523155 |

**Program Studi Teknik Informatika**  
Sekolah Teknik Elektro dan Informatika  
Institut Teknologi Bandung  
Tahun 2025

## Deskripsi Program

Lexical Analyzer (Lexer) adalah komponen pertama dalam proses kompilasi yang bertugas mengkonversi kode sumber menjadi token-token yang bermakna. Program ini mengimplementasikan lexer untuk bahasa Pascal-S dengan fitur-fitur:

### Fitur Utama
- ✅ Pengenalan keyword Pascal-S (`program`, `var`, `begin`, `end`, dll.)
- ✅ Identifikasi identifier dan variabel
- ✅ Support tipe data `integer` dan `real` (desimal)
- ✅ Operator aritmetika (`+`, `-`, `*`, `/`, `div`, `mod`)
- ✅ Operator relasional (`<`, `>`, `<=`, `>=`, `=`, `<>`)
- ✅ Operator logika (`and`, `or`, `not`)
- ✅ String literal dengan escape sequence
- ✅ Range operator (`..`)
- ✅ Error handling untuk input invalid

### Teknologi
- **Bahasa:** Python 3.7+
- **Model:** Deterministic Finite Automaton (DFA)
- **Konfigurasi:** JSON-based DFA rules

## Requirements

### Software
- Python 3.7 atau lebih baru
- Git (untuk cloning repository)

### Dependencies
**Tidak ada dependency eksternal** - Program hanya menggunakan Python standard library.

## 📦 Cara Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/fliegenhaan/JJK-Tubes-IF2224.git
cd JJK-Tubes-IF2224
```

### 2. Verifikasi Instalasi Python
```bash
python --version
# atau
python3 --version
```

## Cara Penggunaan

```bash
python3 src/compiler.py test/milestone-1/{test_case_file_name}.pas
```

## Testing

Program telah diuji dengan 6 kategori test case:

| Test Case | File | Tujuan |
|-----------|------|--------|
| Fungsionalitas Dasar | `test_basic.pas` | Token dasar |
| Real & Operator | `test_real_operators.pas` | Bilangan desimal, `mod`, `div` |
| Relasional & Logika | `test_relational_logic.pas` | `<>`, `<=`, `>=`, `and`, `or`, `not` |
| String Literal | `test_string_edgecase.pas` | String kosong, escape `''` |
| Range Operator | `test_range_operator.pas` | Token `..` |
| Error Handling | `test_error_handling.pas` | Input invalid |

## 👨‍💻 Pembagian Tugas

| Nama | Tugas |
|------|-------|
| **Nathanael Rachmat** | Implementasi kode program (`compiler.py`, `lexer.py`) |
| **Muhammad Raihaan Perdana** | Perancangan dan translasi DFA (`dfa_rules.json`) |
| **Danendra Shafi Athallah** | Diagram DFA dan dokumentasi laporan |
| **M. Abizzar Gamadrian** | Diagram DFA dan dokumentasi laporan |

## 📚 Referensi

- Spesifikasi Tugas: [Google Docs](https://docs.google.com/document/d/1w0GmHW5L0gKZQWbgmtJPFmOzlpSWBknNPdugucn4eII/edit?usp=sharing)
- Diagram DFA: [Google Drive](https://drive.google.com/file/d/1iRkdA6PxP96ra3_NZBBQHKHXOPRHp2pd/view?usp=drive_link)
- Repository: [GitHub](https://github.com/fliegenhaan/JJK-Tubes-IF2224.git)

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik Tugas Besar IF2224 - Teori Bahasa Formal & Otomata, Institut Teknologi Bandung.

---

**© 2025 Kelompok JJK - Institut Teknologi Bandung**
