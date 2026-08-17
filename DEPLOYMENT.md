# PusulamNet'i kalıcı veritabanıyla yayınlama

Bu kurulumda arayüz ve FastAPI sunucusu Render'da, öğrenci verileri ise
Supabase PostgreSQL'de tutulur. Böylece Render'ın ücretsiz sunucusu uyusa veya
yeniden başlasa bile denemeler, notlar ve hedefler silinmez.

## 1. Supabase veritabanını oluşturun

1. Supabase'de yeni bir **Free** proje oluşturun.
2. Proje hazır olduğunda **Connect** bölümünden PostgreSQL bağlantı dizesini
   kopyalayın. Doğrudan bağlantı dizesinde `sslmode=require` bulunmalıdır.
3. Bu dizeyi kimseyle paylaşmayın; veritabanı parolası içerir.

## 2. Mevcut verileri bir kez taşıyın

Önce proje klasöründe bağımlılıkları güncelleyin:

```powershell
.\venv\Scripts\pip install -r requirements.txt
```

Ardından bağlantı dizesini geçici olarak ortam değişkeni yapıp aktarımı başlatın:

```powershell
$env:DATABASE_URL = "Supabase'ten-kopyalanan-postgresql-baglanti-dizesi"
.\venv\Scripts\python scripts\migrate_sqlite_to_postgres.py
```

İşlem yalnızca boş hedef veritabanına yazılır. Bu güvenlik önlemi aynı veriyi
iki kez eklemeyi engeller. Başarılı aktarımın ardından `pusulamnet.db` dosyasını
silmek yerine güvenli bir yerde yedek olarak tutun.

## 3. Render'da yayınlayın

1. Projeyi GitHub'a gönderip Render'da **New > Web Service** ile bağlayın.
2. Ortam olarak Dockerfile'ı seçin.
3. Render ortam değişkenlerine aşağıdakileri ekleyin:

   - `DATABASE_URL`: Supabase PostgreSQL bağlantı dizesi
   - `SECRET_KEY`: uzun, rastgele ve yalnızca bu uygulamaya ait bir değer

4. Yayınlama tamamlandığında Render adresini telefonda açın.

## Telefona uygulama gibi ekleme

- Android Chrome: menüden **Ana ekrana ekle** veya **Uygulamayı yükle**.
- iPhone/iPad Safari: **Paylaş > Ana Ekrana Ekle**.

PusulamNet açılır pencere yerine uygulama görünümünde çalışır. İnternet yokken
son açılan arayüz kabuğu görünür; veri kaydetme ve güncel verileri alma için
internet bağlantısı gerekir.

## Ücretsiz plan notu

Render'ın ücretsiz web servisi 15 dakika kullanılmayınca uyur; sonraki açılış
biraz daha uzun sürebilir. Supabase ücretsiz proje bir hafta hiç kullanılmazsa
duraklatılabilir. Bu durum veri silinmesi değildir; proje yeniden açıldığında
aynı PostgreSQL verileri kullanılmaya devam eder.
