# Vision Controlled Jump Game

Gerçek zamanlı bilgisayarlı görü ile kontrol edilen, jest tabanlı bir 2D oyun projesi.
Bu çalışma, kamera akışının işlenmesinden oyun fiziğine kadar uçtan uca bir gerçek zamanlı sistem geliştirerek Computer Vision ve Game Development disiplinlerini bir araya getirir.

## Kullanılan Teknolojiler

- **Python**
  - Projenin ana geliştirme dili
  - Oyun mantığı, jest kuralları ve modüler yapı yönetimi

- **OpenCV**
  - Kamera akışını alma ve frame işleme
  - `BGR -> RGB` dönüşümü ve Pygame uyumlu görüntü hazırlığı

- **MediaPipe Hands**
  - El landmark tespiti (21 nokta)
  - Jest kurallarının (tek parmak / açık el) landmark koordinatlarıyla çıkarımı

- **Pygame**
  - Oyun döngüsü ve sahne yönetimi
  - Sprite çizimi, animasyon frame güncelleme, çarpışma ve HUD

- **Pathlib + OOP yaklaşımı**
  - Varlık dosyalarının platformdan bağımsız yönetimi
  - `Player`, `Pipe`, `HandTracker`, `GestureDetector` gibi ayrık sorumluluklara sahip sınıflar

Bu proje ile gerçek zamanlı görüntü işleme, durum bazlı oyun akışı (state machine), mask tabanlı çarpışma kontrolü ve kullanıcı etkileşimi odaklı UI geliştirme becerilerimi uyguladım.

## Project Snapshot

- **Proje tipi:** Computer Vision + Game Development
- **Rol:** Solo Developer
- **Temel teknoloji:** Python, OpenCV, MediaPipe Hands, Pygame
- **Kontrol modeli:** Kamera tabanlı el jestleri

## Ne Yapar?

- Tek parmak jesti ile oyunu başlatır / yeniden başlatır.
- Açık el jesti ile karakterin zıplamasını tetikler.
- Gerçek zamanlı engel üretimi, çarpışma kontrolü ve skor takibi yapar.
- Start / Playing / Dying / Game Over akışlarını yönetir.

## Teknik Öne Çıkanlar

- **Real-time hand tracking:** MediaPipe ile landmark çıkarımı
- **Rule-based gesture detection:** Landmark konumlarına göre jest kuralları
- **State-driven game loop:** Durum bazlı ekran ve davranış yönetimi
- **Pixel-accurate collision:** Mask tabanlı çarpışma kontrolü
- **Asset pipeline:** Kuş, boru ve ölüm animasyon frame yönetimi

## Görsel Üretim (Pixel Art)

- Kuş animasyon sprite'ları **Piskel** kullanılarak kendim oluşturdum.
- Oyun içindeki sarmaşık/engel çizimlerini (**pipe assets**) yine **Piskel** ile kendim oluşturdum.

## Mimari

- `main.py` → oyun döngüsü, ekranlar, state yönetimi, HUD
- `hand_tracker.py` → kamera frame işleme ve landmark üretimi
- `gesture_detector.py` → jest kuralları (`is_one_finger`, `is_hand_open`)
- `game_logic.py` → `Player` ve `Pipe` sınıfları, fizik/animasyon/çarpışma
- `Assets/` → oyun görselleri

## Kurulum

### Gereksinimler

- Python 3.10+
- Webcam

### Adımlar

1. Repo'yu klonla:

`git clone https://github.com/AynurAltintas/vision-controlled-jump-game.git`

2. Klasöre gir:

`cd vision-controlled-jump-game`

3. (Önerilen) Sanal ortam oluştur:

`python -m venv .venv`

4. Sanal ortamı aktive et (PowerShell):

`.venv\Scripts\Activate.ps1`

5. Bağımlılıkları yükle:

`pip install pygame opencv-python mediapipe`

## Çalıştırma

`python main.py`

## Kontroller

- **Start / Restart:** Tek parmak
- **Jump:** Açık el (3+ parmak)

## Geliştirme Notları

- Aydınlatma ve kamera açıları jest algı kalitesini doğrudan etkiler.
- Start/Game Over ekranları minimal UI yaklaşımıyla optimize edilmiştir.
