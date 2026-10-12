# modules/qsl.py
import os
import requests
from PIL import Image, ImageDraw, ImageFont

# Konfigurasi File
TEMPLATE_PATH = "template.jpg"
FONT_PATH = "arial.ttf"  # Sesuaikan dengan font di folder Anda (opsional)


def edit_foto_template(from_call):
    """Membuka background, menambahkan callsign bot berkotak di kiri atas,

    teks hitam di atas kotak bawah, dan callsign pengirim di kotak hitam bawah.
    """
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: File {TEMPLATE_PATH} tidak ditemukan!")
        return None

    # Buka gambar background dan ubah ke mode RGBA
    base_img = Image.open(TEMPLATE_PATH).convert("RGBA")
    width, height = base_img.size

    # Layer transparan untuk menggambar
    overlay = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # 1. Menyiapkan Ukuran Font secara Proporsional
    try:
        font_besar = ImageFont.truetype(FONT_PATH, int(height * 0.065))
        font_sedang = ImageFont.truetype(FONT_PATH, int(height * 0.045))
        font_kecil = ImageFont.truetype(FONT_PATH, int(height * 0.035))
    except Exception:
        font_besar = ImageFont.load_default()
        font_sedang = ImageFont.load_default()
        font_kecil = ImageFont.load_default()

    # ==========================================
    # 2. CALLSIGN BOT DENGAN KOTAK HITAM DI KIRI ATAS
    # ==========================================
    teks_bot = "YD3ADB-1"
    bbox_bot = draw.textbbox((0, 0), teks_bot, font=font_kecil)
    bot_w = bbox_bot[2] - bbox_bot[0]
    bot_h = bbox_bot[3] - bbox_bot[1]

    # Padding dan Posisi Kotak Bot (Kiri Atas)
    pad_bot_x = int(width * 0.02)
    pad_bot_y = int(height * 0.01)

    bot_box_x1 = int(width * 0.03)  # Jarak dari kiri
    bot_box_y1 = int(height * 0.03)  # Jarak dari atas
    bot_box_x2 = bot_box_x1 + bot_w + (pad_bot_x * 2)
    bot_box_y2 = bot_box_y1 + bot_h + (pad_bot_y * 2)

    # Gambar Kotak Hitam Kiri Atas
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(
            [bot_box_x1, bot_box_y1, bot_box_x2, bot_box_y2],
            radius=8,
            fill=(0, 0, 0, 220),
        )
    else:
        draw.rectangle(
            [bot_box_x1, bot_box_y1, bot_box_x2, bot_box_y2], fill=(0, 0, 0, 220)
        )

    # Tulis Teks Callsign Bot (Warna Putih)
    bot_text_x = bot_box_x1 + pad_bot_x
    bot_text_y = bot_box_y1 + pad_bot_y - bbox_bot[1]
    draw.text(
        (bot_text_x, bot_text_y), teks_bot, fill=(255, 255, 255, 255), font=font_kecil
    )

    # ==========================================
    # 3. KOTAK HITAM & CALLSIGN PENGIRIM DI TENGAH BAWAH
    # ==========================================
    teks_callsign = from_call.upper()
    bbox_cs = draw.textbbox((0, 0), teks_callsign, font=font_besar)
    cs_w = bbox_cs[2] - bbox_cs[0]
    cs_h = bbox_cs[3] - bbox_cs[1]

    padding_x = int(width * 0.04)
    padding_y = int(height * 0.015)
    box_w = cs_w + (padding_x * 2)
    box_h = cs_h + (padding_y * 2)

    # Posisi Kotak Hitam Bawah
    box_x1 = (width - box_w) // 2
    box_y1 = height - box_h - int(height * 0.08)  # 8% dari batas bawah
    box_x2 = box_x1 + box_w
    box_y2 = box_y1 + box_h

    # Gambar Kotak Hitam Bawah
    if hasattr(draw, "rounded_rectangle"):
        draw.rounded_rectangle(
            [box_x1, box_y1, box_x2, box_y2],
            radius=10,
            fill=(0, 0, 0, 220),
        )
    else:
        draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=(0, 0, 0, 220))

    # Tulis Callsign Pengirim (Warna Putih)
    cs_x = box_x1 + padding_x
    cs_y = box_y1 + padding_y - bbox_cs[1]
    draw.text((cs_x, cs_y), teks_callsign, fill=(255, 255, 255, 255), font=font_besar)

    # ==========================================
    # 4. TULISAN HITAM DI SEDIKIT ATAS KOTAK HITAM
    # ==========================================
    teks_tengah = "halo dari informatika ukdc"
    bbox_tengah = draw.textbbox((0, 0), teks_tengah, font=font_sedang)
    teks_tengah_w = bbox_tengah[2] - bbox_tengah[0]
    teks_tengah_h = bbox_tengah[3] - bbox_tengah[1]

    # Posisi horizontal Rata Tengah (Center)
    pos_tengah_x = (width - teks_tengah_w) // 2
    # Posisi vertikal diletakkan sedikit di atas Kotak Hitam Bawah
    pos_tengah_y = box_y1 - teks_tengah_h - int(height * 0.025)

    # Tulis Pesan (Warna Hitam R=0, G=0, B=0)
    draw.text(
        (pos_tengah_x, pos_tengah_y),
        teks_tengah,
        fill=(255, 255, 255, 255),
        font=font_sedang,
    )

    # Gabungkan layer background dan overlay
    final_img = Image.alpha_composite(base_img, overlay).convert("RGB")

    # Simpan hasil sementara
    nama_file_hasil = f"hasil_{from_call}.jpg"
    final_img.save(nama_file_hasil, "JPEG", quality=90)
    return nama_file_hasil


def upload_ke_cloud(file_path):
    """Upload gambar ke Catbox.moe (Permanen & Direct Link)."""
    try:
        url = "https://catbox.moe/user/api.php"
        data = {"reqtype": "fileupload"}
        with open(file_path, "rb") as file:
            files = {"fileToUpload": file}
            response = requests.post(url, data=data, files=files)

        if response.status_code == 200:
            direct_url = response.text.strip()
            return direct_url
        else:
            print(f"Gagal upload, status: {response.status_code}")
    except Exception as e:
        print(f"Gagal upload gambar ke Catbox: {e}")

    return None


def handle_command(from_call="GUEST"):
    """Fungsi utama yang dipanggil oleh main.py."""
    print(f"Memproses gambar untuk {from_call}...")

    file_hasil = edit_foto_template(from_call)

    if not file_hasil:
        return "Gagal: File template.jpg tidak ditemukan."

    url_gambar = upload_ke_cloud(file_hasil)

    # Hapus file temporary lokal
    if os.path.exists(file_hasil):
        os.remove(file_hasil)

    if url_gambar:
        return f"Gambar {from_call}: {url_gambar}"
    else:
        return f"Maaf {from_call}, gagal membuat/mengunggah gambar."