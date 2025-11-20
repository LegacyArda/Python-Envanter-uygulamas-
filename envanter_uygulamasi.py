import mysql.connector
from datetime import datetime # Tarih formatlama için

# ==========================================================================
# ⚙️ BAĞLANTI VE TEMEL AYARLAR
# ==========================================================================

# NOT: Bu bilgileri kendi veritabanı kurulumunuza göre DÜZENLEYİN.
DB_HOST = "127.0.0.1"
DB_USER = "legacy"
DB_PASSWORD = "ardaarda4141" # KENDİ ŞİFRENİZİ BURAYA GİRİN!
DB_NAME = "envanter_db"
TABLO_ADI = "urunler"

# ==========================================================================
# 🛠️ GENEL FONKSİYONLAR
# ==========================================================================

def get_db_connection(use_db=True):
    """
    MySQL sunucusuna veya belirtilen veritabanına bağlanır.
    use_db=False ise, henüz oluşturulmamış veritabanı ismini kullanmadan sunucuya bağlanır.
    """
    try:
        if use_db:
            # Belirtilen veritabanına bağlan
            cnn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        else:
            # Sadece MySQL sunucusuna bağlan (Veritabanı oluşturmak için)
            cnn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
        return cnn
    except mysql.connector.Error as err:
        print(f"❌ Hata: Veritabanına bağlanılamadı. Ayarları kontrol edin: {err}")
        return None

def veritabani_ve_tablo_olustur():
    """İlk çalıştırmada veritabanını ve tabloyu oluşturur."""
    cnn = get_db_connection(use_db=False)
    if cnn is None:
        return

    cursor = cnn.cursor()

    try:
        # 1. Veritabanını oluşturma (Eğer mevcut değilse)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ '{DB_NAME}' veritabanı kontrol edildi/oluşturuldu.")

        # 2. Bağlantıyı yeni veritabanına çevir
        cnn.database = DB_NAME

        # 3. Tablo oluşturma
        tablo_olusturma_sorgusu = f"""
        CREATE TABLE IF NOT EXISTS {TABLO_ADI} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            urun_adi VARCHAR(255) NOT NULL,
            aciklama TEXT,
            stok_miktari INT NOT NULL,
            fiyat DECIMAL(10, 2) NOT NULL,
            eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(tablo_olusturma_sorgusu)
        print(f"✅ '{TABLO_ADI}' tablosu kontrol edildi/oluşturuldu.")

        cnn.commit()

    except mysql.connector.Error as err:
        print(f"❌ Tablo Oluşturma Hatası: {err}")
    finally:
        cursor.close()
        cnn.close()

# ==========================================================================
# ➕ CREATE (EKLEME)
# ==========================================================================

def urun_ekle(urun_adi, aciklama, stok_miktari, fiyat):
    """Yeni bir ürün kaydını tabloya ekler."""
    cnn = get_db_connection()
    if cnn is None:
        return

    cursor = cnn.cursor()
    sorgu = f"INSERT INTO {TABLO_ADI} (urun_adi, aciklama, stok_miktari, fiyat) VALUES (%s, %s, %s, %s)"
    degerler = (urun_adi, aciklama, stok_miktari, fiyat)

    try:
        cursor.execute(sorgu, degerler)
        cnn.commit()
        print(f"✅ Ürün başarıyla eklendi. ID: {cursor.lastrowid}")

    except mysql.connector.Error as err:
        print(f"❌ Hata: Ürün eklenemedi: {err}")
        cnn.rollback()

    finally:
        cursor.close()
        cnn.close()

# ==========================================================================
# 🔎 READ (LİSTELEME)
# ==========================================================================

def urunleri_listele():
    """Tüm ürün kayıtlarını tablodan okur."""
    cnn = get_db_connection()
    if cnn is None:
        return [], []

    cursor = cnn.cursor()
    sorgu = f"SELECT id, urun_adi, stok_miktari, fiyat, eklenme_tarihi FROM {TABLO_ADI}"

    try:
        cursor.execute(sorgu)
        sonuclar = cursor.fetchall()
        # Sütun isimlerini al
        sutun_isimleri = [i[0] for i in cursor.description]
        return sutun_isimleri, sonuclar

    except mysql.connector.Error as err:
        print(f"❌ Hata: Ürünler listelenemedi: {err}")
        return [], []

    finally:
        cursor.close()
        cnn.close()

def envanteri_goster():
    """Ürün listeleme fonksiyonunu çalıştırır ve sonuçları formatlı gösterir."""
    basliklar, urun_listesi = urunleri_listele()

    print("\n" + "="*70)
    print("                      📊 MEVCUT ENVANTER LİSTESİ 📊")
    print("="*70)

    if not urun_listesi:
        print("Envanterde kayıtlı ürün bulunmamaktadır.")
        return

    # Başlıkları formatlı yazdır
    print(f"| {'ID':<3} | {'Ürün Adı':<25} | {'Stok':<10} | {'Fiyat':<8} | {'Eklenme Tarihi':<19} |")
    print("-" * 70)

    # Ürünleri formatlı yazdır
    for urun in urun_listesi:
        fiyat_str = f"{urun[3]:.2f}"
        # Tarih formatını temizleyerek yazdır
        tarih_str = urun[4].strftime("%Y-%m-%d %H:%M:%S")

        print(f"| {urun[0]:<3} | {urun[1]:<25} | {urun[2]:<10} | {fiyat_str:<8} | {tarih_str:<19} |")

    print("="*70 + "\n")

# ==========================================================================
# ✏️ UPDATE (GÜNCELLEME)
# ==========================================================================

def urun_guncelle(urun_id, yeni_stok, yeni_fiyat=None, yeni_aciklama=None):
    """Belirtilen ID'ye sahip ürünün bilgilerini günceller."""
    cnn = get_db_connection()
    if cnn is None:
        return

    cursor = cnn.cursor()
    guncellenecek_alanlar = ["stok_miktari = %s"]
    degerler = [yeni_stok]

    if yeni_fiyat is not None:
        guncellenecek_alanlar.append("fiyat = %s")
        degerler.append(yeni_fiyat)

    if yeni_aciklama is not None:
        guncellenecek_alanlar.append("aciklama = %s")
        degerler.append(yeni_aciklama)

    set_ifadesi = ", ".join(guncellenecek_alanlar)
    sorgu = f"UPDATE {TABLO_ADI} SET {set_ifadesi} WHERE id = %s"
    degerler.append(urun_id)

    try:
        cursor.execute(sorgu, tuple(degerler))

        if cursor.rowcount == 0:
            print(f"⚠️ ID {urun_id} bulunamadı veya güncelleme yapılmadı.")
        else:
            cnn.commit()
            print(f"✅ Ürün ID: {urun_id} başarıyla güncellendi.")

    except mysql.connector.Error as err:
        print(f"❌ Hata: Ürün güncellenemedi: {err}")
        cnn.rollback()

    finally:
        cursor.close()
        cnn.close()

