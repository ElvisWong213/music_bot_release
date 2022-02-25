# Music Bot

## Setup

1. Install requirements files
    ```
    python -m pip install -r requirements.txt
    ```

2. Create .env and add this line in .env
    ```
    DISCORD_TOKEN = Your Token
    ```

3. Run music bot
    ```
    python bot.py
    ```
    
## Command

- **!join**
    ```
    簡寫(!j, !J)
    加bot到你身處的channel

    Shortform(!j, !J)
    Bot join to the channel
    ```

- **!leave**
    ```
    中斷bot連接
    Bot leave the channel
    ```

- **!play (URL,歌名)**
    ```
    簡寫(!p, !P)
    加歌到playlist
    可以直接用!play
    會自動加個bot入channel

    Shortform(!p, !P)
    Adding songs to playlist
    ```

- **!add_next (URL,歌名)**
    ```
    簡寫(!an, !AN)
    加歌到下一首播放

    Shortform(!an, !AN)
    Add songs to play next
    ```

- **!play_next (編號)**
    ```
    簡寫(!pn, !PN)
    將已經加左入playlist嘅歌移到下一首播放

    Sortform(!pn, !PN)
    Play next song that has been added to the playlist
    ```

- **!force_play (URL,歌名)**
    ```
    簡寫(!fp, !FP)
    強制播放歌曲

    Sortform(!fp, !FP)
    Force play a song
    ```

- **!list**
    ```
    列出所有已加入playlist嘅歌

    list all the songs in the playlist
    ```

- **!mylist (動作) (URL)**
    ```
    簡寫(!ml, !ML)
    Shortform(!ml, !ML)

    !mylist
    建立自己的播放列表
    Create your own playlist

    !mylist list
    列出列表中的歌曲
    List all the song in your playlist

    !mylist add (URL)
    將歌曲加到列表中
    Add song to your playlist

    !mylist remove (URL, 歌曲編號)
    將歌曲從列表中移除
    Remove song from your playlist
    ```

- **!remove (編號)**
    ```
    簡寫(!r, !R, !rm, !RM)
    將歌從playlist移除

    Sortform(!r, !R, !rm, !RM)
    Remove song from the playlist

    !remove all
    移除playlist嘅所有歌
    Remove all songs from playlist
    ```

- **!mode (編號)**
    ```
    簡寫(!m, !M)
    1. 順序單次播放
    2. 重覆播放成個playlist
    3. 重覆播放一首歌

    Sortform(!m, !M)
    1. Play in order
    2. Repeat playlist
    3. Repeat a single song
    ```

- **!pause**
    ```
    暫停
    Pause
    ```

- **!resume**
    ```
    繼續播放
    Resume
    ```

- **!skip**
    ```
    跳過
    Skip
    ```

- **!stop**
    ```
    停止播放所有歌(playlist 的所有歌會被移除)
    Stop and playlist will clear
    ```

- **!lyrics (歌名) _beta_**
    ```
    簡寫(!ly, !LY)
    顯示歌詞

    Shortform(!ly, !LY)
    Display song lyrics
    ```