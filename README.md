Dijital Bütçe Takibi

Bu proje; Flask, SQLAlchemy ve Bootstrap 5 kullanılarak geliştirilmiş bir kişisel finans ve bütçe yönetim uygulamasıdır.

Kullanıcılar:

Gelir \& gider ekleyebilir

Kategori oluşturabilir

Finans akışını grafiklerle görebilir

Güvenli kullanıcı girişi yapabilir

Dashboard üzerinden bakiye analiz edebilir

\*Kurulum Rehberi

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları uygulayın.

1️-Gerekli Araçların Kurulumu

Bilgisayarınızda şunlar yüklü olmalıdır:

Python 3.10+

Git

(Önerilen) VS Code

Python Kurulumu

->https://python.org

!!Kurulum sırasında “Add Python to PATH” kutucuğunu mutlaka işaretleyin.

Git Kurulumu

->https://git-scm.com

2️-Projeyi Bilgisayara Çekme (Clone)

Terminal açın ve şu komutu yazın:

git clone https://github.com/KULLANICI\_ADIN/dijital-butce-takibi.git



Klasöre girin:

cd dijital-butce-takibi

3️-Sanal Ortam Kurulumu (Virtual Environment)
Windows:
python -m venv venv
venv\\Scripts\\activate

Mac / Linux:
python3 -m venv venv
source venv/bin/activate



Başında (venv) görmelisiniz.

4️-Gerekli Kütüphanelerin Yüklenmesi
pip install -r requirements.txt

5️-Veritabanı Oluşturma

Bu proje SQLite kullanmaktadır.

İlk çalıştırmada tablolar otomatik oluşturulur.

Eğer manuel oluşturmak isterseniz:

with app.app\_context():
db.create\_all()

6️-Uygulama Çalıştırma
python app.py



Tarayıcıda açın:

http://127.0.0.1:5000

\*Özellikler

Kullanıcı Kayıt \& Giriş Sistemi

Şifre Hashleme (Flask-Bcrypt)

Dashboard Finans Özeti

Günlük Gelir-Gider Grafiği

Kategori Bazlı Harcama Analizi

Dark / Light Mode

Responsive Tasarım

\*Kullanılan Teknolojiler

Python

Flask

SQLAlchemy

Bootstrap 5

Chart.js

SQLite

