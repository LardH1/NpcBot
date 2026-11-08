import discord, threading, datetime, asyncio, random, os
from discord import app_commands
from discord.ext import commands
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
bot_ayarlari = {"web_panel_durum": "Aktif", "islem_sonucu": "Sistem hazir ve sunucunuza bagli."}

@app.route('/')
def dashboard():
    uye_sayisi = bot.guilds.member_count if bot.guilds else 0
    sesteki_sayisi = sum(len(c.members) for c in bot.guilds.voice_channels) if bot.guilds else 0
    bot_gecikme = round(bot.latency * 1000) if bot.latency else 0

    html_kod_blogu = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>NpcBot Yönetim Paneli</title>
        <style>
            body { background-color: #111214; color: #dbdee1; font-family: sans-serif; padding: 20px; }
            .panel-container { max-width: 1000px; margin: auto; background: #2b2d31; padding: 25px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); }
            h1 { color: #fff; font-size: 24px; font-weight: bold; margin-bottom: 5px; }
            .subtitle { color: #949ba4; font-size: 14px; margin-bottom: 25px; }
            .section-title { font-size: 13px; text-transform: uppercase; color: #949ba4; font-weight: bold; margin-top: 25px; margin-bottom: 12px; letter-spacing: 0.5px; }
            .btn-grid { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 5px; }
            .btn-custom { padding: 8px 18px; font-weight: 600; border-radius: 5px; font-size: 14px; border: none; cursor: pointer; }
            .btn-green { background-color: #248046; color: white; }
            .btn-red { background-color: #da373c; color: white; }
            .btn-blue { background-color: #5865f2; color: white; }
            .btn-dark-gray { background-color: #4e5058; color: white; }
            .btn-orange { background-color: #faa81a; color: black; }
            .stats-box { background-color: #1e1f22; padding: 15px; border-radius: 5px; margin-top: 15px; border-left: 4px solid #5865f2; }
            .stats-box p { margin: 0; font-size: 14px; color: #b5bac1; line-height: 1.6; }
            .alert-custom { background-color: #35373c; color: #dbdee1; border: none; border-left: 4px solid #248046; margin-bottom: 20px; padding: 12px; border-radius: 4px; }
            .custom-modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.7); }
            .modal-content { background-color: #313338; margin: 15% auto; padding: 20px; border: 1px solid #4e5058; width: 400px; border-radius: 8px; color: white; }
            .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
            .close-btn { color: #aaa; font-size: 24px; font-weight: bold; cursor: pointer; }
            .form-group { margin-bottom: 15px; }
            .form-group label { display: block; margin-bottom: 5px; color: #b5bac1; font-size: 14px; }
            .form-control-custom { width: 100%; padding: 10px; background-color: #1e1f22; color: white; border: 1px solid #3f4147; border-radius: 4px; box-sizing: border-box; }
        </style>
    </head>
    <body>
    <div class="panel-container">
        <h1>☕ NpcBot Yönetim Paneli</h1>
        <p class="subtitle">Aşağıdaki butonlardan istediğin işlemi seç. Açılan form ekranı sadece sana görünür.</p>
        <div class="alert alert-custom">📢 <strong>Sistem Bildirimi:</strong> PAN_BILDIRIM</div>
        
        <div class="section-title">İçerik, Duyuru ve Müzik</div>
        <div class="btn-grid">
            <button class="btn-custom btn-green" onclick="openModal('duyuru')">Duyuru</button>
            <button class="btn-custom btn-green" onclick="openModal('bot-adina-konus')">Bot Adına Konuş</button>
            <button class="btn-custom btn-green" onclick="openModal('embed')">Embed</button>
            <button class="btn-custom btn-blue" onclick="openModal('muzik-oynat')">🎵 Müzik Çal</button>
        </div>
        <div class="section-title">Moderasyon</div>
        <div class="btn-grid">
            <button class="btn-custom btn-red" onclick="openModal('uyar')">Uyar</button>
            <button class="btn-custom btn-red" onclick="openModal('sustur')">Sustur</button>
            <button class="btn-custom btn-red" onclick="openModal('at')">At</button>
            <button class="btn-custom btn-red" onclick="openModal('banla')">Banla</button>
            <button class="btn-custom btn-green" onclick="openModal('ban-ac')">Ban Aç</button>
        </div>
        <div class="section-title">Karantina</div>
        <div class="btn-grid"><button class="btn-custom btn-orange" onclick="openModal('karantina')">Karantina</button></div>
        <div class="section-title">İnceleme ve Araçlar</div>
        <div class="btn-grid">
            <button class="btn-custom btn-blue" onclick="openModal('uye-sicili')">Üye Sicili</button>
            <button class="btn-custom btn-dark-gray" onclick="openModal('susturmayi-kaldir')">Susturmayı Kaldır</button>
            <button class="btn-custom btn-dark-gray" onclick="openModal('uyari-sil')">Uyarı Sil</button>
            <button class="btn-custom btn-dark-gray" onclick="openModal('not-ekle')">Not Ekle</button>
            <button class="btn-custom btn-dark-gray" onclick="openModal('mesaj-temizle')">Mesaj Temizle</button>
        </div>
        <div class="stats-box">
            <p>● PAN_UYE üye • PAN_SES seste • 0 susturulmuş • 0 uyarılı</p>
            <p>● Gecikme: PAN_MSms • Panel: PAN_DURUM 🟢</p>
        </div>
    </div>
    <div id="islemModal" class="custom-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h5 id="modalBaslik" style="margin:0; font-size:18px;">İşlem Formu</h5>
          <span class="close-btn" onclick="closeModal()">&times;</span>
        </div>
        <form action="/panel-islem-tetikleme" method="POST">
            <input type="hidden" name="islem_turu" id="hiddenIslemTuru">
            <div class="form-group">
                <label id="idEtiket">ID Girin:</label>
                <input type="text" name="hedef_id" class="form-control-custom" required>
            </div>
            <div class="form-group">
                <label id="icerikEtiket">Metin:</label>
                <input type="text" name="metin_icerik" class="form-control-custom" value="Panel üzerinden işlem yapıldı.">
            </div>
            <div style="text-align: right; margin-top:20px;">
                <button type="button" class="btn-custom btn-dark-gray" onclick="closeModal()" style="margin-right:5px;">İptal</button>
                <button type="submit" class="btn-custom btn-blue" style="background-color:#5865f2;">Onayla</button>
            </div>
        </form>
      </div>
    </div>
    <script>
        function openModal(action) {
            document.getElementById('hiddenIslemTuru').value = action;
            var modal = document.getElementById('islemModal');
            var baslik = document.getElementById('modalBaslik');
            var idEtiket = document.getElementById('idEtiket');
            var icerikEtiket = document.getElementById('icerikEtiket');
            if(action === 'duyuru' || action === 'bot-adina-konus' || action === 'embed') {
                baslik.innerText = action.toUpperCase() + " Gönderme Menüsü";
                idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Mesaj İçeriği:";
            } else if(action === 'muzik-oynat') {
                baslik.innerText = "🎵 Canlı Ses / Müzik Oynatma Motoru";
                idEtiket.innerText = "Ses Kanalı ID'si:"; icerikEtiket.innerText = "Canlı Müzik / Radyo Stream URL:";
            } else if(action === 'mesaj-temizle') {
                baslik.innerText = "Mesaj Temizleme";
                idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Silinecek Adet:";
            } else {
                baslik.innerText = action.toUpperCase() + " Menüsü";
                idEtiket.innerText = "Kullanıcı ID:"; icerikEtiket.innerText = "Gerekçe / Rol Adı:";
            }
            modal.style.display = "block";
        }
        function closeModal() { document.getElementById('islemModal').style.display = "none"; }
    </script>
    </body>
    </html>
    """
    html_kod_blogu = html_kod_blogu.replace("PAN_BILDIRIM", bot_ayarlari['islem_sonucu'])
    html_kod_blogu = html_kod_blogu.replace("PAN_UYE", str(uye_sayisi))
    html_kod_blogu = html_kod_blogu.replace("PAN_SES", str(sesteki_sayisi))
    html_kod_blogu = html_kod_blogu.replace("PAN_MS", str(bot_gecikme))
    html_kod_blogu = html_kod_blogu.replace("PAN_DURUM", bot_ayarlari['web_panel_durum'])
    return render_template_string(html_kod_blogu)
@app.route('/panel-islem-tetikleme', methods=['POST'])
def panel_islem_tetikleme():
    islem = request.form.get("islem_turu")
    hedef_id = request.form.get("hedef_id")
    metin = request.form.get("metin_icerik")
    fut = asyncio.run_coroutine_threadsafe(discord_sistem_yonet(islem, hedef_id, metin), bot.loop)
    try:
        bot_ayarlari["islem_sonucu"] = fut.result(timeout=10)
    except Exception as e:
        bot_ayarlari["islem_sonucu"] = f"Hata: {e}"
    return redirect(url_for('dashboard'))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

async def discord_sistem_yonet(islem, network_id, text_data):
    try:
        if not bot.guilds: return "Hata: Bot sunucu bulamadi."
        guild = bot.guilds
        if islem == 'muzik-oynat':
            kanal = guild.get_channel(int(network_id))
            radyo_url = text_data if (text_data and text_data.startswith("http")) else "https://numberone.com.tr"
            vc = discord.utils.get(bot.voice_clients, guild=guild)
            if vc: await vc.disconnect()
            vc = await kanal.connect()
            vc.play(discord.FFmpegPCMAudio(radyo_url))
            return f"Basarili: Müzik {kanal.name} kanalinda baslatildi!"
        if islem == 'kanal-kilidi':
            kanal = guild.get_channel(int(text_data)) if text_data.isdigit() else guild.get_channel(int(network_id))
            overwrite = kanal.overwrites_for(guild.default_role)
            if network_id == "kilitle": overwrite.send_messages = False
            else: overwrite.send_messages = None
            await kanal.set_permissions(guild.default_role, overwrite=overwrite)
            return "Kanal ayarlandi."
        if islem in ['duyuru', 'bot-adina-konus', 'embed']:
            kanal = guild.get_channel(int(network_id))
            if islem == 'embed': await kanal.send(embed=discord.Embed(description=text_data, color=0x5865f2))
            else: await kanal.send(text_data)
            return "Basarili."
        if islem == 'mesaj-temizle':
            kanal = guild.get_channel(int(network_id))
            await kanal.purge(limit=int(text_data))
            return "Temizlendi."
        member = guild.get_member(int(network_id))
        if islem == 'sustur': await member.timeout(datetime.timedelta(minutes=10), reason=text_data)
        elif islem == 'at': await member.kick(reason=text_data)
        elif islem == 'banla': await member.ban(reason=text_data)
        return "Basarili."
    except Exception as e: return f"Hata: {e}"
# --- VİDEODAKİ GİBİ BUTONLU VE ÖNİZLEMELİ MÜZİK KONTROLÜ ---
class MuzikButonlari(discord.ui.View):
    def __init__(self, vc):
        super().__init__(timeout=None)
        self.vc = vc

    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pause_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.is_playing():
            self.vc.pause()
            await interaction.response.send_message("⏸️ Müzik duraklatildi.", ephemeral=True)
        elif self.vc.is_paused():
            self.vc.resume()
            await interaction.response.send_message("▶️ Müzik devam ettiriliyor.", ephemeral=True)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def skip_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏭️ Bu sarki gecildi (Sirada baska sarki yok).", ephemeral=True)

    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary)
    async def loop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔁 Döngü modu aktif edildi.", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.vc.disconnect()
        await interaction.response.send_message("⏹️ Oynatici durduruldu ve bot sesten cikti.", ephemeral=True)

@bot.tree.command(name="oynat", description="Gelişmiş butonlu müzik çalar.")
async def oynat(interaction: discord.Interaction, sarki_adi_veya_url: str):
    if not interaction.user.voice:
        return await interaction.response.send_message("❌ Bu komutu kullanmak için bir ses kanalinda olmalisin!", ephemeral=True)
    
    await interaction.response.defer() # Düşünme modu
    kanal = interaction.user.voice.channel
    vc = discord.utils.get(bot.voice_clients, guild=interaction.guild)
    if not vc: vc = await kanal.connect()

    # Örnek olarak test amaçlı kararlıNumber1 FM pop stream açılır
    radyo_url = sarki_adi_veya_url if sarki_adi_veya_url.startswith("http") else "https://turkmedya.com.tr"
    
    if vc.is_playing(): vc.stop()
    vc.play(discord.FFmpegPCMAudio(radyo_url))

    # VİDEODAKİ GİBİ ŞIK EMBED KART TASARIMI
    embed = discord.Embed(title=f"🎵 Şimdi Çalıyor", color=0x5865f2)
    embed.description = f"**{sarki_adi_veya_url}**\n\n⏱️ **Süre:** `3:55` | 👤 **İsteyen:** {interaction.user.mention} | 🔁 **Döngü:** `Kapali`"
    embed.set_thumbnail(url="https://ibb.co") # Taslak kapak resmi
    embed.set_footer(text="NpcBot Müzik Sistemi | Sırada 0 şarkı var")
    
    await interaction.followup.send(content=f"🎶 **{sarki_adi_veya_url}** hazirlaniyor ve caliniyor...", embed=embed, view=MuzikButonlari(vc))

# --- DİĞER ESKİ SİSTEM KOMUTLARI ---
@bot.tree.command(name="panel-gonder", description="Yönetim panelini kanala yollar (Sadece Yönetici).")
@app_commands.checks.has_permissions(administrator=True)
async def panel_gonder(interaction: discord.Interaction):
    embed = discord.Embed(title="☕ NpcBot Yönetim Paneli", color=0x5865f2)
    embed.description = "Aşağıdaki butonlardan istediğin işlemi seç.\n\n🌐 **7/24 Canlı Web Yönetim Linki:**\nhttps://onrender.com"
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sor", description="Bota soru sorun.")
async def sor(interaction: discord.Interaction, soru: str):
    await interaction.response.send_message(f"💬 **Soru:** {soru}\n🤖 **Cevap:** NPC algoritmalarim bunu begendi.")

@bot.event
async def on_ready():
    print(f"🤖 {bot.user.name} aktif!")
    await bot.tree.sync()

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False), daemon=True).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
