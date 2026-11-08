import discord, threading, datetime, asyncio, random, os
from discord import app_commands
from discord.ext import commands
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
bot_ayarlari = {"web_panel_durum": "Aktif", "islem_sonucu": "Sistem hazir."}

@app.route('/')
def dashboard():
    uye_sayisi = bot.guilds.member_count if bot.guilds else 0
    sesteki_sayisi = sum(len(c.members) for c in bot.guilds.voice_channels) if bot.guilds else 0
    bot_gecikme = round(bot.latency * 1000) if bot.latency else 0

    # Tam olarak istediğin o mor neon daireli fütüristik arka plan yapısı
    html_kod_blogu = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>NpcBot Yönetim Paneli</title>
        <style>
            body { background: url('https://peakpx.com') no-repeat center center fixed; background-size: cover; color: #dbdee1; font-family: sans-serif; padding: 20px; }
            .panel-container { max-width: 1000px; margin: auto; background: rgba(20, 20, 25, 0.65); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); padding: 25px; border-radius: 16px; box-shadow: 0 0 30px rgba(168, 85, 247, 0.4); border: 2px solid #a855f7; }
            h1 { color: #fff; font-size: 26px; font-weight: bold; margin-bottom: 5px; text-shadow: 0 0 10px rgba(168,85,247,0.5); }
            .subtitle { color: #949ba4; font-size: 14px; margin-bottom: 25px; }
            .section-title { font-size: 13px; text-transform: uppercase; color: #a855f7; font-weight: bold; margin-top: 25px; margin-bottom: 12px; letter-spacing: 1px; }
            .btn-grid { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 5px; }
            .btn-custom { padding: 10px 22px; font-weight: 600; border-radius: 10px; font-size: 14px; border: 2px solid transparent; cursor: pointer; transition: all 0.3s ease; background: rgba(0,0,0,0.4); }
            .btn-green { color: #2ecc71; border-color: #2ecc71; } .btn-green:hover { background: #2ecc71; color: white; box-shadow: 0 0 20px #2ecc71; }
            .btn-red { color: #e74c3c; border-color: #e74c3c; } .btn-red:hover { background: #e74c3c; color: white; box-shadow: 0 0 20px #e74c3c; }
            .btn-blue { color: #3498db; border-color: #3498db; } .btn-blue:hover { background: #3498db; color: white; box-shadow: 0 0 20px #3498db; }
            .btn-dark-gray { color: #95a5a6; border-color: #95a5a6; } .btn-dark-gray:hover { background: #95a5a6; color: white; box-shadow: 0 0 20px #95a5a6; }
            .btn-orange { color: #f39c12; border-color: #f39c12; } .btn-orange:hover { background: #f39c12; color: black; box-shadow: 0 0 20px #f39c12; }
            .stats-box { background-color: rgba(0, 0, 0, 0.4); padding: 15px; border-radius: 10px; margin-top: 15px; border: 1px solid #3498db; }
            .alert-custom { background-color: rgba(0, 0, 0, 0.4); color: #dbdee1; border: 1px solid #2ecc71; margin-bottom: 20px; padding: 12px; border-radius: 10px; }
            .custom-modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); }
            .modal-content { background-color: #1e1f22; margin: 15% auto; padding: 20px; border: 2px solid #a855f7; width: 400px; border-radius: 12px; color: white; }
            .close-btn { color: #aaa; font-size: 24px; font-weight: bold; cursor: pointer; }
            .form-group { margin-bottom: 15px; }
            .form-control-custom { width: 100%; padding: 10px; background-color: #111214; color: white; border: 1px solid #a855f7; border-radius: 6px; }
        </style>
    </head>
    <body>
    <div class="panel-container">
        <h1>☕ NpcBot Yönetim Paneli</h1>
        <p class="subtitle">Aşağıdaki butonlardan istediğin işlemi seç. Açılan form ekranı sadece sana görünür.</p>
        <div class="alert alert-custom">📢 <strong>Sistem Bildirimi:</strong> PAN_BILDIRIM</div>
        <div class="section-title">İçerik ve Duyuru</div>
        <div class="btn-grid">
            <button class="btn-custom btn-green" onclick="setFormAction('duyuru')">Duyuru</button>
            <button class="btn-custom btn-green" onclick="setFormAction('bot-adina-konus')">Bot Adına Konuş</button>
            <button class="btn-custom btn-green" onclick="setFormAction('embed')">Embed</button>
        </div>
        <div class="section-title">Moderasyon</div>
        <div class="btn-grid">
            <button class="btn-custom btn-red" onclick="setFormAction('uyar')">Uyar</button>
            <button class="btn-custom btn-red" onclick="setFormAction('sustur')">Sustur</button>
            <button class="btn-custom btn-red" onclick="setFormAction('at')">At</button>
            <button class="btn-custom btn-red" onclick="setFormAction('banla')">Banla</button>
            <button class="btn-custom btn-green" onclick="setFormAction('ban-ac')">Ban Aç</button>
        </div>
        <div class="section-title">Karantina</div>
        <div class="btn-grid"><button class="btn-custom btn-orange" onclick="setFormAction('karantina')">Karantina</button></div>
        <div class="section-title">İnceleme ve Araçlar</div>
        <div class="btn-grid">
            <button class="btn-custom btn-blue" onclick="setFormAction('uye-sicili')">Üye Sicili</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('susturmayi-kaldir')">Susturmayı Kaldır</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('uyari-sil')">Uyarı Sil</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('not-ekle')">Not Ekle</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('mesaj-temizle')">Mesaj Temizle</button>
        </div>
        <div class="btn-grid mt-2">
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('kanal-kilidi')">Kanal Kilidi</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('yavas-mod')">Yavaş Mod</button>
            <button class="btn-custom btn-dark-gray" onclick="setFormAction('durum')">Durum</button>
        </div>
        <div class="section-title">Canlı Durum</div>
        <div class="stats-box">
            <p>● PAN_UYE üye • PAN_SES seste • 0 susturulmuş • 0 uyarılı</p>
            <p>● Gecikme: PAN_MSms • Panel: PAN_DURUM 🟢</p>
        </div>
    </div>
    <div id="islemModal" class="custom-modal">
      <div class="modal-content" style="padding:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
          <h5 id="modalBaslik" style="margin:0; font-size:18px;">İşlem Formu</h5>
          <span class="close-btn" onclick="closeModal()">&times;</span>
        </div>
        <form action="/panel-islem-tetikleme" method="POST">
            <input type="hidden" name="islem_turu" id="hiddenIslemTuru">
            <div class="form-group"><label id="idEtiket">ID Girin:</label><input type="text" name="hedef_id" class="form-control-custom" required></div>
            <div class="form-group"><label id="icerikEtiket">Metin:</label><input type="text" name="metin_icerik" class="form-control-custom" value="Panel üzerinden işlem yapıldı."></div>
            <div style="text-align: right; margin-top:20px;">
                <button type="button" class="btn-custom btn-dark-gray" onclick="closeModal()" style="margin-right:5px;">İptal</button>
                <button type="submit" class="btn-custom btn-blue" style="background-color:#5865f2; border:none; border-radius:6px; padding:10px 20px; color:white;">Onayla</button>
            </div>
        </form>
      </div>
    </div>
    <script>
        function openModal() { document.getElementById('islemModal').style.display = "block"; }
        function closeModal() { document.getElementById('islemModal').style.display = "none"; }
        function setFormAction(action) {
            document.getElementById('hiddenIslemTuru').value = action;
            var baslik = document.getElementById('modalBaslik');
            var idEtiket = document.getElementById('idEtiket');
            var icerikEtiket = document.getElementById('icerikEtiket');
            if(action === 'duyuru' || action === 'bot-adina-konus' || action === 'embed') {
                baslik.innerText = action.toUpperCase() + " Menüsü"; idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Mesaj İçeriği:";
            } else if(action === 'mesaj-temizle') {
                baslik.innerText = "Mesaj Temizleme"; idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Silinecek Adet:";
            } else if(action === 'kanal-kilidi') {
                baslik.innerText = "Kanal Kilidi"; idEtiket.innerText = "İşlem (kilitle / ac):"; icerikEtiket.innerText = "Kanal ID:";
            } else if(action === 'yavas-mod') {
                baslik.innerText = "Yavaş Mod"; idEtiket.innerText = "Saniye:"; icerikEtiket.innerText = "Kanal ID:";
            } else {
                baslik.innerText = action.toUpperCase() + " Menüsü"; idEtiket.innerText = "Kullanıcı ID:"; icerikEtiket.innerText = "Gerekçe:";
            }
            openModal();
        }
    </script>
    </body>
    </html>
    """
    html_kod_blogu = html_kod_blogu.replace("PAN_BILDIRIM", bot_ayarlari['islem_sonucu'])
    html_kod_blogu = html_kod_blogu.replace("PAN_UYE", str(uye_sayisi)).replace("PAN_SES", str(sesteki_sayisi))
    html_kod_blogu = html_kod_blogu.replace("PAN_MS", str(bot_gecikme)).replace("PAN_DURUM", bot_ayarlari['web_panel_durum'])
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
        if islem == 'kanal-kilidi':
            kanal = guild.get_channel(int(text_data)) if text_data.isdigit() else guild.get_channel(int(network_id))
            overwrite = kanal.overwrites_for(guild.default_role)
            if network_id == "kilitle": overwrite.send_messages = False
            else: overwrite.send_messages = None
            await kanal.set_permissions(guild.default_role, overwrite=overwrite)
            return "Kanal kilidi guncellendi."
        if islem == 'yavas-mod':
            kanal = guild.get_channel(int(text_data))
            await kanal.edit(slowmode_delay=int(network_id))
            return "Yavas mod guncellendi."
        if islem in ['duyuru', 'bot-adina-konus', 'embed']:
            kanal = guild.get_channel(int(network_id))
            if islem == 'embed': await kanal.send(embed=discord.Embed(description=text_data, color=0x5865f2))
            else: await kanal.send(text_data)
            return "Mesaj gonderildi."
        if islem == 'mesaj-temizle':
            kanal = guild.get_channel(int(network_id))
            await kanal.purge(limit=int(text_data))
            return "Mesajlar temizlendi."
        if islem == 'ban-ac':
            user = await bot.fetch_user(int(network_id))
            await guild.unban(user)
            return "Ban acildi."
        member = guild.get_member(int(network_id))
        if not member: return "Hata: Kullanici bulunamadi."
        if islem == 'sustur': await member.timeout(datetime.timedelta(minutes=10), reason=text_data)
        elif islem == 'at': await member.kick(reason=text_data)
        elif islem == 'banla': await member.ban(reason=text_data)
        return "Islem basarili."
    except Exception as e: return f"Hata: {e}"

@bot.event
async def on_member_join(member):
    rol = discord.utils.get(member.guild.roles, name="Uye")
    if rol: await member.add_roles(rol)

class PanelButonlari(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Duyuru", style=discord.ButtonStyle.green)
    async def duyuru_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("📢 Duyuru sistemi web panelde aktiftir.", ephemeral=True)

@bot.tree.command(name="panel-gonder", description="Yönetim panelini kanala yollar (Sadece Yönetici).")
@app_commands.checks.has_permissions(administrator=True)
async def panel_gonder(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title="☕ NpcBot Yönetim Paneli", color=0x5865f2)
    embed.description = "Aşağıdaki butonlardan istediğin işlemi seç.\n\n🌐 **7/24 Canlı Web Yönetim Linki:**\nhttps://onrender.com"
    await interaction.response.send_message(embed=embed, view=PanelButonlari())

@panel_gonder.error
async def panel_gonder_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.AppCommandError):
        await interaction.response.send_message("❌ Bu komutu kullanmak için **Yönetici** yetkisine sahip olmalısın!", ephemeral=True)

@bot.tree.command(name="yazi-tura", description="Yazi tura atar.")
async def yazi_tura(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 Sonuc: **{random.choice(['Yazi', 'Tura'])}**")

@bot.tree.command(name="zar-at", description="Zar atar.")
async def zar_at(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 Zar: **{random.randint(1, 6)}**")

@bot.tree.command(name="sor", description="Bota soru sorun.")
async def sor(interaction: discord.Interaction, soru: str):
    cevaplar = ["Harika bir soru!", "NPC algoritmalarim bunu begendi.", "Bence kesinlikle evet!"]
    await interaction.response.send_message(f"💬 **Soru:** {soru}\n🤖 **Cevap:** {random.choice(cevaplar)}")

@bot.event
async def on_ready():
    print(f"🤖 {bot.user.name} aktif!")
    await bot.tree.sync()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False), daemon=True).start()
    bot.run(os.environ.get('DISCORD_TOKEN'))
