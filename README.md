# PusulamNet

PusulamNet is a personal web application for tracking practice exams, planning study sessions, and reviewing progress for Turkish national exams.

Live application: https://pusulamnet-1.onrender.com

## Table of Contents

- [English](#english)
  - [Overview](#overview)
  - [Features](#features)
  - [Supported Exams](#supported-exams)
  - [Architecture](#architecture)
  - [Technology](#technology)
  - [Local Setup](#local-setup)
  - [Configuration](#configuration)
  - [Tests](#tests)
  - [Deployment and Security](#deployment-and-security)
- [Türkçe](#türkçe)
  - [Genel Bakış](#genel-bakış)
  - [Özellikler](#özellikler)
  - [Desteklenen Sınavlar](#desteklenen-sınavlar)
  - [Mimari](#mimari)
  - [Teknolojiler](#teknolojiler)
  - [Yerelde Çalıştırma](#yerelde-çalıştırma)
  - [Yapılandırma](#yapılandırma)
  - [Testler](#testler)
  - [Yayınlama ve Güvenlik](#yayınlama-ve-güvenlik)

## English

### Overview

PusulamNet helps students record correct, incorrect, and unanswered questions from practice exams; calculate net scores; observe progress through charts; and organize study tasks and notes in one place. It is designed as a responsive web application that can also be installed on a phone or tablet as a Progressive Web App.

### Features

- Practice exam tracking by exam type and course
- Automatic net-score calculation with configurable incorrect-answer penalties
- Performance analytics, moving averages, trend analysis, and course-level review
- Target tracking and official exam countdowns
- Pomodoro timer, stopwatch, study notes, and task planning
- CSV and Excel export for exam history and reports
- Light and dark themes with a responsive interface for mobile, tablet, and desktop
- JWT-based authentication and separate data for each user

### Supported Exams

- YKS TYT
- YKS AYT
- LGS
- KPSS
- TUS
- DUS

### Architecture

| Area | Responsibility |
| --- | --- |
| FastAPI application | Serves the web application and REST API |
| SQLAlchemy models | Defines users, exams, courses, goals, notes, and tasks |
| Service layer | Handles authentication, net calculations, analytics, exports, and seed data |
| Vanilla JavaScript SPA | Provides the client-side interface and API communication |
| PostgreSQL or SQLite | Stores application data |
| Service worker | Enables installable PWA behavior and offline shell caching |

### Technology

- Python 3.11
- FastAPI and Uvicorn
- SQLAlchemy and Pydantic
- PostgreSQL with Psycopg or SQLite for local development
- Vanilla JavaScript, HTML, CSS, and Chart.js
- PyJWT and Bcrypt
- Pytest, Pandas, and OpenPyXL
- Docker, Render, and Supabase PostgreSQL

### Local Setup

1. Create and activate a virtual environment.

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   Linux or macOS:

   ```bash
   source venv/bin/activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Start the development server.

   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. Open http://127.0.0.1:8000 in a browser. API documentation is available at http://127.0.0.1:8000/docs.

### Configuration

Copy `.env.example` to `.env` and set a strong secret key before production use.

```env
DATABASE_URL=sqlite:///./pusulamnet.db
SECRET_KEY=replace-with-a-long-random-value
```

For PostgreSQL, use the connection URL supplied by your provider. Do not commit `.env`, database files, or connection URLs to source control.

### Tests

Run the test suite with:

```bash
pytest app/tests
```

### Deployment and Security

The production deployment uses Render for the web service and Supabase PostgreSQL for persistent data. Configure `DATABASE_URL` and `SECRET_KEY` only in the Render Environment settings.

The source repository excludes `.env`, SQLite database files, virtual environments, and key files. Passwords are stored as Bcrypt hashes, and user-specific API endpoints require a valid JWT.

## Türkçe

### Genel Bakış

PusulamNet, Türkiye'deki ulusal sınavlara hazırlanan öğrencilerin deneme sonuçlarını kaydetmesini, netlerini otomatik hesaplamasını, gelişimini grafiklerle takip etmesini ve çalışma düzenini planlamasını sağlayan kişisel bir web uygulamasıdır. Mobil uyumlu yapısı sayesinde telefon ve tablette PWA olarak da kullanılabilir.

### Özellikler

- Sınav türü ve ders bazında deneme kaydı
- Yanlış cevap götürme oranına göre otomatik net hesaplama
- Hareketli ortalama, eğilim ve ders bazlı performans analizi
- Hedef takibi ve resmî sınav geri sayımları
- Pomodoro, kronometre, ders notları ve görev planlayıcısı
- Deneme geçmişi ve raporları CSV ile Excel olarak dışa aktarma
- Telefon, tablet ve masaüstüne uyumlu açık ve koyu tema
- JWT tabanlı oturum sistemi ve her kullanıcı için ayrı veriler

### Desteklenen Sınavlar

- YKS TYT
- YKS AYT
- LGS
- KPSS
- TUS
- DUS

### Mimari

| Katman | Sorumluluk |
| --- | --- |
| FastAPI uygulaması | Web arayüzünü ve REST API'yi sunar |
| SQLAlchemy modelleri | Kullanıcı, deneme, ders, hedef, not ve görev verilerini tanımlar |
| Servis katmanı | Kimlik doğrulama, net hesaplama, analiz, dışa aktarma ve örnek verileri yönetir |
| Vanilla JavaScript SPA | Arayüzü ve API iletişimini yönetir |
| PostgreSQL veya SQLite | Uygulama verilerini saklar |
| Service worker | Uygulamanın PWA olarak kurulmasını ve temel çevrimdışı önbelleği sağlar |

### Teknolojiler

- Python 3.11
- FastAPI ve Uvicorn
- SQLAlchemy ve Pydantic
- Psycopg ile PostgreSQL veya yerel geliştirme için SQLite
- Vanilla JavaScript, HTML, CSS ve Chart.js
- PyJWT ve Bcrypt
- Pytest, Pandas ve OpenPyXL
- Docker, Render ve Supabase PostgreSQL

### Yerelde Çalıştırma

1. Sanal ortam oluşturun ve etkinleştirin.

   ```bash
   python -m venv venv
   ```

   Windows:

   ```bash
   venv\Scripts\activate
   ```

   Linux veya macOS:

   ```bash
   source venv/bin/activate
   ```

2. Bağımlılıkları yükleyin.

   ```bash
   pip install -r requirements.txt
   ```

3. Geliştirme sunucusunu başlatın.

   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. Tarayıcıdan http://127.0.0.1:8000 adresini açın. API dokümantasyonuna http://127.0.0.1:8000/docs adresinden erişebilirsiniz.

### Yapılandırma

`.env.example` dosyasını `.env` olarak kopyalayın ve canlıya almadan önce güçlü bir gizli anahtar tanımlayın.

```env
DATABASE_URL=sqlite:///./pusulamnet.db
SECRET_KEY=uzun-ve-rastgele-bir-deger-yazin
```

PostgreSQL için sağlayıcınızın verdiği bağlantı adresini kullanın. `.env`, veritabanı dosyaları ve bağlantı adreslerini hiçbir zaman GitHub'a yüklemeyin.

### Testler

Testleri çalıştırmak için:

```bash
pytest app/tests
```

### Yayınlama ve Güvenlik

Canlı sürüm web servisi için Render, kalıcı veri için Supabase PostgreSQL kullanır. `DATABASE_URL` ve `SECRET_KEY` değerlerini yalnızca Render Environment ayarlarında saklayın.

Kaynak depoda `.env`, SQLite veritabanı dosyaları, sanal ortamlar ve anahtar dosyaları dışarıda bırakılır. Kullanıcı parolaları Bcrypt ile özetlenir; kullanıcıya özel API uçları geçerli bir JWT gerektirir.
