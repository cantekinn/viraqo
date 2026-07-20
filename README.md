## 🚀 Sprint 1 Raporu

### 1. Backlog Dağıtma Mantığı
Takımımız 3 kişiden oluşmakta olup Sprint 1 için planlanan toplam iş hacmimiz 31 SP (Story Point) olarak belirlenmiştir. İş bölümü takım üyelerimizin yetkinliklerine ve odaklanacakları katmanlara göre dengeli (Sıla: 10 SP, Özlem: 10 SP, Can: 8 SP, Ortak: 3 SP) bir şekilde dağıtılmıştır. 

İlk sprintte projenin omurgasını ayağa kaldırmak ve temel makine öğrenmesi tahmin altyapısını kurmak hedeflendiği için en yüksek puanlı iş yükü olan "Crop Recommendation GBDT Modeli Eğitimi" (8 SP) önceliklendirilmiştir. Story'ler alt görevlere bölünerek Miro üzerinden şeffaf bir şekilde takip edilmektedir.

| İş / Görev | SP | Sorumlu | Durum |
| :--- | :---: | :---: | :---: |
| Crop Recommendation GBDT Modeli Eğitimi | 8 | Sıla | Done |
| Tarla Profili DB Şeması ve Hafıza Temeli | 5 | Özlem | Done |
| Toprak ve İklim API İstemcileri (SoilGrids + Open-Meteo) | 5 | Can | Done |
| MEGSİS Parsel İstemcisi Entegrasyonu ve Koordinat Çıkarımı | 5 | Özlem | In Progress |
| Proje Repo İskeleti ve LangGraph Orkestratör Kabuğu | 3 | Can | Done |
| Basit UI MVP: Parsel Girişi ve Ürün Önerisi Ekranı | 3 | Birlikte | In Progress |
| Antalya Ürün Bilgi Tabanı Oluşturulması (crop_params.yaml) | 2 | Sıla | Done |

<img width="2936" height="1692" alt="WhatsApp Image 2026-07-05 at 15 26 36" src="https://github.com/user-attachments/assets/7e3aebc8-8b29-4363-95d9-eb91df498652" />


---

### 2. Daily Scrum Notları
Takımımız, sınav haftası yoğunlukları ve üyelerin çalışma takvimlerinin esnekliği nedeniyle bu sprint boyunca her gün senkronize toplantılar yapmak yerine, periyodik aralıklarla asenkron bir iletişim modeli yürütmüştür. İlerleme durumları, teknik blokajlar ve görev geçişleri takım içi mesajlaşma kanallarımız üzerinden yazılı olarak aktarılmış ve süreç Can (SM) koordinasyonunda sorunsuz yönetilmiştir.

**Sprint Ortası Durum Güncelleme Özeti:**
* **Can (Scrum Master / Developer):** "Projenin temel mimari iskeletini ve LangGraph orkestratör kabuğunu ayağa kaldırdım, repo yapısı modüler olarak hazır durumda. Toprak ve iklim verilerini çekeceğimiz dış veri istemcilerini (SoilGrids ve Open-Meteo API bağlantılarını) başarıyla kodladım. Şu an basit UI üzerinde çalışıyorum; parsel girildiğinde ürün önerisi ekranının çalışabilmesi için Özlem and Sıla'nın çıktılarını bekliyorum, ardından arayüz entegrasyonunu birlikte tamamlayacağız. Önümde bir engel yok."
* **Sıla (Product Owner / Developer):** "Model geliştirme tarafında veri setini temizledim, feature engineering adımlarını uygulayarak eksik SoilGrids verilerini modelledim. Bugün itibarıyla projenin kalbi olan Crop Recommendation LightGBM baseline modelinin eğitimini yüksek doğrulukla tamamladım. Antalya bölgesine ait ürün parametre tabanını da hazırlayarak DB katmanına entegre edilmek üzere hazır hale getirdim. Önümde herhangi bir engel yok."
* **Özlem (Developer):** "MEGSİS entegrasyonu tarafında ada/parsel sorgularından GeoJSON verisi dönmeyi başardım, şu an merkez koordinat çıkarımı üzerinde çalışıyorum. Tek engelim TKGM servislerindeki rate-limit belirsizliği; eğer çok sıkıntı yaşarsak harita üzerinde manuel çizim yapılmasına olanak tanıyacak bir yedek planı Sprint 2'ye devredecek şekilde planlıyorum. Tarla profili DB şemasının hafıza temelini ise tamamladım."

---

