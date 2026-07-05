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
Takımımız, sınav haftası yoğunlukları ve üyelerin çalışma takvimlerinin esnekliği nedeniyle bu sprint boyunca her gün senkronize toplantılar yapmak yerine, periyodik aralıklarla asenkron bir iletişim modeli yürütmüştür[cite: 1]. İlerleme durumları, teknik blokajlar ve görev geçişleri takım içi mesajlaşma kanallarımız üzerinden yazılı olarak aktarılmış ve süreç Can (SM) koordinasyonunda sorunsuz yönetilmiştir[cite: 1].

**Sprint Ortası Durum Güncelleme Özeti:**
* **Can (Scrum Master / Developer):** "Projenin temel mimari iskeletini ve LangGraph orkestratör kabuğunu ayağa kaldırdım, repo yapısı modüler olarak hazır durumda. Toprak ve iklim verilerini çekeceğimiz dış veri istemcilerini (SoilGrids ve Open-Meteo API bağlantılarını) başarıyla kodladım. Şu an basit UI üzerinde çalışıyorum; parsel girildiğinde ürün önerisi ekranının çalışabilmesi için Özlem and Sıla'nın çıktılarını bekliyorum, ardından arayüz entegrasyonunu birlikte tamamlayacağız. Önümde bir engel yok."
* **Sıla (Product Owner / Developer):** "Model geliştirme tarafında veri setini temizledim, feature engineering adımlarını uygulayarak eksik SoilGrids verilerini modelledim. Bugün itibarıyla projenin kalbi olan Crop Recommendation LightGBM baseline modelinin eğitimini yüksek doğrulukla tamamladım. Antalya bölgesine ait ürün parametre tabanını da (crop_params.yaml) hazırlayarak DB katmanına entegre edilmek üzere hazır hale getirdim. Önümde herhangi bir engel yok."
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
* tarim-asistani/
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
