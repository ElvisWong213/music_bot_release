import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import youtube_dl
import asyncio
import json

from web_scraping import get_web_lyrics

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

class all_var:
    mode_name = ["Single", "Loop list", "Loop single song"]
    server_list = []
    file_name = []
    file_name_backup = []
    mode_number = []

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
        # take first item from a playlist
            data = data['entries']
        if len(data) == 1:
            data = data[0]
        filename = data
        return filename

@bot.command(name="play_local", aliases=['PL', 'pl'], help='play local song')
async def play_local(ctx, file_id=None, f=None):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    server = ctx.message.guild
    voice_channel = server.voice_client
    music_file = os.listdir("Music")

    list_all_file = ""

    for i in enumerate(music_file):
        list_all_file += "{}. {}\n".format(i[0], i[1])

    if file_id != None:
        int_file_id = int(file_id)
        if int_file_id >= 0 and int_file_id < len(music_file) - 1:
            if f == None:
                #play
                all_var.file_name[id_index].append([music_file[int_file_id], "Music/{}".format(music_file[int_file_id]), "0"])
                if not voice_channel.is_playing():
                    async with ctx.typing():
                        voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
                    await ctx.send('**正在播放: ** {}\n**長度:** {}:{}'.format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60))
                    voice_channel.is_playing()
                else:
                    await ctx.send('**已加入:** {}'.format((music_file[int_file_id])))
            if f == "an":
                if len(all_var.file_name[id_index]) > 0:
                    dummy = [music_file[int_file_id], "Music/{}".format(music_file[int_file_id])]
                    all_var.file_name[id_index].insert(1, dummy)
                    await ctx.send('**音樂已加入到待播清單:** {}'.format((dummy[0])))
                else:
                    await ctx.send('**所有音樂已經播放完畢!**. 請用 !play 加入音槳')

    else:
        await ctx.send(list_all_file)


@bot.command(name='play', aliases=['P', 'p', 'Play'], help='播放')
async def play(ctx, *, url):
    if not discord.utils.get(bot.voice_clients, guild=ctx.guild):
        await join(ctx)
    await play_run(ctx, url)

async def play_run(ctx, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    if url != None:
        if 'list' in url and url != "mylist":
            async with ctx.typing():
                filenames = await YTDLSource.from_url(url, loop=bot.loop)
                for filename in filenames:
                    all_var.file_name[id_index].append([filename['title'], filename["formats"][2]["url"], filename["duration"]])
                    print(filename['title'])
                await ctx.send('所有音樂已加入到待播清單, 請用 **!list** 顯示待播清單')
                if not voice_channel.is_playing():
                    voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
                    await ctx.send('**正在播放: ** {}\n**長度:** {}:{}'.format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60))
                    voice_channel.is_playing()
        elif url == "mylist":
            play_list_file = os.listdir("play_list")
            user_name = ctx.message.author.name
            json_file_name = "play_list/" + user_name + ".json"
            have_user = False

            for i in play_list_file:
                if i == user_name + ".json":
                    have_user = True
                    break
                else:
                    have_user = False

            if not have_user:
                await ctx.send("You don't have your own playlist, please use **!mylist** to create your playlist")
            else:
                list_url = []
                with open(json_file_name, "r") as f:
                    data = json.load(f)
                if len(data) > 0:
                    if len(data[0]) > 0 and len(data[1]) > 0:
                        list_url = data[1]
                
                async with ctx.typing():
                    for i in list_url:
                        filename = await YTDLSource.from_url(i, loop=bot.loop)
                        all_var.file_name[id_index].append([filename['title'], filename["formats"][2]["url"], filename["duration"]])
                        if not voice_channel.is_playing():
                            async with ctx.typing():
                                voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
                            await ctx.send('**正在播放: ** {}\**長度:** {}'.format(all_var.file_name[id_index][0][0], all_var.file_name[id_index][0][2]))
                            voice_channel.is_playing()
                await ctx.send("{}'s playlist has been added, use **!list** to show all the songs".format(user_name))
        else:
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            all_var.file_name[id_index].append([filename['title'], filename["formats"][2]["url"], filename["duration"]])
            if not voice_channel.is_playing():
                async with ctx.typing():
                    voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
                await ctx.send('**正在播放: ** {}\n**長度:** {}:{}'.format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60))
                voice_channel.is_playing()
            else:
                await ctx.send('**已加入:** {}'.format((filename['title'])))

