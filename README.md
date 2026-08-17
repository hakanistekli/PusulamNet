---
title: PusulamNet
emoji: 🧭
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# PusulamNet - Student Exam Tracking & Analysis System

---

## Table of Contents / İçindekiler

- [English Section](#english-section)
  - [Overview](#overview)
  - [Key Features](#key-features)
  - [Application Screenshots](#application-screenshots)
  - [Project Architecture](#project-architecture)
  - [Tech Stack](#tech-stack)
  - [Quick Start & Setup](#quick-start--setup)
  - [Running Tests](#running-tests)
  - [Database & Configuration](#database--configuration)
  - [Security & Deployment](#security--deployment)
  - [License](#license)
- [Türkçe Bölüm](#türkçe-bölüm)
  - [Genel Bakış](#genel-bakış)
  - [Öne Çıkan Özellikler](#öne-çıkan-özellikler)
  - [Uygulama Ekran Görüntüleri](#uygulama-ekran-görüntüleri)
  - [Proje Mimarisi](#proje-mimarisi)
  - [Teknoloji Yığını](#teknoloji-yığını)
  - [Hızlı Başlangıç & Kurulum](#hızlı-başlangıç--kurulum)
  - [Testleri Çalıştırma](#testleri-çalıştırma)
  - [Veritabanı ve Yapılandırma](#veritabanı-ve-yapılandırma)
  - [Güvenlik ve Canlıya Alma](#güvenlik-ve-canlıya-alma)
  - [Lisans](#lisans)

---

## English Section

### Overview
PusulamNet is a full-stack student practice exam tracking, statistical analytics, and study planning web platform. It automatically calculates net scores based on exam-specific wrong-to-right penalty ratios, tracks moving averages, generates rule-based analytical feedback, provides official exam countdowns, study timers (Pomodoro/Stopwatch), and a course note notebook with to-do task planning.

### Key Features
- Automatic Net Score Calculation: Configurable penalty divisors per exam type (e.g. 4 wrong 1 right, 3 wrong 1 right).
- Statistical Performance Analytics: Moving averages, standard deviation stability classification (Stable, Moderately Volatile, Volatile), and trend evaluation.
- Rule-Based Automated Feedback Engine: Algorithmic text evaluation engine providing objective, constructive feedback summaries based on statistical threshold rules.
- Exam & Focus Timers: Official Exam Countdown Timer (auto-populates exam duration upon completion), Pomodoro Focus Timer, and Lap/Course Stopwatch.
- Subject Notes Notebook & Study Planner: Course-categorized note taker and prioritized to-do task list.
- Official Exam Countdown: Dynamic countdown widget tracking upcoming ÖSYM and MEB official exam dates.
- Data Export: Export practice exam history and general performance summaries to CSV and Excel (.xlsx) formats.
- Fully Responsive Interface: Dark/Light mode support, modern glassmorphism design system, and custom modal dialogs.

### Application Screenshots

<img width="1571" height="1007" alt="Ekran görüntüsü 2026-08-14 165618" src="https://github.com/user-attachments/assets/524b205f-ab31-463c-ada2-0951ba73f3f1" /><img width="1894" height="1065" alt="Ekran görüntüsü 2026-08-14 165605" src="https://github.com/user-attachments/assets/9f9653f3-ec87-4eea-8e72-b04fea40e9e0" />
<img width="351" height="385" alt="Ekran görüntüsü 2026-08-14 165744" src="https://github.com/user-attachments/assets/75a191fa-ad72-4ab0-9cdb-423bf1a4b0e8" />
<img width="1914" height="1072" alt="Ekran görüntüsü 2026-08-14 165736" src="https://github.com/user-attachments/assets/da3f79eb-32a3-4ece-930e-396cd2c36ce7" />
<img width="1910" height="1073" alt="Ekran görüntüsü 2026-08-14 165729" src="https://github.com/user-attachments/assets/a45886fd-7030-4a3d-b44f-9fd8f95464b0" />
<img width="1893" height="1073" alt="Ekran görüntüsü 2026-08-14 165711" src="https://github.com/user-attachments/assets/b260064f-3f26-4892-8034-b5b8738a6294" /><img width="1892" height="1068" alt="Ekran görüntüsü 2026-08-14 165631" src="https://github.com/user-attachments/assets/df7b186a-00d9-49d1-9322-92e8fe12251e" />oading Ekran görüntüsü 2026-08-14 165618.png…]()
<img width="1895" height="1069" alt="Ekran görüntüsü 2026-08-14 165702" src="https://github.com/user-attachments/assets/d4082ce0-af99-4f56-84ad-7be030f3200c" />
<img width="1875" height="1062" alt="Ekran görüntüsü 2026-08-14 165653" src="https://github.com/user-attachments/assets/d0b9bfa5-317a-4c3a-b369-912ae039069a" />
<img width="1906" height="1064" alt="Ekran görüntüsü 2026-08-14 165640" src="https://github.com/user-attachments/assets/6604a685-7697-484d-9480-eb0e4316badd" />

### Project Architecture
```text
PusulamNet/
├── app/
│   ├── main.py               # FastAPI Main Entrypoint & Router Ingestion
│   ├── config.py             # Application Settings & Statistical Thresholds
│   ├── database.py           # SQLAlchemy Database Engine & Session Setup
│   ├── models.py             # SQLAlchemy Database ORM Models
│   ├── schemas.py            # Pydantic Request & Response Schemas
│   ├── services/
│   │   ├── auth_service.py      # Authentication & JWT Token Management
│   │   ├── net_calculator.py    # Net Score Calculation & Validation
│   │   ├── analysis_service.py  # Statistical & Moving Average Analytics
│   │   ├── explanation_service.py # Rule-Based Text Analysis Engine
│   │   ├── export_service.py    # CSV & Excel Export Generator
│   │   └── demo_data_service.py # Predefined Exam & Demo Seeding Service
│   ├── api/
│   │   ├── auth.py            # Authentication Endpoints
│   │   ├── dashboard.py       # Dashboard Analytics API
│   │   ├── exams.py           # Practice Exam CRUD & Export API
│   │   ├── exam_types.py      # Exam Types & Course Settings API
│   │   ├── course_analysis.py # Subject Analysis API
│   │   ├── goals.py           # Target Goal Tracking API
│   │   ├── report.py          # General Report API
│   │   ├── planner.py         # Study Notes & Tasks API
│   │   └── demo.py            # Demo Data Reset API
│   └── tests/
│       ├── test_auth_service.py
│       ├── test_net_calculator.py
│       ├── test_analysis_service.py
│       └── test_explanation_service.py
├── static/
│   ├── screenshots/          # Application UI Screenshots
│   ├── index.html            # Main SPA HTML Dashboard Layout
│   ├── css/
│   │   └── styles.css        # Custom Modern CSS & Theme Variables
│   └── js/
│       ├── app.js            # SPA Controller & Timer Management
│       ├── api.js            # Central Backend API Client
│       └── charts.js         # Chart.js Rendering Engine
├── requirements.txt          # Python Dependencies List
├── .env.example              # Environment Configuration Template
├── .gitignore                # Git Excluded Files Rules
└── README.md                 # Project Documentation
```

### Tech Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy ORM, SQLite / PostgreSQL, Pydantic, Passlib (Bcrypt), PyJWT, Pytest
- Frontend: Single Page Application (SPA), HTML5, Vanilla CSS3 (Custom Dark Glassmorphism System), Vanilla JavaScript (ES6+ OOP), Chart.js, Lucide Icons

### Quick Start & Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the application:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. Access web application at `http://127.0.0.1:8000` and API docs at `http://127.0.0.1:8000/docs`.

### Running Tests
Execute unit tests via Pytest:
```bash
pytest
```

### Database & Configuration
The default database is SQLite (`pusulamnet.db`). To configure PostgreSQL or change environment settings, update `.env`:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/pusulamnet
SECRET_KEY=your_production_secret_key_here
```

### Security & Deployment
- Never commit `.env` or `pusulamnet.db` files. Exclusions are defined in `.gitignore`.
- Use a strong `SECRET_KEY` in production.
- Enable HTTPS SSL certificates for production server deployments.

### License
This project is licensed under the MIT License.

---

## Türkçe Bölüm

### Genel Bakış
PusulamNet, öğrencilerin çözdükleri deneme sınavlarının sonuçlarını (doğru, yanlış, boş) ders bazında kaydederek netlerini otomatik hesaplamasını, gelişim süreçlerini istatistiksel grafiklerle takip etmesini, geri sayım sayacı ve zamanlayıcı araçlarıyla çalışma oturumlarını yönetmesini sağlayan tam kapsamlı bir web uygulamasıdır.

### Öne Çıkan Özellikler
- Otomatik Net Hesaplama: Sınav türüne özel yanlış-doğru götürme katsayıları (Örn: 4 yanlış 1 doğru, 3 yanlış 1 doğru).
- İstatistiksel Performans Analizi: Ortalama net, hareketli ortalamalar, standart sapma ile performans istikrarı sınıflandırması (İstikrarlı, Orta Dalgalı, Dalgalı) ve eğilim analizi.
- Kural Tabanlı Otomatik Değerlendirme Motoru: İstatistiksel eşik değerlerine dayalı yapıcı ve nesnel Türkçe analiz motoru.
- Sınav & Çalışma Zamanlayıcısı: Gerçek Sınav Modu (Deneme süresi bitince süre aktarımı), Pomodoro Odaklanma Modu ve Tur/Ders Sayacı.
- Ders Notları Defteri & Çalışma Planlayıcısı: Ders bazlı kategorize edilebilir not defteri ve öncelik seviyeli yapılacaklar listesi.
- Resmi Sınav Geri Sayımı: ÖSYM ve MEB resmi sınav tarihlerine göre dinamik kalan zaman sayacı.
- Veri Dışa Aktarma: Deneme geçmişi ve genel performans raporlarının CSV ve Excel (.xlsx) formatında indirilmesi.
- Tam Responsive Arayüz: Koyu/Açık Tema desteği, cam efektli (glassmorphism) modern arayüz ve özel diyalog modalları.

### Uygulama Ekran Görüntüleri

<img width="1571" height="1007" alt="Ekran görüntüsü 2026-08-14 165618" src="https://github.com/user-attachments/assets/524b205f-ab31-463c-ada2-0951ba73f3f1" /><img width="1894" height="1065" alt="Ekran görüntüsü 2026-08-14 165605" src="https://github.com/user-attachments/assets/9f9653f3-ec87-4eea-8e72-b04fea40e9e0" />
<img width="351" height="385" alt="Ekran görüntüsü 2026-08-14 165744" src="https://github.com/user-attachments/assets/75a191fa-ad72-4ab0-9cdb-423bf1a4b0e8" />
<img width="1914" height="1072" alt="Ekran görüntüsü 2026-08-14 165736" src="https://github.com/user-attachments/assets/da3f79eb-32a3-4ece-930e-396cd2c36ce7" />
<img width="1910" height="1073" alt="Ekran görüntüsü 2026-08-14 165729" src="https://github.com/user-attachments/assets/a45886fd-7030-4a3d-b44f-9fd8f95464b0" />
<img width="1893" height="1073" alt="Ekran görüntüsü 2026-08-14 165711" src="https://github.com/user-attachments/assets/b260064f-3f26-4892-8034-b5b8738a6294" /><img width="1892" height="1068" alt="Ekran görüntüsü 2026-08-14 165631" src="https://github.com/user-attachments/assets/df7b186a-00d9-49d1-9322-92e8fe12251e" />oading Ekran görüntüsü 2026-08-14 165618.png…]()
<img width="1895" height="1069" alt="Ekran görüntüsü 2026-08-14 165702" src="https://github.com/user-attachments/assets/d4082ce0-af99-4f56-84ad-7be030f3200c" />
<img width="1875" height="1062" alt="Ekran görüntüsü 2026-08-14 165653" src="https://github.com/user-attachments/assets/d0b9bfa5-317a-4c3a-b369-912ae039069a" />
<img width="1906" height="1064" alt="Ekran görüntüsü 2026-08-14 165640" src="https://github.com/user-attachments/assets/6604a685-7697-484d-9480-eb0e4316badd" />
### Proje Mimarisi
```text
PusulamNet/
├── app/
│   ├── main.py               # FastAPI Ana Uygulama & Sunucu
│   ├── config.py             # Ayarlar & Analiz Eşik Değerleri
│   ├── database.py           # SQLAlchemy Veritabanı Bağlantısı
│   ├── models.py             # SQLAlchemy ORM Veritabanı Modelleri
│   ├── schemas.py            # Pydantic Şemaları
│   ├── services/
│   │   ├── auth_service.py      # Kimlik Doğrulama & JWT Servisi
│   │   ├── net_calculator.py    # Net & Form Doğrulama Servisi
│   │   ├── analysis_service.py  # İstatistik & Hareketli Ortalama Servisi
│   │   ├── explanation_service.py # Kural Tabanlı Metin Açıklama Motoru
│   │   ├── export_service.py    # CSV & Excel Dışa Aktarma Servisi
│   │   └── demo_data_service.py # Örnek Demo Veri Yükleme Servisi
│   ├── api/
│   │   ├── auth.py            # Kimlik Doğrulama API
│   │   ├── dashboard.py       # Ana Panel API
│   │   ├── exams.py           # Deneme CRUD & Export API
│   │   ├── exam_types.py      # Sınav Türleri & Ders Ayarları API
│   │   ├── course_analysis.py # Ders Analizi API
│   │   ├── goals.py           # Hedef Takip API
│   │   ├── report.py          # Genel Rapor API
│   │   ├── planner.py         # Notlar & Planlayıcı API
│   │   └── demo.py            # Demo Yükleme API
│   └── tests/
│       ├── test_auth_service.py
│       ├── test_net_calculator.py
│       ├── test_analysis_service.py
│       └── test_explanation_service.py
├── static/
│   ├── screenshots/          # Ekran Görüntüleri Görselleri
│   ├── index.html            # Modern Web SPA Ana Arayüzü
│   ├── css/
│   │   └── styles.css        # Custom CSS & Tema Stilleri
│   └── js/
│       ├── app.js            # SPA Controller & Zamanlayıcı Motoru
│       ├── api.js            # Backend API İletişim Modülü
│       └── charts.js         # Chart.js Görselleştirme Modülü
├── requirements.txt          # Python Bağımlılık Listesi
├── .env.example              # Ortam Değişkenleri Şablonu
├── .gitignore                # Git Engelleme Kuralları
└── README.md                 # Proje Dokümantasyonu
```

### Teknoloji Yığını
- Arka Plan (Backend): Python 3.12, FastAPI, SQLAlchemy ORM, SQLite / PostgreSQL, Pydantic, Passlib (Bcrypt), PyJWT, Pytest
- Ön Yüz (Frontend): Tek Sayfa Uygulaması (SPA), HTML5, Vanilla CSS3 (Koyu Cam Efektli Tasarım), Vanilla JavaScript (ES6+ OOP), Chart.js, Lucide İkonları

### Hızlı Başlangıç & Kurulum
1. Sanal ortamı (venv) oluşturun ve aktif edin:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/macOS:
   source venv/bin/activate
   ```
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Uygulamayı başlatın:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
4. Uygulamaya `http://127.0.0.1:8000` adresinden, Swagger API dokümantasyonuna `http://127.0.0.1:8000/docs` adresinden erişebilirsiniz.

### Testleri Çalıştırma
Birim testlerini yürütmek için:
```bash
pytest
```

### Veritabanı ve Yapılandırma
Uygulama varsayılan olarak `pusulamnet.db` adında SQLite veritabanı kullanır. PostgreSQL veritabanına geçmek için `.env` dosyasını güncelleyin:
```env
DATABASE_URL=postgresql://kullanici:sifre@localhost:5432/pusulamnet
SECRET_KEY=goclu_ve_gizli_jwt_anahtari
```

### Güvenlik ve Canlıya Alma
- Üretim ortamında `.env` dosyasında güçlü bir `SECRET_KEY` tanımlayın.
- `.env` ve `pusulamnet.db` dosyalarını asla GitHub'a commit etmeyin. `.gitignore` yapılandırması hazır durumdadır.
- Canlı sunucu kurulumlarında HTTPS SSL sertifikası kullanın.

### Lisans
Bu proje MIT lisansı ile korunmaktadır.
