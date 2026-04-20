import cv2
import numpy as np

# === Ganti IP sesuai DroidCam di HP ===
ipcam_url = "http://192.168.1.72:4747/video"

print("Mencoba menghubungkan ke kamera...")
cap = cv2.VideoCapture(ipcam_url)

if not cap.isOpened():
    print("Tidak dapat membuka IP Cam.")
    print("Pastikan:")
    print("1. HP dan laptop di WiFi yang sama.")
    print("2. DroidCam sedang berjalan dan menampilkan video di HP.")
    print(f"3. Coba buka di browser: {ipcam_url}")
    exit()

print("Terhubung ke kamera! Tekan 'q' untuk keluar.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal membaca frame.")
        break

    # --- Deteksi warna merah (simulasi infrared) ---
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("Kamera Asli (DroidCam)", frame)
    cv2.imshow("Deteksi Warna Merah (Simulasi Infrared)", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