async def play_next(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)

    if len(all_var.file_name[id_index]) > 0:
        #single
        if all_var.mode_number[id_index] == 1:
            all_var.file_name[id_index].pop(0)
            if len(all_var.file_name[id_index]) > 0:
                voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
            else:
                await ctx.send("**所有音樂已經播放完畢!**")
        #loop list
        elif all_var.mode_number[id_index] == 2:
            all_var.file_name_backup[id_index].append(all_var.file_name[id_index][0])
            all_var.file_name[id_index].pop(0)
            if len(all_var.file_name[id_index]) <= 0:
                all_var.file_name[id_index] = all_var.file_name_backup[id_index]
            voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        #loop single song
        elif all_var.mode_number[id_index] == 3:
            voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send('**正在播放: ** {}\n**長度:** {}:{}'.format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60))
    else:
        await ctx.send("**所有音樂已經播放完畢!**")



@bot.command(name='add_next', aliases=['an', 'AN'], help='插入音樂')
async def add_next(ctx, *, url):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    if len(all_var.file_name[id_index]) > 0:
        if url != None:
                if 'list' in url:
                    async with ctx.typing():
                        filenames = await YTDLSource.from_url(url, loop=bot.loop)
                        for filename in filenames:
                            all_var.file_name[id_index].insert(1 ,[filename['title'], filename["formats"][2]["url"]])
                        await ctx.send('已插入音樂所有音樂, 請用 **!list** 顯示待播清單')
                else:
                    filename = await YTDLSource.from_url(url, loop=bot.loop)
                    all_var.file_name[id_index].insert(1, [filename['title'], filename["formats"][2]["url"]])
                    await ctx.send('**已插入音樂:** {}'.format((filename['title'])))
    else:
        await ctx.send('**所有音樂已經播放完畢!**. 請用 !play 加入音槳')

@bot.command(name='play_next', aliases=['pn', 'PN'], help='播放下一首歌')
async def play_next_song(ctx, song_index):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    int_song_index = int(song_index)
    if len(all_var.file_name[id_index]) > 0 and int_song_index > 0 and int_song_index < len(all_var.file_name[id_index]):
        await ctx.send("{} will play next".format(all_var.file_name[id_index][int_song_index][0]))
        all_var.file_name[id_index].insert(1, all_var.file_name[id_index][int_song_index])
        all_var.file_name[id_index].pop(int_song_index + 1)
    elif len(all_var.file_name[id_index]) <= 0:
        await ctx.send("**所有音樂已經播放完畢!**")
    elif int_song_index <= 0:
        await ctx.send("It cannot smaller than 1")
    elif int_song_index > len(all_var.file_name[id_index]) - 1:
        await ctx.send("It cannot larger than {}".format(len(all_var.file_name[id_index])))

@bot.command(name='force_play', aliases=['fp', 'FP'], help='立即播放')
async def force_play(ctx, *, url):
    server = ctx.message.guild
    voice_channel = server.voice_client
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)

    if voice_channel.is_playing():
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            all_var.file_name[id_index].insert(0, [filename['title'], filename["formats"][2]["url"], filename["duration"]])
            voice_channel.stop()
            voice_channel.play(discord.FFmpegOpusAudio(source=all_var.file_name[id_index][0][1]), after= lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), client.loop))
        await ctx.send('**正在播放: ** {}\n**長度:** {}:{}'.format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60))
        voice_channel.is_playing()
    else:
        await ctx.send("Bot 目前沒有播放任何音樂")
    
@bot.command(name='mode', aliases=['m', 'M'], help='Mode = (1.single, 2.loop_list, 3.loop_single_song)')
async def mode(ctx, number = 0):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    check = False
    output = ""
    if number == 1:
        check = True
        output = all_var.mode_name[0]
    elif number == 2:
        check = True
        output = all_var.mode_name[1]
    elif number == 3:
        check = True
        output = all_var.mode_name[2]
    else:
        check = False
    if check:
        all_var.mode_number[id_index] = number
        await ctx.send('Change to {} mode'.format(output))
    else:
        await ctx.send('Mode unchanged \nMode: ' + str(all_var.mode_name[int(all_var.mode_number[id_index]) - 1]))

