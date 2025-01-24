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
ALLOWED_GROUP_ID = int(os.getenv('ALLOWED_GROUP_ID'))  # ID Grup yang diizinkan

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

# Variabel untuk menyimpan jumlah chat per pengguna
user_chat_count = {}

# Event handler untuk pesan baru
@client.on(events.NewMessage)
async def handle_new_message(event):
    global chat_count, today_date, user_chat_count
    
    # Cek apakah pesan diterima hari ini
    message_date = event.date.date()
    
    if message_date == today_date:
        chat_count += 1
        
        # Catat jumlah chat per pengguna
        user_id = event.sender_id
        if user_id in user_chat_count:
            user_chat_count[user_id] += 1
        else:
            user_chat_count[user_id] = 1

        # Tambahkan log untuk chat ID dan chat title untuk debugging
        logger.debug(f"Pesan diterima dari chat ID {event.chat.id} ({event.chat.title if hasattr(event.chat, 'title') else 'Chat Pribadi'})")
        logger.debug(f"Pengirim ID: {user_id}, Pesan: {event.text}")

# Event handler untuk perintah .ck
@client.on(events.NewMessage(pattern=r'^\.ck$'))  # Hanya merespons jika kata kunci adalah ".ck"
async def check_user_info(event):
    try:
        # Batasi akses hanya untuk owner_id
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
            
            # Ambil informasi chat (bisa grup atau pribadi)
            chat_title = event.chat.title if hasattr(event.chat, 'title') else 'Chat Pribadi'
            chat_username = event.chat.username if hasattr(event.chat, 'username') else '-'
            chat_id = event.chat.id

            # Buat pesan hasil
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
        # Batasi akses hanya untuk owner_id dan di grup yang diizinkan
        if event.sender_id != owner_id or event.chat.id != ALLOWED_GROUP_ID:
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

# Event handler untuk perintah .rank
@client.on(events.NewMessage(pattern=r'^\.rank$'))  # Hanya merespons jika kata kunci adalah ".rank"
async def rank_users(event):
    try:
        # Batasi akses hanya untuk owner_id dan di grup yang diizinkan
        if event.sender_id != owner_id or event.chat.id != ALLOWED_GROUP_ID:
            logger.warning(f"Akses ditolak: Pengguna dengan ID {event.sender_id} mencoba mengakses .rank")
            await event.respond("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return
        
        logger.info(f"Perintah .rank digunakan oleh ID {event.sender_id}")
        
        # Periksa apakah ada data pengguna
        if not user_chat_count:
            await event.respond("Belum ada data chat yang tersedia.")
            return
        
        # Urutkan pengguna berdasarkan jumlah chat (descending)
        sorted_users = sorted(user_chat_count.items(), key=lambda x: x[1], reverse=True)
        
        # Ambil 3 pengguna dengan chat terbanyak
        top_users = sorted_users[:3]
        
        # Siapkan pesan hasil
        rank_message = "**Top 3 Pengguna dengan Chat Terbanyak:**\n"
        for idx, (user_id, count) in enumerate(top_users, start=1):
            try:
                # Ambil informasi pengguna
                user = await client.get_entity(user_id)
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                username = f"@{user.username}" if user.username else "Tidak ada username"
                
                # Tambahkan ke pesan hasil
                rank_message += f"{idx}. {full_name} ({username}) - {count} pesan\n"
            
            except Exception as e:
                logger.error(f"Terjadi kesalahan saat mengambil data pengguna dengan ID {user_id}: {e}")
                rank_message += f"{idx}. Pengguna dengan ID {user_id} tidak ditemukan.\n"
        
        # Kirimkan hasilnya
        await event.respond(rank_message)
        logger.info(f"Rank pengguna dikirim ke {event.sender_id}")
        
        # Menghapus perintah setelah dieksekusi
        await event.delete()
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}", exc_info=True)
        await event.respond(f"Terjadi kesalahan saat memproses perintah: {str(e)}")

# Event handler untuk perintah .mute
@client.on(events.NewMessage(pattern=r'^\.mute$'))  # Hanya merespons jika kata kunci adalah ".mute"
async def mute_user(event):
    try:
        # Batasi akses hanya untuk owner_id dan di grup yang diizinkan
        if event.sender_id != owner_id or event.chat.id != ALLOWED_GROUP_ID:
            logger.warning(f"Akses ditolak: Pengguna dengan ID {event.sender_id} mencoba mengakses .mute")
            await event.respond("Anda tidak memiliki izin untuk menggunakan perintah ini.")
            return
        
        logger.info(f"Perintah .mute digunakan oleh ID {event.sender_id}")
        
        # Pastikan perintah ini digunakan untuk reply
        if event.is_reply:
            # Ambil pesan yang direply
            replied_message = await event.get_reply_message()
            logger.debug(f"Pesan yang direply: {replied_message.text}")
            
            # Ambil informasi pengguna dari pesan yang direply
            user = await client.get_entity(replied_message.sender_id)
            logger.debug(f"Data pengguna: {user}")
            
            # Mute pengguna (contoh: set status user menjadi mute)
            # (Jika Anda menggunakan fitur mute di grup, sesuaikan dengan metode mute grup)
            await event.respond(f"{user.first_name} telah dimute.")
        else:
            logger.warning(f"Perintah .mute digunakan tanpa membalas pesan")
            await event.respond("Mohon gunakan perintah `.mute` dengan membalas pesan pengguna yang ingin dimute.")
        
        # Menghapus perintah setelah dieksekusi
        await event.delete()
    
    except Exception as e:
        logger.error(f"Terjadi kesalahan: {e}", exc_info=True)
        await event.respond(f"Terjadi kesalahan saat memproses perintah: {str(e)}")

# Jalankan bot
client.start(phone_number)
client.run_until_disconnected()
