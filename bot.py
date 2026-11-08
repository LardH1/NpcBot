import discord, threading, datetime, asyncio, random, os
from discord import app_commands
from discord.ext import commands
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
bot_ayarlari = {"web_panel_durum": "Aktif", "islem_sonucu": "Sistem hazir ve sunucunuza bagli."}

@app.route('/')
def dashboard():
    uye_sayisi = bot.guilds[0].member_count if bot.guilds else 0
    sesteki_sayisi = sum(len(c.members) for c in bot.guilds[0].voice_channels) if bot.guilds else 0
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
        function setFormAction(action) {
            document.getElementById('hiddenIslemTuru').value = action;
            var modal = document.getElementById('islemModal');
            var baslik = document.getElementById('modalBaslik');
            var idEtiket = document.getElementById('idEtiket');
            var icerikEtiket = document.getElementById('icerikEtiket');
            if(action === 'duyuru' || action === 'bot-adina-konus' || action === 'embed') {
                baslik.innerText = action.toUpperCase() + " Gönderme Menüsü";
                idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Mesaj İçeriği:";
            } else if(action === 'mesaj-temizle') {
                baslik.innerText = "Mesaj Temizleme";
                idEtiket.innerText = "Kanal ID:"; icerikEtiket.innerText = "Silinecek Adet:";
            } else if(action === 'kanal-kilidi') {
                baslik.innerText = "Kanal Kilidi";
                idEtiket.innerText = "İşlem (kilitle / ac):"; icerikEtiket.innerText = "Kanal ID:";
            } else if(action === 'yavas-mod') {
                baslik.innerText = "Yavaş Mod";
                idEtiket.innerText = "Saniye (0 = kapat):"; icerikEtiket.innerText = "Kanal ID:";
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

async def discord_sistem_yonet(islem, hedef_id, text_data):
    try:
        if not bot.guilds: return "Hata: Bot sunucu bulamadi."
        guild = bot.guilds[0]
        if islem == 'kanal-kilidi':
            kanal = guild.get_channel(int(text_data)) if text_data.isdigit() else guild.get_channel(int(hedef_id))
            if not kanal: return "Hata: Kanal bulunamadi."
            overwrite = kanal.overwrites_for(guild.default_role)
            if hedef_id == "kilitle": overwrite.send_messages = False
            else: overwrite.send_messages = None
            await kanal.set_permissions(guild.default_role, overwrite=overwrite)
            return "Kanal ayarlandi."
        if islem == 'yavas-mod':
            kanal = guild.get_channel(int(text_data))
            if not kanal: return "Hata: Kanal bulunamadi."
            await kanal.edit(slowmode_delay=int(hedef_id))
            return f"Basarili: Yavas mod ayarlandi."
        if islem in ['duyuru', 'bot-adina-konus', 'embed']:
            kanal = guild.get_channel(int(hedef_id))
            if not kanal: return "Hata: Kanal bulunamadi."
            if islem == 'embed': await kanal.send(embed=discord.Embed(description=text_data, color=0x5865f2))
            else: await kanal.send(text_data)
            return "Basarili: Mesaj iletildi."
        if islem == 'mesaj-temizle':
            kanal = guild.get_channel(int(hedef_id))
            if not kanal: return "Hata: Kanal bulunamadi."
            await kanal.purge(limit=int(text_data))
            return "Temizlendi."
        if islem == 'ban-ac':
            user = await bot.fetch_user(int(hedef_id))
            await guild.unban(user, reason=text_data)
            return f"Basarili: {user.name} yasagi kaldirildi."
        member = guild.get_member(int(hedef_id))
        if not member: return "Hata: Kullanici bulunamadi."
        if islem == 'sustur': await member.timeout(datetime.timedelta(minutes=10), reason=text_data)
        elif islem == 'at': await member.kick(reason=text_data)
        elif islem == 'banla': await member.ban(reason=text_data)
        return "Basarili."
    except Exception as e: return f"Discord Hatasi: {e}"

@bot.event
async def on_member_join(member):
    try: await member.send(f"Merhaba {member.name}! Sunucumuza hos geldin.")
    except discord.Forbidden: pass
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
    embed.description = (
        "Aşağıdaki butonlardan istediğin işlemi seç.\n\n"
        f"**Canlı Durum**\n• {guild.member_count} üye • Koruma: 5/8 açık\n\n"
        "🌐 **7/24 Canlı Web Yönetim Linki:**\n"
        "https://onrender.com"
    )
    await interaction.response.send_message(embed=embed, view=PanelButonlari())

@panel_gonder.error
async def panel_gonder_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.MissingPermissions):
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