#use for debug
@bot.command(name='debug')
async def debug(ctx):
    server_id = ctx.guild.id
    channel_id = ctx.guild.channels
    print("\nchannel_id: {}".format(channel_id))
    print("server_id: {}".format(server_id))
    print("server_list: {}".format(all_var.server_list))
    print("file_name: {}".format(all_var.file_name))
    print("file_name_backup: {}".format(all_var.file_name_backup))
    print("mode_number: {}\n".format(all_var.mode_number))

@bot.command(name='join', aliases=['J', 'j', 'Join'], help='將bot加入')
async def join(ctx):
    server_id = ctx.guild.id
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        all_var.server_list.append(server_id)
        all_var.file_name.append([])
        all_var.file_name_backup.append([])
        all_var.mode_number.append(1)
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='remove', aliases=['r', 'R', 'rm', 'RM', 'Remove'], help='移除所有音樂')
async def remove(ctx, song_index):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    if "all" in song_index:
        all_var.file_name[id_index].pop()
        await ctx.send("已移除所有音樂!")
    elif "-" in song_index:
        song_index = song_index.replace(" ", "")
        start = int(song_index[song_index.index('-') + 1::])
        end = int(song_index[:song_index.index('-'):])
        if start < 0 or start > len(all_var.file_name[id_index]):
            await ctx.send("start value was unvalid")
        elif end < 0 or end > len(all_var.file_name[id_index]):
            await ctx.send("end value was unvalid")
        elif start <= end:
            await ctx.send("the range was unvalid")
        else:
            output = ""
            counter = 0
            for i in range(start, end - 1, -1):
                output += "{} 已被移除".format(all_var.file_name[id_index][i][0])
                all_var.file_name[id_index].pop(i)
                counter += 1
            await ctx.send(output)
            await ctx.send("由 {} 到 {} 已被移除. 總共:{}".format(end, start, counter))
    else:
        int_song_index = int(song_index)
        if len(all_var.file_name[id_index]) > 0 and int_song_index > 0 and int_song_index < len(all_var.file_name[id_index]):
            await ctx.send("{} 已被移除".format(all_var.file_name[id_index][int_song_index][0]))
            all_var.file_name[id_index].pop(int_song_index)
        elif len(all_var.file_name[id_index]) <= 0:
            await ctx.send("**所有音樂已經播放完畢!**")
        elif int_song_index <= 0:
            await ctx.send("It cannot smaller than 1")
        elif int_song_index > len(all_var.file_name[id_index]) - 1:
            await ctx.send("It cannot larger than {}".format(len(all_var.file_name[id_index])))

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("Bot 目前沒有播放任何音樂")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("Bot 目前沒有播放任何音樂. 請用 **!play** 加入音樂")
    


@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client.is_connected():
        server_id = ctx.guild.id
        id_index = all_var.server_list.index(server_id)
        voice_client.stop()
        all_var.server_list.pop(id_index)
        all_var.file_name.pop(id_index)
        all_var.file_name_backup.pop(id_index)
        all_var.mode_number.pop(id_index)
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='stop', help='停止')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    if voice_client.is_playing():
        voice_client.stop()
        all_var.file_name[id_index].clear()
    else:
        await ctx.send("Bot 目前沒有播放任何音樂")

@bot.command(name='skip', help='跳過音樂')
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await play(ctx, None)
    else:
        await ctx.send("Bot 目前沒有播放任何音樂")

@bot.command(name='list', help='列出待播清單')
async def list(ctx):
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    total_number_song = len(all_var.file_name[id_index])
    output = ""
    server_id = ctx.guild.id
    id_index = all_var.server_list.index(server_id)
    if total_number_song > 0:
        output += "**Mode:** " + str(all_var.mode_name[int(all_var.mode_number[id_index]) - 1])
        output += "\n**正在播放: ** {} **長度:** {}:{}\n".format(all_var.file_name[id_index][0][0], int(all_var.file_name[id_index][0][2] / 60), all_var.file_name[id_index][0][2] % 60)
        for i in range(total_number_song):
            if i < total_number_song - 1:
                output += "**{}.** {} **長度:** {}:{}\n".format(i+1, all_var.file_name[id_index][i+1][0], int(all_var.file_name[id_index][i+1][2] / 60), all_var.file_name[id_index][i+1][2] % 60)
            if (i != 0 and i % 30 == 0) or i == total_number_song - 1:
                await ctx.send(output)
                output = ""
    else:
        await ctx.send("**所有音樂已經播放完畢!!**")

