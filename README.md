# 🔗 ERPNext ↔ LOGO Tiger Entegrasyonu

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ERPNext](https://img.shields.io/badge/ERPNext-v14+-orange)](https://erpnext.com)
[![LOGO Tiger](https://img.shields.io/badge/LOGO-Tiger%20Family-red)](https://www.logo.com.tr)
[![Python](https://img.shields.io/badge/Python-3.10+-green)](https://www.python.org)

> **Türkiye'nin ilk açık kaynak ERPNext - LOGO Tiger entegrasyon çözümü**  
> Üretim firmaları için iki yönlü stok, cari, sipariş ve fatura senkronizasyonu + e-Fatura/e-İrsaliye desteği

---

## 🎯 Neden Bu Entegrasyon?

**90% daha az manuel iş**  
Stok, müşteri ve fatura verilerini elle girmek yerine otomatik senkronizasyon

**e-Fatura/e-İrsaliye hazır**  
GİB uyumluluğu için yerleşik e-belge desteği (BETA)

**Çift yönlü senkronizasyon**  
ERPNext → LOGO ve LOGO → ERPNext, her iki yönde de çalışır

**Üretim firmalarına özel**  
Tekstil, metal işleme, mobilya, savunma sanayii için optimize edilmiş

---

## ⚡ Özellikler

### Şu An Mevcut
- ✅ **Stok Kartları** → Ürün/malzeme otomatik senkronizasyonu
- ✅ **Cari Hesaplar** → Müşteri ve tedarikçi aktarımı
- ✅ **Satış Siparişleri** → ERPNext'ten LOGO'ya sipariş akışı
- ✅ **Satış Faturaları** → Fatura oluşturma ve senkronizasyon
- ✅ **Ödeme Kayıtları** → Tahsilat/ödeme takibi
- ✅ **e-Fatura Entegrasyonu** → GİB'e otomatik e-fatura gönderimi
- ✅ **e-İrsaliye Desteği** → Sevkiyat belgelerinin otomasyonu
  
### Geliştirme Aşamasında
- 🚧 **Stok Hareketleri** → Gerçek zamanlı stok senkronizasyonu
- 🚧 **Fiyat Güncellemeleri** → Otomatik fiyat listesi aktarımı

---

## 🚀 Hızlı Başlangıç

### 1️⃣ Kurulum
```
# ERPNext bench'inizde
bench get-app https://github.com/logedosoft/erpnext-logo-tiger-integration
bench --site siteadı install-app tiger_integration
```

### 2️⃣ Yapılandırma
1. ERPNext'te **LOGO Tiger Ayarları**'na gidin
2. LOGO REST API kimlik bilgilerinizi girin
3. Senkronizasyon yöntemini seçin (Manuel / Otomatik)
4. İlk senkronizasyonu başlatın

### 3️⃣ İlk Kullanım
```
# Senkronizasyon testi
bench --site yoursite.com execute tiger_integration.sync.sync_items
```

📖 **Detaylı kurulum ve kullanım için:** [Wiki sayfalarımıza göz atın](../../wiki)

---

## 🏭 Kimler İçin?

✅ ERPNext kullanan üretim firmaları  
✅ LOGO Tiger/Tiger3/Tiger3 Enterprise kullanan işletmeler  
✅ e-Fatura/e-İrsaliye zorunluluğu olan şirketler  
✅ Manuel veri girişinden kurtulmak isteyen ekipler  
✅ Çift sistem yönetimini otomatikleştirmek isteyen KOBİ'ler

---

## 🛠️ Teknik Detaylar

| Özellik | Açıklama |
|---------|----------|
| **ERPNext Versiyonu** | v14, v15 (önerilen) |
| **LOGO Ürünleri** | Tiger, Tiger3, Tiger3 Enterprise, TigerWings |
| **API** | LOGO REST API + Logo Object |
| **Dil** | Python 3.10+ |
| **Lisans** | MIT (Ticari kullanıma açık) |
| **Destek** | Türkçe + English |

---

## 📊 Senkronizasyon Özellikleri

### Desteklenen LOGO Tabloları
- `LG_ITEMS` → ERPNext Item
- `LG_CLCARD` → ERPNext Customer/Supplier
- `LG_ORFICHE` → ERPNext Sales Order
- `LG_STFICHE` → ERPNext Sales Invoice
- `LG_PAYLINES` → ERPNext Payment Entry

### Veri Akış Yönleri
```
ERPNext → LOGO Tiger (Ana akış)
LOGO Tiger → ERPNext (Ters senkronizasyon)
İki Yönlü (Otomatik çakışma çözümü)
```

---

## 🤝 Katkıda Bulunun

Bu proje açık kaynak ve topluluk katkılarına açıktır!

**Katkı yapmanın yolları:**
- 🐛 Hata bildirin ([Issues](../../issues))
- 💡 Yeni özellik önerin ([Discussions](../../discussions))
- 📝 Dokümantasyon geliştirin
- 🔧 Pull request gönderin
- ⭐ Projeyi yıldızlayın (takip etmek için)

[Katkı Rehberi](CONTRIBUTING.md) • [Geliştirici Dokümantasyonu](../../wiki/Development)

---

## 📞 Destek & İletişim

### Sorularınız mı var?

- 📧 **E-posta:** [support@logedo.com](mailto:support@logedo.com)
- 💬 **GitHub Discussions:** [Sorularınızı sorun](../../discussions)
- 🐛 **Hata Bildirimi:** [Talep açın](../../issues/new)
- 🌐 **Web:** [logedo.com](https://logedo.com)
- 🌐 **Web:** [logedosoft.com](https://logedosoft.com)

### Topluluk

- 🇹🇷 **ERPNext Türkiye:** [discuss.frappe.io](https://discuss.frappe.io)
- 💼 **LinkedIn:** [@logedosoft](https://linkedin.com/company/logedosoft)

---

## 📋 Yol Haritası

### ✅ 2024 Q4 (Tamamlandı)
- Temel LOGO Tiger bağlantısı
- Stok kartı senkronizasyonu
- Cari hesap aktarımı

### 🎯 2025 Q1 (Aktif Geliştirme)
- e-Fatura/e-İrsaliye entegrasyonu
- Otomatik senkronizasyon zamanlayıcı
- Hata yönetimi ve log sistemi
- Çoklu şirket desteği

### 🔮 2025 Q2 (Planlanan)
- LOGO Zirve entegrasyonu (ayrı repo)
- Mikro Muhasebe entegrasyonu (ayrı repo)
- Gelişmiş raporlama
- Mobil bildirimler

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında lisanslanmıştır.

**Özet:** Ticari kullanım ✅ • Değiştirme ✅ • Dağıtım ✅ • Özel kullanım ✅

---

## 🌟 Projeyi Beğendiniz mi?

GitHub'da ⭐ vererek destekleyebilirsiniz!

```
# Hızlı clone
git clone https://github.com/logedosoft/erpnext-logo-tiger-integration.git
```

---

<div align="center">

**[Logedo](https://logedo.com) tarafından geliştirilmiştir 🇹🇷**

Açık kaynak ERP çözümleri ile Türk sanayisine güç veriyoruz

[🌐 Website](https://logedo.com) • [📧 İletişim](mailto:info@logedo.com) • [💼 LinkedIn](https://linkedin.com/company/logedosoft)

</div>