# ==========================================================================
# 🗑️ DELETE (SİLME)
# ==========================================================================

def urun_sil(urun_id):
    """Belirtilen ID'ye sahip ürünü veritabanından siler."""
    cnn = get_db_connection()
    if cnn is None:
        return

    cursor = cnn.cursor()
    sorgu = f"DELETE FROM {TABLO_ADI} WHERE id = %s"
    degerler = (urun_id,)

    try:
        cursor.execute(sorgu, degerler)

        if cursor.rowcount == 0:
            print(f"⚠️ Hata: ID {urun_id} bulunamadığı için silinemedi.")
        else:
            cnn.commit()
            print(f"✅ Ürün ID: {urun_id} envanterden başarıyla silindi.")

    except mysql.connector.Error as err:
        print(f"❌ Hata: Ürün silinemedi: {err}")
        cnn.rollback()

    finally:
        cursor.close()
        cnn.close()

# ==========================================================================
# 🚀 ANA UYGULAMA MENÜSÜ
# ==========================================================================

def main():
    """Uygulamanın ana menüsü."""
    # Uygulama başladığında veritabanı ve tabloyu hazırla
    veritabani_ve_tablo_olustur()

    while True:
        print("\n" + "="*35)
        print("       🛒 ENVANTER YÖNETİMİ (CRUD)")
        print("="*35)
        print("1. Ürün Ekle (Create) ➕")
        print("2. Ürünleri Listele (Read) 🔎")
        print("3. Ürün Güncelle (Update) ✏️")
        print("4. Ürün Sil (Delete) 🗑️")
        print("5. Çıkış 🚪")
        print("-" * 35)

        secim = input("Lütfen bir işlem seçin (1-5): ")

        if secim == '1':
            print("\n--- Yeni Ürün Ekle ---")
            urun_adi = input("Ürün Adı: ")
            aciklama = input("Açıklama: ")
            try:
                stok_miktari = int(input("Stok Miktarı: "))
                fiyat = float(input("Fiyat (Örn: 150.50): "))
                urun_ekle(urun_adi, aciklama, stok_miktari, fiyat)
            except ValueError:
                print("⚠️ Hata: Stok ve Fiyat sayı olmalıdır.")

        elif secim == '2':
            envanteri_goster()

        elif secim == '3':
            print("\n--- Ürün Güncelle ---")
            try:
                envanteri_goster() # Güncellemeden önce mevcut listeyi göster
                urun_id = int(input("Güncellenecek Ürün ID'si: "))
                yeni_stok = int(input("Yeni Stok Miktarı: "))
                yeni_fiyat_input = input("Yeni Fiyat (Boş bırakmak için Enter): ")
                yeni_fiyat = float(yeni_fiyat_input) if yeni_fiyat_input else None
                urun_guncelle(urun_id, yeni_stok, yeni_fiyat=yeni_fiyat)
            except ValueError:
                print("⚠️ Hata: ID, Stok veya Fiyat hatalı formatta.")

        elif secim == '4':
            print("\n--- Ürün Sil ---")
            try:
                envanteri_goster() # Silmeden önce mevcut listeyi göster
                urun_id = int(input("Silinecek Ürün ID'si: "))
                urun_sil(urun_id)
            except ValueError:
                print("⚠️ Hata: ID sayı olmalıdır.")

        elif secim == '5':
            print("Uygulamadan çıkılıyor. Güle güle! 👋")
            break

        else:
            print("Geçersiz seçim. Lütfen 1 ile 5 arasında bir sayı girin.")

if __name__ == "__main__":
    main()