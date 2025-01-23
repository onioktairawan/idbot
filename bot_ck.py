import logging
from telethon import TelegramClient, events
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os

# Muat variabel dari file .env
load_dotenv()

# Ganti dengan data Anda yang diambil dari .env
api_id = int(os.getenv('API_ID'))            # API ID Anda
api_hash = os.getenv('API_HASH')             # API Hash Anda
phone_number = os.getenv('PHONE_NUMBER')     # Nomor Telepon Anda
owner_id = int(os.getenv('OWNER_ID'))        # ID Telegram Anda

# Setup logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Inisialisasi session
client = TelegramClient('my_session', api_id, api_hash)

# Variabel untuk mencatat jumlah chat hari ini
chat_count = 0
today_date = datetime.today().date()

# Zona waktu WIB
wib_tz = pytz.timezone('Asia/Jakarta')

# Event handler untuk pesan baru
@client.on(events.NewMessage)
async def handle_new_message(event):
    global chat_count, today_date
    
    # Cek apakah pesan diterima hari ini
    message_date = event.date.date()
    
    if message_date == today_date:
        chat_count += 1

# Event handler untuk perintah .ck
@client.on(events.NewMessage(pattern=r'^\.ck$'))  # Hanya merespons jika kata kunci adalah ".ck"
async def check_user_info(event):
    try:
        # Batasi akses hanya untuk Anda
        if event.sender_id != owner_id:
            logger.warning(f"Akses ditolak: Pengguna dengan ID {event.sender_id} mencoba mengakses .ck")
            await event.respond("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return
        
        logger.info(f"Perintah .ck digunakan oleh ID {event.sender_id}")
        
        # Pastikan perintah ini digunakan untuk reply
        if event.is_reply:
            # Ambil pesan yang direply
            replied_message = await event.get_reply_message()
            logger.debug(f"Pesan yang direply: {replied_message.text}")
            
            # Ambil informasi pengguna dari pesan yang direply
            user = await client.get_entity(replied_message.sender_id)
            logger.debug(f"Data pengguna: {user}")
            
            # Siapkan informasi pengguna
            user_id = user.id
            username = f"@{user.username}" if user.username else "Tidak ada username"
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            
            logger.info(f"Informasi pengguna: ID {user_id}, Nama {full_name}, Username {username}")
            
            # Buat pesan hasil
            info_message = (
                f"**Informasi Pengguna:**\n"
                f"ID: `{user_id}`\n"
                f"Nama: {full_name}\n"
                f"Username: {username}"
            )
            
            # Kirimkan hasilnya menggunakan respond, bukan reply
            await event.respond(info_message)
            logger.info(f"Informasi pengguna dikirim ke {event.sender_id}")
        
        else:
            logger.warning(f"Perintah .ck digunakan tanpa membalas pesan")
            await event.respond("Mohon gunakan perintah `.ck` dengan membalas pesan anggota yang ingin diperiksa.")
        
        # Menghapus perintah setelah dieksekusi
        await event.delete()
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}", exc_info=True)
        await event.respond(f"Terjadi kesalahan saat memproses perintah: {str(e)}")

# Event handler untuk perintah .ct
@client.on(events.NewMessage(pattern=r'^\.ct$'))  # Hanya merespons jika kata kunci adalah ".ct"
async def check_total_chats(event):
    try:
        # Batasi akses hanya untuk Anda
        if event.sender_id != owner_id:
            logger.warning(f"Akses ditolak: Pengguna dengan ID {event.sender_id} mencoba mengakses .ct")
            await event.respond("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return
        
        logger.info(f"Perintah .ct digunakan oleh ID {event.sender_id}")
        
        # Ambil waktu sekarang di zona WIB
        current_time_wib = datetime.now(wib_tz).strftime('%H:%M')
        
        # Tampilkan total chat yang diterima hari ini beserta jam dan zona waktu WIB
        await event.respond(f"Total chats today: {chat_count} messages. ({current_time_wib} WIB)")
        logger.info(f"Total chats today dikirim ke {event.sender_id}")
        
        # Menghapus perintah setelah dieksekusi
        await event.delete()
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}", exc_info=True)
        await event.respond(f"Terjadi kesalahan saat memproses perintah: {str(e)}")

# Jalankan client
logger.info("Bot-like account is running...")
client.start(phone=phone_number)
client.run_until_disconnected()
