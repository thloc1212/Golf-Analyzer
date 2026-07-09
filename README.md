# Golf Quyt Analyzer

Ung dung phan tich cu swing golf bang computer vision. He thong cho phep upload video swing, trich xuat pose, tinh mot so chi so chuyen dong va du doan handicap band cua nguoi choi.

## Chuc nang chinh

- Upload video swing golf tu giao dien web.
- Xu ly video bang backend Node.js ket hop Python.
- Trich xuat pose va tao video co overlay skeleton.
- Du doan handicap band va tra ve cac chi so nhu swing speed, arm angle.
- Luu pipeline/notebook phuc vu tien xu ly du lieu va huan luyen model trong thu muc `model`.

## Cau truc thu muc

```text
.
+-- dataset/                 # Du lieu video local, khong nen commit len git
+-- model/                   # Notebook, pipeline, ket qua va model training
+-- website/
|   +-- backend/             # Express API + Python video processing
|   +-- frontend/            # React + Vite UI
+-- README.md
```

## Dataset

Dataset duoc luu tren Google Drive:

[Tai dataset tai day](https://drive.google.com/file/d/1An0NDms-Ku354V0mct9fE577wErdFT5I/view?usp=drive_link)

Sau khi tai va giai nen, tao thu muc `model/Public Test` va copy noi dung dataset vao thu muc do:

```bash
model/
+-- Public Test/
    +-- Trong nha - Indoor/
    +-- Ngoai troi - Outdoor/
```

Thu muc `dataset/` o goc repo co the dung de luu ban dataset local. Thu muc nay da duoc them vao `.gitignore` vi video dataset thuong rat nang.

## Yeu cau moi truong

- Node.js 16 tro len
- Python 3.8 tro len
- FFmpeg da cai va nam trong `PATH`
- pip/virtualenv cho Python dependencies

## Cai dat

### 1. Cai backend

```bash
cd website/backend
npm install
python -m venv venv
```

Kich hoat virtual environment:

```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

Cai Python packages:

```bash
pip install -r requirements.txt
```

### 2. Cai frontend

```bash
cd ../frontend
npm install
```

## Chay ung dung

Mo 2 terminal rieng.

Terminal 1 - backend:

```bash
cd website/backend
npm start
```

Backend chay tai `http://localhost:5001`.

Terminal 2 - frontend:

```bash
cd website/frontend
npm run dev
```

Frontend mac dinh chay tai `http://localhost:5173`.

## Cach su dung

1. Mo `http://localhost:5173` tren trinh duyet.
2. Upload video swing golf.
3. Doi backend xu ly video.
4. Xem video ket qua va cac chi so phan tich.

## Ghi chu phat trien

- API phan tich video nam o `POST http://127.0.0.1:5001/analyze`.
- File model chay inference cua backend nam trong `website/backend/models`.
- Backend can file scaler tai `website/backend/processed_videos/features/feature_scaler.json`.
- Pipeline training/tien xu ly nam trong `model/pipeline` va cac notebook trong `model`.
- Khong commit `dataset/`, `node_modules/`, virtualenv, cache Python, file upload tam hoac output video sinh ra.