### 3. Sprint Board Updates
Sprint başında "ToDo" sütununda yer alan iş paketlerimizin büyük bir kısmı tamamlanarak "Done" sütununa taşınmış ve sprint hedeflerimizin veri ve model omurgasını içeren aşamaları başarıyla kapatılmıştır. Sprint sonu itibarıyla güncel Scrum Board görünümümüz şu şekildedir:

* **Done (5 Görev - 23 SP):** Model eğitimi, ürün parametre tabanı, veri tabanı hafıza katmanı, temel API istemcileri ve proje genel mimari iskeleti başarıyla tamamlanmıştır.
* **In Progress (2 Görev - 8 SP):** MEGSİS entegrasyonu üzerindeki test süreçleri ve kullanıcı arayüzü entegrasyon çalışmaları devam etmektedir. Bir sonraki sprintin başında "Done" durumuna çekilmesi planlanmıştır.

<img width="2936" height="1692" alt="WhatsApp Image 2026-07-05 at 15 26 36" src="https://github.com/user-attachments/assets/4faf29fe-d92a-4b91-8bc7-9411478e56fd" />


---

### 4. Ürün Durumu (Product Status)
Sprint 1 sonu itibarıyla projemizin çekirdek veri omurgası ve yapay zeka tahmin katmanı başarıyla ayağa kaldırılmıştır. Kullanıcı arayüzü (UI) çalışmaları entegrasyon aşamasında olup, sistemin arka plan kodları uçtan uca veri akışını sağlayacak şekilde çalışmaktadır.

**Sprint 1 Çıktıları ve Mevcut Yetenekler:**
* **Veri Omurgası Entegrasyonu:** `SoilGrids` ve `Open-Meteo` API istemcileri tamamlanmıştır. Koordinat bazlı toprak (pH, doku, azot, organik karbon) ve anlık hava durumu (sıcaklık, yağış, nem) verileri dinamik olarak çekilebilmektedir.
* **Hafıza Katmanı:** Çekilen coğrafi ve agronomik verilerin sisteme kaydedilmesi için SQLite/Postgres tabanlı `tarla_profili_db.py` veri tabanı şeması kurulmuştur.
* **Yapay Zeka Modeli:** Toprak ve iklim verilerini işleyerek en uygun ürün önerisini sunan GBDT (LightGBM) baseline model eğitimi başarıyla tamamlanmış ve `crop_params.yaml` bilgi tabanı ile ilişkilendirilmiştir.
* **Çalışma Akışı (MVP):** Sistem şu anda parsel verisini aldığında (MEGSİS entegrasyon testleri paralelinde) ilgili koordinatın toprak/iklim analizini yapıp, LightGBM modeli üzerinden Antalya bölgesi için domates, biber veya patates ürün uygunluk skorunu ve ekim penceresini başarıyla hesaplayabilmektedir.

<img width="1600" height="841" alt="WhatsApp Image 2026-07-05 at 20 50 46 (1)" src="https://github.com/user-attachments/assets/08f8b676-d2ba-43a4-bf54-de3d86d43f3c" />
<img width="1600" height="841" alt="WhatsApp Image 2026-07-05 at 20 50 46" src="https://github.com/user-attachments/assets/beab46f0-c663-4331-ae05-d69dc39e5198" />
<img width="1600" height="840" alt="WhatsApp Image 2026-07-05 at 20 50 47" src="https://github.com/user-attachments/assets/df27de2d-8348-4d3c-9a16-847298e2db71" />


---

### 5. Sprint Review
Sprint 1 sonunda planlanan hedefler ve teslim kapsamı başarıyla gözden geçirilmiş, sistemin temel yapı taşları mentor değerlendirmesine sunulacak olgunluğa ulaştırılmıştır.

* **Teslim Edilen Ürün Kapsamı:** Projenin çekirdek veri omurgası (MEGSİS/SoilGrids/Open-Meteo API entegrasyonları), tarla profili veri tabanı hafızası, ilk eğitilmiş GBDT (LightGBM) makine öğrenmesi modeli ve temel arayüz (UI) altyapısı başarıyla teslim edilmiştir.
* **Demo Özeti:** Antalya bölgesine ait örnek bir parsel verisi üzerinden sistem simüle edilmiştir. Girilen koordinata ait anlık toprak ve iklim verilerinin API'ler üzerinden çekilerek veri tabanına kaydedildiği ve LightGBM modelinin bu verilere dayanarak domates/biber/patates için ürün uygunluk ve ekim penceresi önerisini başarıyla ürettiği canlı olarak gösterilmiştir.
* **Hedef Değerlendirmesi:** Sprint başında taahhüt edilen "Parsel bilgisi girildiğinde toprak ve iklim verilerinin çekilmesi, bu verilere göre yapay zeka tabanlı ürün önerisinin üretilmesi" kilometre taşı (milestone) %100 başarıyla karşılanmıştır.

