![https://discord.gg/rXVnuTB](https://img.shields.io/discord/671897656003395595?color=blue&logo=discord)
![](https://img.shields.io/github/languages/code-size/keli5/LettersBotPY?logo=github&logoColor=black)
![https://github.com/keli5/LettersBotPY/issues](https://img.shields.io/github/issues-raw/keli5/lettersbotpy)
![https://github.com/keli5/LettersBotPY/commits/master](https://img.shields.io/github/commit-activity/w/keli5/LettersBotPY)
![https://creativecommons.org/licenses/by-sa/4.0/](https://img.shields.io/badge/license-CC%20BY--SA%204.0-informational)

# LettersBotPY
LettersBot 2.0, if you will. Marginally better &amp; rewritten in Python. dread
<br>Join the Discord: [Click here](https://discord.gg/DPCEzJT)<br>
Or, invite the bot to your own Discord: [Click here](https://cutt.ly/lettersbot)

### Thanks
Thanks to [kaylynn234](https://github.com/kaylynn234) for a lot but commit [`b308f5d`](https://github.com/keli5/LettersBotPY/commit/b308f5d6e5cb8f60ce90a73788b06689c9610293) in particular  <br>
Thanks to [Litleck](https://github.com/Litleck) for causing me to realize how painful JS is<br>
And huge thanks to [everyone who works on crimsoBOT](https://github.com/crimsobot/crimsoBOT/) because the help command may, or may not, be directly lifted from them

## Setup?
There's a 99% chance this doesn't work on windows<br>
Run launcher.py to start the bot - on first run, it will create a sqlite3 file<br>
Should work on Python 3.6 and up, tested on 3.7.5<br>
You'll need an environment variable called BOT_TOKEN, containing the token of the discord bot you want to run this as<br>
You'll also need an environment variable called LB_PREFIX to set the bot prefix. Defaults to `d::`. <br>
Make sure that you change the classes/botowners.txt to contain user IDs of people who should be able to run owner-only commands and use Jishaku if installed
### Deps
Ensure that ffmpeg and libopus are installed on your system
do `pip install -r requirements.txt` to automatically install required dependencies<br>
for extra debugging commands, do `pip install jishaku`


## License
LettersBotPY is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/ " Atribution Share-Alike 4.0 license ")
