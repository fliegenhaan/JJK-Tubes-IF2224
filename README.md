# Compiler Pascal-S

Implementasi Compiler untuk bahasa pemrograman Pascal-S yang terdiri dari Lexical Analyzer (DFA) dan Syntax Analyzer (Parser).

## 👥 Identitas Kelompok

**Kelompok: JJK (JanganJanganKecompile)**

| Nama                     | NIM      |
| ------------------------ | -------- |
| Muhammad Raihaan Perdana | 13523124 |
| Danendra Shafi Athallah  | 13523136 |
| Nathanael Rachmat        | 13523142 |
| M. Abizzar Gamadrian     | 13523155 |

**Program Studi Teknik Informatika**  
Sekolah Teknik Elektro dan Informatika  
Institut Teknologi Bandung  
Tahun 2025

## Deskripsi Program

Program ini mengimplementasikan compiler untuk bahasa Pascal-S yang terdiri dari dua komponen utama:

### 🔹 Milestone 1: Lexical Analyzer (Lexer)

Komponen pertama dalam proses kompilasi yang bertugas mengkonversi kode sumber menjadi token-token yang bermakna.

**Fitur:**

- ✅ Pengenalan keyword Pascal-S (`program`, `var`, `begin`, `end`, dll.)
- ✅ Identifikasi identifier dan variabel
- ✅ Support tipe data `integer` dan `real` (desimal)
- ✅ Operator aritmetika (`+`, `-`, `*`, `/`, `div`, `mod`)
- ✅ Operator relasional (`<`, `>`, `<=`, `>=`, `=`, `<>`)
- ✅ Operator logika (`and`, `or`, `not`)
- ✅ String literal dengan escape sequence
- ✅ Range operator (`..`)
- ✅ Error handling untuk input invalid

### 🔹 Milestone 2: Syntax Analyzer (Parser)

Komponen kedua yang melakukan analisis sintaks dan membangun parse tree dari token-token yang dihasilkan lexer.

**Fitur:**

- ✅ Parsing struktur program Pascal-S lengkap
- ✅ Deklarasi variabel, konstanta, dan tipe data
- ✅ Statement control flow (`jika-maka-tidak`, `untuk`, `selagi`)
- ✅ Statement `case` untuk kondisi majemuk
- ✅ Deklarasi dan pemanggilan procedure & function
- ✅ Array dan struktur data
- ✅ Nested structures (struktur bersarang)
- ✅ Complex expressions (ekspresi kompleks)
- ✅ Syntax error detection dan reporting

### 🔹 Milestone 3: Semantic Analyzer

Komponen ketiga yang memvalidasi makna dari struktur program yang telah diparsing, memastikan kepatuhan terhadap aturan semantik bahasa Pascal-S.

**Fitur & Kesimpulan:**
Berdasarkan perancangan, implementasi, dan pengujian yang telah dilakukan, implementasi Semantic Analyzer berhasil diintegrasikan dengan Lexer dan Parser sehingga melengkapi keseluruhan fungsionalitas compiler Pascal-S.

- ✅ **Visitor Pattern**: Penggunaan pola Visitor pada AST terbukti efektif dalam melakukan analisis semantik.
- ✅ **Symbol Table**: Struktur data Symbol Table (tab, atab, btab) mampu mengelola manajemen scope (termasuk nested scope) dan memeriksa tipe data kompleks (array, record).
- ✅ **Type Checking**: Sistem Type Checking menjalankan aturan _strong typing_ dengan baik, mencegah operasi ilegal seperti assignment antartipe yang tidak kompatibel.
- ✅ **Error Handling**: Mampu mendeteksi berbagai kesalahan semantik serta memberikan pesan error yang jelas.

### Teknologi

- **Bahasa:** Python 3.7+
- **Lexer:** Deterministic Finite Automaton (DFA)
- **Parser:** Recursive Descent Parser dengan Context-Free Grammar (CFG)
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

### Mode 1: Full Compilation (Lexer + Parser)

Untuk menjalankan lexical analysis dan syntax analysis sekaligus:

```bash
python src/compiler.py test/milestone-2/{test_case_file_name}.pas
```

### Mode 2: Lexer Only (Milestone 1)

Untuk menjalankan hanya lexical analysis:

```bash
python src/compiler.py test/milestone-1/{test_case_file_name}.pas
```

atau dengan flag `--lexer-only`:

```bash
python src/compiler.py test/milestone-2/{test_case_file_name}.pas --lexer-only
```

### Mode 3: Parser dari File Token

Untuk menjalankan syntax analysis dari file tokenisasi (.txt):

```bash
python src/compiler.py test/milestone-2/{result_file_name}.txt
```

### Contoh Output

**Lexer Output:**

```
KEYWORD(program)
IDENTIFIER(Hello)
SEMICOLON(;)
...
```

**Parser Output (Parse Tree):**

```
<program>
├── <program-header>
│   ├── KEYWORD(program)
│   ├── IDENTIFIER(Hello)
│   └── SEMICOLON(;)
├── <declaration-part>
...
```

## Struktur Proyek