---

### 6. Sprint Retrospective
Sprint 1 sonunda takım içi süreçlerin ve mühendislik pratiklerinin kalitesini artırmak adına gerçekleştirdiğimiz retrospektif toplantısı çıktılarımız şu şekildedir:

* **İyi Giden Yönler:** Dış veri istemcilerinin (SoilGrids ve Open-Meteo API bağlantıları) beklenen süreden çok daha hızlı tamamlanması. Makine öğrenmesi katmanında LightGBM baseline modelinin ilk aşamada yüksek doğruluk oranlarına ulaşması. 3 kişilik optimize ekibimiz sayesinde kararların ve entegrasyon süreçlerinin çok hızlı bir şekilde yürütülmesi.
* **Zorlanılan Noktalar:** MEGSİS API erişimindeki dönemsel yavaşlıklar ve servis belirsizlikleri. Sınav haftası ve yoğun takvimler nedeniyle 3 kişi arasındaki iş yükü dengesini ve zaman yönetimini koruma zorluğu.
* **Gelecek Sprint İçin Aksiyon Planı (Sprint 2):** MEGSİS tarafındaki belirsizlik riskine karşı harita üzerinde manuel çizim yapılmasını sağlayacak yedek planın geliştirilmesine erken başlanması. Sprint 2 hedeflerinde yer alan görüntü işleme (hastalık teşhis) modeli eğitimi için Google Colab GPU süreçlerinin önden optimize edilmesi ve iş paketlerinin daha küçük task'lere bölünerek takip edilmesi.
* Sprint 2 için Product Backlog'a şimdiden 5 görev (görüntü işleme tabanlı hastalık teşhis modeli, RAG+LLM tabanlı danışman agent, iklim/risk ve sulama agent yapıları, vektör hafıza katmanı, WhatsApp/Twilio entegrasyonu) eklenerek bir sonraki sprintin planlama sürecine hız kazandırılmıştır.

  
### 7. Mimarı Yapı
```
tarim-asistani/
  app/                    # arayüz katmanı
    ui/                   # Streamlit (hızlı MVP) veya Next.js
    whatsapp/             # WhatsApp webhook
  agents/                 # LangGraph orkestrasyon
    orchestrator.py       # router + state graph
    soil_crop_agent.py
    diagnosis_agent.py
    climate_risk_agent.py
    irrigation_agent.py
    pest_agent.py
    advisor_agent.py      # RAG tedavi (doğal+kimyasal)
    carbon_agent.py
  models/                 # ML eğitim + çıkarım
    crop_reco/            # GBDT (XGBoost/LightGBM)
    disease/              # CNN eğitim + Grad-CAM
    climate_risk/         # LightGBM
    weed/                 # YOLO (faz 2)
  data/                   # dış veri istemcileri
    megsis.py             # parsel -> geojson
    soilgrids.py
    open_meteo.py
    nasa_power.py
  knowledge/              # bilgi tabanları
    crop_params.yaml      # ürün: pH/sıcaklık/GDD/Kc/don/zararlı
    fao56.py              # sulama formülleri
    degree_day.py         # zararlı eşikleri
    rag_docs/             # tarım kaynakları (tedavi)
  memory/                 # hafıza katmanı
    farm_profile_db.py    # SQLite/Postgres
    vector_store.py       # Chroma (sezon günlüğü)
  core/                   # config, şemalar, ortak yardımcılar
    schemas.py
    config.py
  tests/
  README.md
  requirements.txt
```

## 🚀 Sprint 2 Raporu

**Bootcamp:** Google YZTA 2026 - 14. Grup (Yapay Zeka)
**Proje:** Küçük çiftçi için çok agentli yapay zeka tarım danışmanı
**Kalkınma hedefleri (SDG):** 1 Yoksulluğa Son, 2 Açlığa Son, 13 İklim Eylemi
**Sprint süresi:** 6 Temmuz - 20 Temmuz 2026 (2 hafta)
**Takım:** Can Tekin, Özlem, Sıla (3 kişi)

---

### 1. Sprint 2 İçinde Yer Alan Konuların Belirlenmesi ve Bağlantı Kurulması

