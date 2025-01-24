import logging
from telethon import TelegramClient, events
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
import re  # Impor library untuk ekspresi reguler

# Muat variabel dari file .env
load_dotenv()

# Ganti dengan data Anda yang diambil dari .env
api_id = int(os.getenv('API_ID'))            # API ID Anda
api_hash = os.getenv('API_HASH')             # API Hash Anda
phone_number = os.getenv('PHONE_NUMBER')     # Nomor Telepon Anda
owner_id = int(os.getenv('OWNER_ID'))        # ID Telegram Anda
ALLOWED_GROUP_IDS = [int(group_id) for group_id in os.getenv('ALLOWED_GROUP_IDS').split(',')]  # ID Grup yang diizinkan (sekarang list)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Inisialisasi session
client = TelegramClient('my_session', api_id, api_hash)

# Variabel untuk mencatat jumlah chat hari ini
chat_count = 0
today_date = datetime.today().date()

# Zona waktu WIB
wib_tz = pytz.timezone('Asia/Jakarta')

# Variabel untuk menyimpan jumlah chat per pengguna (di dalam grup yang diizinkan)
user_chat_count = {}

# Kata kunci yang ingin dideteksi
keywords = ['memek', 'naik', 'ser', 'ok', 'pc', 'cpc', 'oke']

# Event handler untuk pesan baru
@client.on(events.NewMessage)
async def handle_new_message(event):
    global chat_count, today_date, user_chat_count
    
    # Cek apakah pesan diterima hari ini dan hanya dari grup yang diizinkan
    if event.chat.id in ALLOWED_GROUP_IDS:
        message_date = event.date.date()
        
        if message_date == today_date:
            chat_count += 1
            
            # Catat jumlah chat per pengguna
            if event.sender_id not in user_chat_count:
                user_chat_count[event.sender_id] = 1
            else:
                user_chat_count[event.sender_id] += 1

            # Tambahkan log untuk chat ID dan chat title untuk debugging
            logger.debug(f"Pesan diterima dari chat ID {event.chat.id} ({event.chat.title if hasattr(event.chat, 'title') else 'Chat Pribadi'})")
            logger.debug(f"Pengirim ID: {event.sender_id}, Pesan: {event.text}")

# Event handler untuk mendeteksi kata kunci baru dan membalas pesan yang mengandung kata kunci
@client.on(events.NewMessage)
async def respond_to_keywords(event):
    try:
        # Hanya merespons di grup yang diizinkan
        if event.chat.id in ALLOWED_GROUP_IDS:
            # Looping untuk setiap kata kunci dan deteksi dengan ekspresi reguler \b<kata_kunci>\b
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', event.raw_text.strip(), re.IGNORECASE):
                    logger.info(f"Kata kunci '{keyword}' terdeteksi dari pengguna {event.sender_id}")
                    if keyword == 'memek':
                        photo_url = "https://i.pinimg.com/236x/1f/c8/24/1fc8244a27f7665e2d694a44665a4d83.jpg"
                        await event.reply(file=photo_url)  # Menggunakan reply untuk membalas pesan yang berisi kata kunci
                    elif keyword == 'naik':
                        await event.reply("NAIK ANJING AJA NAIK ANJING")
                    elif keyword == 'ser':
                        await event.reply("APA, KANGEN SAMA SERPA YA")
                    elif keyword == 'ok':
                        await event.reply("OK")
                    elif keyword == 'pc':
                        await event.reply("MINIMAL CAKEP BARU PC PC")
                    elif keyword == 'cpc':
                        await event.reply("MINIMAL CAKEP BARU PC PC")
                    elif keyword == 'oke':
                        await event.reply("OK")
                    logger.info(f"Respons berhasil dikirim untuk kata kunci '{keyword}'.")
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat merespons kata kunci: {e}", exc_info=True)

# Event handler untuk perintah .rank
@client.on(events.NewMessage(pattern=r'^\.rank$'))
async def rank(event):
    try:
        # Hanya merespons di grup yang diizinkan
        if event.chat.id in ALLOWED_GROUP_IDS:
            # Sort user berdasarkan jumlah chat mereka
            sorted_users = sorted(user_chat_count.items(), key=lambda item: item[1], reverse=True)

            rank_message = "**Ranking Sender Message:**\n"
            for idx, (user_id, message_count) in enumerate(sorted_users, 1):
                user = await client.get_entity(user_id)
                # Cek apakah user memiliki username, jika tidak tampilkan nama depan dan belakang
                if user.username:
                    username = f"@{user.username}"
                else:
                    username = f"{user.first_name} {user.last_name if user.last_name else ''}".strip() or "Tidak ada nama"

                rank_message += f"{idx}. {username} - {message_count} pesan\n"

            await event.respond(rank_message)
            logger.info(f"Informasi ranking berhasil dikirim ke {event.sender_id}")
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan saat menampilkan ranking: {e}", exc_info=True)

# Event handler untuk perintah .ck
@client.on(events.NewMessage(pattern=r'^\.ck$'))
async def check_user_info(event):
    try:
        # Batasi akses hanya untuk owner_id
        if event.sender_id != owner_id:
            logger.warning(f"Akses ditolak: Pengguna dengan ID {event.sender_id} mencoba mengakses .ck")
            await event.respond("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return
        
        # Pastikan perintah ini digunakan untuk reply
        if event.is_reply:
            replied_message = await event.get_reply_message()
            user = await client.get_entity(replied_message.sender_id)
            user_id = user.id
            username = f"@{user.username}" if user.username else "Tidak ada username"
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            
            chat_title = event.chat.title if hasattr(event.chat, 'title') else 'Chat Pribadi'
            chat_username = event.chat.username if hasattr(event.chat, 'username') else '-'
            chat_id = event.chat.id

            info_message = (
                f"**Informasi Pengguna:**\n"
                f"GRUB:\n"
                f"title: {chat_title}\n"
                f"type: {event.chat.__class__.__name__}\n"
                f"username: {chat_username}\n"
                f"ID: {chat_id}\n\n"
                f"YOU:\n"
                f"first name: {user.first_name}\n"
                f"last name: {user.last_name or '-'}\n"
                f"username: {username}\n"
                f"ID: {user_id}"
            )
            await event.respond(info_message)
            logger.info(f"Informasi pengguna dikirim ke {event.sender_id}")
        else:
            await event.respond("Mohon gunakan perintah `.ck` dengan membalas pesan anggota yang ingin diperiksa.")
        await event.delete()
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}", exc_info=True)
        await event.respond(f"Terjadi kesalahan saat memproses perintah: {str(e)}")

# Jalankan bot
client.start(phone_number)
client.run_until_disconnected()