```
JJK-Tubes-IF2224/
├── src/
│   ├── compiler.py          # Program utama
│   ├── lexer.py             # Lexical Analyzer (Milestone 1)
│   ├── parser.py            # Syntax Analyzer (Milestone 2)
│   └── dfa_rules.json       # Konfigurasi DFA untuk lexer
├── test/
│   ├── milestone-1/         # Test case untuk lexer
│   │   ├── test_basic.pas
│   │   ├── test_real_operators.pas
│   │   └── ...
│   └── milestone-2/         # Test case untuk parser
│       ├── test1_simple.pas
│       ├── test2_if_statement.pas
│       └── ...
├── doc/
│   ├── Laporan-1-JJK.pdf    # Laporan Milestone 1
│   ├── Laporan-2-JJK.pdf    # Laporan Milestone 2
│   ├── Diagram-1-JJK.png    # Diagram DFA (Milestone 1)
│   └── Diagram-2-JJK.png    # Diagram Parse Tree (Milestone 2)
└── README.md
```

## Testing

### Milestone 1: Lexical Analyzer

Program telah diuji dengan 6 kategori test case:

| Test Case            | File                        | Tujuan                               |
| -------------------- | --------------------------- | ------------------------------------ |
| Fungsionalitas Dasar | `test_basic.pas`            | Token dasar                          |
| Real & Operator      | `test_real_operators.pas`   | Bilangan desimal, `mod`, `div`       |
| Relasional & Logika  | `test_relational_logic.pas` | `<>`, `<=`, `>=`, `and`, `or`, `not` |
| String Literal       | `test_string_edgecase.pas`  | String kosong, escape `''`           |
| Range Operator       | `test_range_operator.pas`   | Token `..`                           |
| Error Handling       | `test_error_handling.pas`   | Input invalid                        |

### Milestone 2: Syntax Analyzer

Program telah diuji dengan 14 test case plus 2 error case:

| No  | Test Case                | File                                | Tujuan                              |
| --- | ------------------------ | ----------------------------------- | ----------------------------------- |
| 1   | Simple Program           | `test1_simple.pas`                  | Struktur program sederhana          |
| 2   | If Statement             | `test2_if_statement.pas`            | Statement `jika-maka-tidak`         |
| 3   | Loop                     | `test3_loop.pas`                    | Statement perulangan `untuk`        |
| 4   | Procedure                | `test4_procedure.pas`               | Deklarasi dan pemanggilan procedure |
| 5   | Function                 | `test5_function.pas`                | Deklarasi dan pemanggilan function  |
| 6   | Array                    | `test6_array.pas`                   | Penggunaan array                    |
| 7   | While Loop               | `test7_while.pas`                   | Statement perulangan `selagi`       |
| 8   | Constant                 | `test8_const.pas`                   | Deklarasi konstanta                 |
| 9   | Nested Structures        | `test9_nested_structures.pas`       | Struktur bersarang                  |
| 10  | Complex Expression       | `test10_complex_expression.pas`     | Ekspresi matematika kompleks        |
| 11  | Nested Loops             | `test11_nested_loops.pas`           | Perulangan bersarang                |
| 12  | Multiple Subprograms     | `test12_multiple_subprograms.pas`   | Banyak procedure/function           |
| 13  | Case Statement           | `test13_case_statement.pas`         | Statement `case`                    |
| 14  | Underscore Identifier    | `test_underscore_identifier.pas`    | Identifier dengan underscore        |
| E1  | Error: Missing Semicolon | `test_error1_missing_semicolon.pas` | Deteksi error syntax                |
| E2  | Error: Missing `maka`    | `test_error2_missing_maka.pas`      | Deteksi error syntax                |

## 👨‍💻 Pembagian Tugas

| No  | Tugas                                                              | NIM                                    |
| --- | ------------------------------------------------------------------ | -------------------------------------- |
| 1   | Implementasi kode program (`compiler.py`, `lexer.py`, `parser.py`) | 13523136, 13523142                     |
| 2   | Perancangan DFA rules                                              | 13523136, 13523124                     |
| 3   | Dokumentasi laporan                                                | 13523136, 13523155, 13523124, 13523142 |
| 4   | Perancangan diagram                                                | 13523124, 13523136                     |

### Pembagian Tugas Milestone 3

| No  | NIM      | Tugas                                                                                           | Persentase |
| --- | -------- | ----------------------------------------------------------------------------------------------- | ---------- |
| 1   | 13523124 | Implementasi kode program; Perancangan DFA rules; Dokumentasi laporan; Perancangan diagram      | 25%        |
| 2   | 13523136 | Implementasi kode program; Pembuatan Test Case unik; Perancangan DFA rules; Dokumentasi laporan | 25%        |
| 3   | 13523142 | Perancangan DFA rules; Dokumentasi laporan; Perancangan diagram                                 | 25%        |
| 4   | 13523155 | Dokumentasi laporan                                                                             | 25%        |

## 📚 Referensi

### Dokumentasi

- **Laporan Milestone 1:** [doc/Laporan-1-JJK.pdf](doc/Laporan-1-JJK.pdf)
- **Laporan Milestone 2:** [doc/Laporan-2-JJK.pdf](doc/Laporan-2-JJK.pdf)
- **Diagram DFA (Milestone 1):** [doc/Diagram-1-JJK.png](doc/Diagram-1-JJK.png)
- **Diagram Parse Tree (Milestone 2):** [doc/Diagram-2-JJK.png](doc/Diagram-2-JJK.png)

### Link Eksternal

- **Repository GitHub:** [github.com/fliegenhaan/JJK-Tubes-IF2224](https://github.com/fliegenhaan/JJK-Tubes-IF2224.git)

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademik Tugas Besar IF2224 - Teori Bahasa Formal & Otomata, Institut Teknologi Bandung.

---

**© 2025 Kelompok JJK - Institut Teknologi Bandung**