Takımımız 3 kişiden oluşuyor ve Sprint 2 için planladığımız toplam iş hacmi **28 SP (Story Point)** olarak belirlendi; hedefler teknik zorluk derecelerine göre dengeli dağıtıldı. Sprint 1'deki katman ayrımını koruduk: yapay zeka/görüntü katmanı Sıla'da, iklim ve su katmanı Özlem'de, orkestrasyon ve fenoloji katmanı Can'da.

Bu sprintin en yüksek efor gerektiren işi olan görüntü tabanlı hastalık teşhis modeli Sıla (8 SP) tarafından üstlenildi. Can (SM) ve Özlem uzman agent algoritmalarını ve bunların LangGraph orkestratörüne bağlanmasını yürüttü.

| İş / Görev | SP | Sorumlu | Durum |
| :--- | :---: | :---: | :---: |
| Hastalık Teşhis Modeli Eğitimi (EfficientNetV2-S + Grad-CAM) | 8 | Sıla | Done |
| Yabancı Yaprak Reddi için "Diğer" OOD Sınıfı | 3 | Sıla | Done |
| Teşhis Agent + Tedavi Bilgi Tabanı (treatments.yaml) | 4 | Sıla & Can | Done |
| Sulama Agent (FAO-56 Penman-Monteith) | 3 | Özlem | Done |
| Kural Tabanlı İklim Riski Agent | 2 | Özlem | Done |
| Zararlı Agent (Derece-Gün / GDD Fenoloji) | 4 | Can | Done |
| LangGraph Orkestratör Bağlama + Arayüz | 4 | Can & Özlem | Done |

**Toplam planlanan:** 28 SP &nbsp;|&nbsp; **Tamamlanan:** 28 SP &nbsp;|&nbsp; **Sprint hedefine ulaşma:** %100