@bot.command(name='mylist', aliases=['ml', 'ML'], help='my playlist')
async def mylist(ctx, control=None, *, url=None):
    play_list_file = os.listdir("play_list")
    user_name = ctx.message.author.name
    json_file_name = "play_list/" + user_name + ".json"
    have_user = False

    for i in play_list_file:
        if i == user_name + ".json":
            have_user = True
            break
        else:
            have_user = False

    if not have_user:
        with open(json_file_name, "w") as f:
            data = [[], []]
            json.dump(data, f)
        await ctx.send("{}'s playlist has been created".format(user_name))

    list_name = []
    list_url = []
    with open(json_file_name, "r") as f:
        data = json.load(f)
    if len(data) > 0:
        if len(data[0]) > 0 and len(data[1]) > 0:
            list_name = data[0]
            list_url = data[1]

    if control == None or control == "list":
        output_text = ""
        if len(list_name) > 0:
            output_text += "{}'s playlist:\n".format(user_name)
            for i in range(len(list_name)):
                output_text += "{}. {}\n".format(i + 1, list_name[i])
        else:
            output_text += "{}'s playlist is empty\n".format(user_name)
        await ctx.send(output_text)
    elif url != None:
        if control == "add":
            if "http" in url:
                filenames = await YTDLSource.from_url(url, loop=bot.loop)
                list_name.append(filenames['title'])
                list_url.append(url)
                save_json(json_file_name, list_name, list_url)
                await ctx.send("**{}** has been add to **{}'s** playlist".format(filenames['title'], user_name))
            elif "list" in url:
                await ctx.send("You cannot add youtube playlist")
            else:
                await ctx.send("**{}** is an invalid url".format(url))
        elif control == "remove":
            int_url = 0
            url_is_int = False
            output = ""
            try:
                int_url = int(url)
                url_is_int = True
            except ValueError:
                url_is_int = False

            if url_is_int:
                if int_url > 0 and int_url < len(list_name) + 1:
                    index = int_url - 1
                    output = list_name[index]
                    list_name.pop(index)
                    list_url.pop(index)
                else:
                    await ctx.send("**{}** is invalid value".format(url))
            else:
                filenames = await YTDLSource.from_url(url, loop=bot.loop)
                list_name.remove(filenames['title'])
                list_url.remove(filenames['title'])
                output = filenames['title']
            if save_json(json_file_name, list_name, list_url):
                await ctx.send("**{}** was removed from **{}'s** playlist!".format(output, user_name))

def save_json(json_file_name, list_name, list_url):
    output_to_json = []
    output_to_json.append(list_name)
    output_to_json.append(list_url)
    with open(json_file_name, "w") as f:
        json.dump(output_to_json, f)
    return True
            

@bot.command(name='lyrics', aliases=['ly', 'LY'], help='Show lyrics')
async def lyrics(ctx, title):
    if title != None:
        async with ctx.typing():
            get_text = get_web_lyrics(title)
        await ctx.send('Song: **' + title + '**\n' + get_text)

# channel冇人，bot會自動離開
# leave when all user are left
@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is not None and len(voice_state.channel.members) == 1:
        #5 minute
        await asyncio.sleep(300)
        if voice_state is not None and len(voice_state.channel.members) == 1:
            await member.guild.system_channel.send("走先啦,係咁先啦!")
            await leave(member)

@bot.event
async def on_ready():
    print('Running!')
    for guild in bot.guilds:
        for channel in guild.text_channels :
            if str(channel) == "general" :
                await channel.send('Bot Activated..')
                await channel.send(file=discord.File('giphy.png'))
        print('Active in {}\n Member Count : {}'.format(guild.name,guild.member_count))

if __name__ == "__main__" :
    bot.run(TOKEN)
