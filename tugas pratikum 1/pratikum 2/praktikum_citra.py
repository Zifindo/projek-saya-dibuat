

import cv2
import numpy as np
from PIL import Image, ImageGrab
import tifffile
import os, datetime, time

# === 1️⃣ Pengaturan Awal ===
OUT_DIR = "hasil_citra"
os.makedirs(OUT_DIR, exist_ok=True)

DROIDCAM_IP = "192.168.1.5:4747"  

def get_camera_source():
    """Coba pakai webcam laptop dulu, kalau gagal pakai kamera HP (DroidCam)."""
    print("Mencoba koneksi ke kamera laptop...")
    cap = cv2.VideoCapture(0)
    ret, _ = cap.read()
    if ret:
        print("Berhasil menggunakan kamera laptop (index 0).")
        return cap

    print("Kamera laptop tidak terdeteksi. Mencoba koneksi ke DroidCam...")
    cap = cv2.VideoCapture(f"http://{DROIDCAM_IP}/video")
    ret, _ = cap.read()
    if ret:
        print(f"Berhasil terhubung ke kamera HP (DroidCam) di {DROIDCAM_IP}")
        return cap

    print("Tidak ada kamera yang dapat digunakan.")
    return None

cap = get_camera_source()
if cap is None:
    raise Exception("Tidak dapat mengakses kamera!")

print("Tekan [SPACE] untuk mengambil gambar, [ESC] untuk batal.")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Tidak bisa membaca frame dari kamera.")
        break
    cv2.imshow("Tekan SPACE untuk Capture", frame)
    key = cv2.waitKey(1)
    if key == 27:  # ESC
        print("Dibatalkan oleh pengguna.")
        break
    elif key == 32:  # SPACE
        base = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUT_DIR}/{base}_capture.jpg"
        cv2.imwrite(filename, frame)
        print("Gambar berhasil disimpan:", filename)
        break

cap.release()
cv2.destroyAllWindows()

img_bgr = cv2.imread(filename)
gray8 = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

def save_2bit_equiv(gray8, path):
    """Konversi grayscale 8-bit menjadi 2-bit (4 level warna)."""
    levels = 4
    q = (gray8.astype(np.uint16) * (levels - 1) // 255).astype(np.uint8)
    mapped = ((q * 255) // (levels - 1)).astype(np.uint8)
    Image.fromarray(mapped).save(path)
    return mapped

def save_rgb16(img_bgr, path):
    """Konversi ke RGB 16-bit (setiap channel 16-bit)."""
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img16 = (img_rgb.astype(np.uint32) * 257).astype(np.uint16)
    tifffile.imwrite(path, img16)
    return img16

base = os.path.splitext(os.path.basename(filename))[0]
p2 = f"{OUT_DIR}/{base}_2bit.png"
p8 = f"{OUT_DIR}/{base}_gray8.png"
p24 = f"{OUT_DIR}/{base}_rgb24.png"
p16 = f"{OUT_DIR}/{base}_rgb16.tiff"

mapped2 = save_2bit_equiv(gray8, p2)
Image.fromarray(gray8).save(p8)
Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).save(p24)
img16 = save_rgb16(img_bgr, p16)

print("Semua format citra berhasil disimpan di folder:", OUT_DIR)
def analyze(arrs):
    results = {}
    for name, arr in arrs.items():
        res = {}
        h, w = arr.shape[:2]
        res['ukuran (px)'] = f"{w} x {h}"
        res['total piksel'] = h * w
        if arr.ndim == 2:
            res['mean'] = float(np.mean(arr))
            res['std dev'] = float(np.std(arr))
        else:
            res['mean per channel (RGB)'] = tuple(np.mean(arr[:,:,i]) for i in range(3))
        results[name] = res
    return results

hasil = analyze({
    "2-bit": mapped2,
    "8-bit": gray8,
    "24-bit": cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB),
})

print("\nHASIL ANALISIS Citra:")
for k, v in hasil.items():
    print(f"\n=== {k} ===")
    for kk, vv in v.items():
        print(f"{kk}: {vv}")

def get_file_info(path):
    size_kb = os.path.getsize(path) / 1024
    img = cv2.imread(path)
    if img is None:
        return {"file": path, "ukuran": "N/A", "file_size_kb": size_kb}
    h, w = img.shape[:2]
    return {"file": os.path.basename(path), "dimensi": f"{w}x{h}", "file_size_kb": f"{size_kb:.2f} KB"}

print("\nInformasi Ukuran File:")
for f in [p2, p8, p16, p24]:
    info = get_file_info(f)
    print(info)

time.sleep(2)
screenshot_path = f"{OUT_DIR}/{base}_screenshot.png"
screenshot = ImageGrab.grab()
screenshot.save(screenshot_path)
print("\nScreenshot otomatis tersimpan di:", screenshot_path)

print("\nLangkah Selanjutnya:")
print("1. Buka folder 'hasil_citra' untuk melihat semua hasil citra dan screenshot.")
print("2. Buka hasil gambar di aplikasi ImageJ untuk mengatur brightness, kontras, warna, bentuk, dan tekstur.")
print("3. Masukkan hasil screenshot dan analisis ke laporan praktikum.")