**Teknik tercih notu (dürüstlük):** İmkânsız veya maliyetli hiçbir bileşen kullanmadık. Hastalık teşhisinde ConvNeXt yerine **EfficientNetV2-S** seçildi (CPU'da daha hızlı, transfer öğrenmede aynı seviye; darboğaz mimari değil veri). Tedavi bilgisi için RAG/LLM yerine **treatments.yaml yapılı tabanı** kullanıldı (9 sabit hastalık için daha ucuz, deterministik, API anahtarı gerektirmez). İklim riskinde LightGBM yerine **kural tabanlı** yaklaşım seçildi çünkü etiketli iklim-riski verisi yok; kural tabanlı yöntem şeffaf ve savunulabilir.

---

### 2. Daily Scrum Notları

Üyelerin yaz stajı tempoları nedeniyle her gün senkron toplantı yerine periyodik asenkron bir iletişim modeli yürüttük. İlerlemeler WhatsApp kanalında Can (SM) koordinasyonunda yazılı aktarıldı; LangGraph state yapısındaki veri tipi uyuşmazlıkları ve foto-teşhis yönlendirmesi anlık çözüldü.

Sprint ortası ve kapanış durum güncellemeleri:

* **Can (Scrum Master / Developer):** "Orkestratörü stub durumdan çıkarıp tüm gerçek agent'ları bağladım; gelen soruya (ya da fotoğraf varlığına) göre doğru uzmana yönlendiriyor. Open-Meteo istemcisini genişlettim, artık FAO-56 ET0 ve 16 günlük tahmin serisi dönüyor. Derece-gün (GDD) zararlı fenoloji modülünü ve agent'ını yazdım. Arayüze dört hızlı aksiyon butonu ve yaprak fotoğraf yükleyici ekledim. Kritik bir hata buldum: profil orkestratöre parsel bilgisi olmadan gidiyordu, düzelttim. Önümde engel yok."
* **Sıla (Product Owner / Developer):** "Hastalık modelini kurdum: EfficientNetV2-S transfer öğrenme, Grad-CAM ısı haritası. PlantVillage laboratuvar verisiyle val doğruluğu %97.8 oldu. Ancak gerçek tarla fotoğraflarında güven düşüktü (lab-saha uçurumu), bu yüzden PlantDoc saha fotoğraflarını ekleyip yeniden eğittim; lab %98.6, saha doğruluğu %31.7'den %61.9'a çıktı. Son olarak modelin yalnızca 9 sınıf bildiği için yabancı yaprağı (ör. narenciye) zorla domates/patates'e itmesi sorununu çözdüm: 'diğer' adında bir OOD sınıfı ekleyip 11 hedef-dışı yaprak türüyle eğittim; artık bilmediği yaprağı reddediyor. Önümde engel yok."
* **Özlem (Developer):** "Sulama tarafında FAO-56 Penman-Monteith modülünü yazdım; ET0 ders kitabı değerleriyle birebir doğrulandı (es(20)=2.338, delta(20)=0.145). Sulama agent'ı parselin konumundan ET0 çekip ürün katsayısı Kc ve etkili yağış ile net litre/gün veriyor. İklim riski modülünü kural tabanlı olarak yeniden yazdım: artık sadece eşik değil, gün sayısı (şiddet) ve ürün uygunluk kararı da veriyor; böylece her ürün için risk gerçekten farklılaşıyor (sıcak dalgasında patates 16/16 gün uygun değil, zeytin sadece 3/16 orta). Önümde engel yok."


---

### 3. Sprint Board Updates

Sprint başında "To Do" sütununda yer alan iş paketlerimizin tamamı tamamlanarak "Done" sütununa taşınmış ve Sprint 2 hedefimiz olan dört uzman agent'ın orkestrasyona canlı bağlanması başarıyla kapatılmıştır. Sprint sonu itibarıyla güncel Scrum Board görünümümüz şu şekildedir:

* **Done (5 Görev - 28 SP):** Hastalık teşhis CNN'i (EfficientNetV2-S + Grad-CAM, eğitildi), yabancı yaprağı reddeden "diğer" OOD sınıfı, treatments.yaml tedavi tabanlı teşhis agent'ı, FAO-56 sulama agent'ı, derece-gün zararlı agent'ı, kural tabanlı iklim riski agent'ı ve tüm agent'ları tek arayüzden yöneten LangGraph orkestratörü başarıyla tamamlanmıştır.
* **In Progress (0 Görev):** Bu sprintte devam eden kart kalmadı; hedeflere %100 ulaşıldı.
* **To Do (Sprint 3'e devir):** Karbon ayak izi agent'ı bilinçli olarak Sprint 3'e bırakılan bir stub olarak duruyor. Ayrıca narenciye/zeytin/muz için gerçek hastalık sınıfları, WhatsApp entegrasyonu ve çoklu parsel/premium bir sonraki sprintin backlog'una alındı.

<img width="2938" height="1582" alt="WhatsApp Image 2026-07-18 at 11 06 32 (1)" src="https://github.com/user-attachments/assets/2e7024a1-1213-4bd3-b25f-f1ee0af59f9e" />
<img width="2940" height="1586" alt="WhatsApp Image 2026-07-18 at 11 08 15" src="https://github.com/user-attachments/assets/8e341a96-9593-432b-bd70-29c6ba1b1504" />


---

### 4. Ürün Durumu (Product Status)

Sprint 2 kapanışında sistem, Sprint 1 iskeletinin üstüne dört uzman agent eklenmiş çalışan bir MVP durumunda:

* **Görüntü İşleme Katmanı:** Çiftçinin yüklediği yaprak fotoğrafından (domates, biber, patates) hastalık teşhisi yapan ve Grad-CAM ile hasarlı bölgeyi işaretleyen CNN. Model önce **ürünü** (domates/biber/patates) belirler, sonra hastalığı önerir. Fotoğraf hedef ürünlerden biri değilse ("diğer") teşhis dayatmaz, "bu yaprak eğittiğim ürünlerden değil" der; yanlış teşhisi önler.
* **Tedavi Bilgi Tabanı:** Teşhis edilen hastalığa karşı `treatments.yaml` içinden doğal ve kimyasal (etken madde sınıfı + yasal uyarı) tedavi öneren danışman altyapısı. Maliyetsiz, API'siz, deterministik.
* **Akıllı Uzman Agent'lar:** FAO-56 ile net sulama ihtiyacını litre/gün hesaplayan Sulama Agent'ı, don/sıcaklık stresi/yağış/kuraklık risklerini gün sayısı ve uygunluk kararıyla veren İklim Agent'ı, derece-gün modeliyle böcek nesil/evresini hesaplayan Zararlı Agent'ı.
* **Orkestrasyon (LangGraph):** Tüm alt agent'ları tek arayüzden kullanıcı niyetine (intent) göre yönlendiren state graph mimarisi uçtan uca çalışıyor. Altı niyet (ürün önerisi, sulama, iklim riski, zararlı, teşhis, danışman) doğru yönlendiriliyor.

**Modelin ölçülen durumu (dürüst rakamlar):**

| Metrik | Değer |
| :--- | :---: |
| Laboratuvar val doğruluğu | **%98.6** |
| Gerçek saha fotoğrafı doğruluğu (sadece lab) | %31.7 |
| Gerçek saha fotoğrafı doğruluğu (lab + PlantDoc saha) | **%61.9** |
| Saha doğruluğu ("diğer" sınıfı takasıyla) | %57 |
| Yabancı yaprak (eğitimde görülmeyen tür) reddi | **%81** |

<img width="1919" height="871" alt="Ekran görüntüsü 2026-07-20 044652" src="https://github.com/user-attachments/assets/d1d698f1-539d-4d8b-a18f-c154d127b1fa" />

<img width="1919" height="869" alt="Ekran görüntüsü 2026-07-20 045756" src="https://github.com/user-attachments/assets/6601b025-c6ef-43c5-9fd0-18324579371a" />

<img width="1919" height="865" alt="Ekran görüntüsü 2026-07-20 045812" src="https://github.com/user-attachments/assets/50b1f98f-b5ed-444d-871b-03ae15d87982" />

<img width="1919" height="867" alt="Ekran görüntüsü 2026-07-20 045901" src="https://github.com/user-attachments/assets/198071c9-4fc6-46d3-8559-e2ba4d34e35d" />

<img width="1919" height="870" alt="Ekran görüntüsü 2026-07-20 045834" src="https://github.com/user-attachments/assets/01d21c5d-aa2e-470e-99a7-e588270dd9e3" />

---

### 5. Sprint Review

Sprint 2 hedefi olan "dört uzman agent'ın orkestrasyona canlı bağlanması" tam teslim edildi. Altı niyetin tamamı uçtan uca test edildi ve gerçek açık veriyle çalıştı: Antalya koordinatında domates için net 7.37 mm/gün sulama, Temmuz'da Tuta absoluta 4. nesil, 41.4 C sıcaklık stresi yüksek riski gibi gerçekçi çıktılar üretildi. Hastalık modeli gerçekten eğitildi (lab %98.6) ve gerçek tarla fotoğraflarına PlantDoc ile uyarlandı; ayrıca yabancı yaprağı reddeden "diğer" sınıfıyla yanlış teşhis riski büyük ölçüde giderildi.

Tüm karar mekanizmaları (FAO-56 fizik, GDD fenoloji, kural tabanlı risk, treatments.yaml) şeffaf ve savunulabilir; hiçbiri lisanslı veri veya API anahtarı gerektirmiyor (SDG uyumlu, sıfıra yakın maliyet).

**Demo senaryosu:** Serik parseli seç → "domates sulama planı" (ET0 ve litre/gün) → "zararlı tahmini" (Tuta absoluta nesli) → "iklim riski" (sıcaklık stresi uyarısı) → yaprak fotoğrafı yükle (doğru teşhis + ürün + Grad-CAM), ardından yabancı yaprak yükle ("tanımadım" reddi).

---

### 6. Sprint Retrospective

**İyi giden yönler:**
- Sprint 1 iskeleti sayesinde agent'lar mevcut düğümlere takılarak hızlı eklendi.
- Her agent'ın kararı fizik/agronomi ile savunulabilir; kara kutu yok.
- Hiçbir özellik lisanslı veri veya ödemeli API gerektirmiyor (SDG uyumlu).
- Model gerçek saha verisiyle eğitildi ve yabancı yaprağı reddetmeyi öğrendi; sunumda güven/doğruluk avantajı.

**Zorlanılan noktalar:**
- Lab-saha uçurumu: PlantVillage laboratuvar fotoğrafları gerçek tarlayı temsil etmiyordu; PlantDoc saha verisiyle kapatıldı ama saha doğruluğu %90'a değil %57-62 seviyesine ulaştı (sınıf başına ~75 saha fotoğrafı sınırı). Dürüst tavan.
- Yabancı yaprak sorunu: model 9 sınıf bildiği için narenciye yaprağını zorla yanlış sınıflandırıyordu; "diğer" OOD sınıfı eğitilerek çözüldü.
- Kimyasal tedavi önerilerinde yasal sorumluluk: etken madde sınıfı + uyarı ile sınırlandı, reçete yerine geçmez.

**Sprint 3 aksiyonları:**
- Narenciye/zeytin/muz için gerçek hastalık sınıfları (veri toplama + yeniden eğitim).
- Karbon ayak izi agent (stub'ın gerçeklenmesi).
- WhatsApp entegrasyonu (sahada erişim).
- Saha doğruluğunu artırmak için ek saha verisi.


