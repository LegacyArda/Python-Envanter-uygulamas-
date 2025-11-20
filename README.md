# Python-Envanter-uygulamas-
Uygulamayı kullanmak veya çalıştırmak için gerekli kütüpnaleri,Python ve SQL Server'ı kurmalısınız.SQL Server kodları aşağıda belirtilmiştir.Koddaki SQL Bilgileri bana aittir kendi bilgilerinizi girmeniz gereklidir.


CREATE DATABASE envanter_db;
USE envanter_db;

CREATE TABLE urunler (
    id INT AUTO_INCREMENT PRIMARY KEY,
    urun_adi VARCHAR(255) NOT NULL,
    aciklama TEXT,
    stok_miktari INT NOT NULL,
    fiyat DECIMAL(10, 2) NOT NULL,
    eklenme_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
