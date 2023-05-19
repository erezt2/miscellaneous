import os
import discord
import asyncio
import re
import random
from keep_alive import keep_alive


BOT_INVINCIBLE = False
TOKEN = os.environ['TOKEN']
PREFIX = "$"

# TEMP = 395137068096
intents = discord.Intents.all()
#intents.reactions = True
#intents.messages = True
client = discord.Client(intents=intents)
    
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

async def create_shiritori(convo, msg):
    thread = await msg.create_thread(name=f"shiritori - host {convo.user.name}")
    s = Shiritori(convo, thread)
    for user in s.users:
        await thread.add_user(user[0])
    if s.current() == client.user:
        await asyncio.sleep(10)
        await s.thread.send(s.guess_word())
        s.first = False

async def delayed_message(channel, time, message):
    await asyncio.sleep(time)
    await channel.send(message)

class Check:
    # default func
    @staticmethod
    def check(convo, cmd):
        try:
            res = Conversation.types[convo.type]["verify"][convo.index](cmd)
            for i in convo.sentences:
                i.reset()
            cmd.reset()
            if res is None:
                return True
            return res
        except Exception as e:
            for i in convo.sentences:
                i.reset()
            cmd.reset()
            return False

    if True:
        @staticmethod
        def participents(cmd):
            if cmd != "yes" and cmd != "no":
                return False
    
            c = 0
            different = False
            if cmd == "yes":
                different = True
                c += 1

            if cmd:
                next(cmd)
                for i in cmd:
                    c += 1
                    user = client.get_user(int(re.search(r"[0-9]+", i).group(0)))
                    if user != client.user:
                        different = True

            if c == 0:
                return "not enough people."
            if not different:
                return "nice try asshole."
            if c >= 20:
                return "too many people."
    
        @staticmethod
        def only_letters(cmd):
            for i in cmd:
                re.search(r"\A[a-zA-Z]+\Z", i).group(0)
    
        @staticmethod
        def one_numeric(cmd):
            if len(cmd) != 1:
                return False
            c = float(cmd[0])
            if c < 1:
                return "timeout is set too low"

            if c > 20:
                return "timeout is set too high"
    

class Texts:
    texts = {}

    @classmethod
    def format(cls, string, **kwargs):
        for key in kwargs:
            string = string.replace(f"[{key}]", kwargs[key])
        return string
    
    @classmethod
    def init(cls):
        _f = open("texts.txt", "r")
        lines = _f.readlines()
        key = "&\n"
        value = "\n"
        for line in lines:
            if line[0] == "&":
                cls.texts[key[1:-1]] = value[:-1]
                key = line
                value = ""
            else:
                value += line

        del cls.texts['']

    @classmethod
    def get(cls, key, *args):
        return cls.texts[key].format(*args, PREFIX=PREFIX)

    @staticmethod
    def get_convo_text(convo):
        key_func = Conversation.types[convo.type]["format"][convo.index]
        if key_func is None:
            return Conversation.types[convo.type]["replies"][convo.index]
        text = Texts.format(Conversation.types[convo.type]["replies"][convo.index], **key_func(convo))
        for cmd in convo.sentences:
            cmd.reset()
        return text
    
    if True:
        @staticmethod
        def game_get_first(convo):
            cmd = convo.sentences[0]
            order = []
            if cmd == "yes":
                order.append(convo.user.mention)

            if cmd:
                next(cmd)
                for i in cmd:
                    order.append(i)

            cmd = convo.sentences[1]
            let = []
            for i in cmd:
                let.append(i)

            return {"ORDER": " -> ".join(order), "MENTION": order[0], "END": ", ".join(let), "TIME": convo.sentences[2][0]}

            
    
class Command:
    def __init__(self, msg):
        self.__full = remove_prefix(msg, PREFIX).split(" ")
        if not remove_prefix(msg, PREFIX):
            self.__full = []
        self.__index = 0

    def __getitem__(self, item=None):
        if item is None:
            return self.__full[self.__item]
        if not (0 <= item < len(self.__full)):
            raise IndexError

        return self.__full[item]

    def __eq__(self, other):
        return self[self.__index] == other

    def __len__(self):
        return len(self.__full)
    
    def __next__(self):
        self.__index += 1
        return self[self.__index]

    def __iter__(self):
        return iter(list(self.__full[self.__index:]))

    def reset(self):
        self.__index = 0

    def __str__(self):
        return str(self.__full)

    def __bool__(self):
        return self.__index != len(self.__full) - 1
            


class Conversation:
    TIMEOUT = 90
    
    active_convos = {}
    
    default_rules = {
        "read-threads": False,
    }
    types = {}
    
    @classmethod
    def init(cls):
        cls.types = {
            "start": {
                "verify": [Check.participents, Check.only_letters, Check.one_numeric],
                "format": [None, None, None, Texts.game_get_first],
                "replies": Texts.get("start-convo").split("|\n"),
                "func": create_shiritori,
                "rules": {
                    
                }
            }
        }
        cls.active_convos = {}

    @classmethod
    async def wait_for(cls, msg):
        try:
            message = await client.wait_for('message', timeout=float(cls.TIMEOUT), check=
                                        (lambda m: m.author == msg.author and m.channel == msg.channel and m.content.startswith(PREFIX)))
        except asyncio.TimeoutError:
            await msg.channel.send(f"{msg.author.mention}\ntoo slow. conversation ended")
            del Conversation.active_convos[(msg.author, msg.channel)]
        else:
            await handle_convo(message)
    
    @classmethod
    async def start(cls, msg):
        c = cls(msg)
        cls.active_convos[(msg.author, msg.channel)] = c
        if (msg.content == "balls"):
            return
        await c.channel.send(f"{msg.author.mention}\n{cls.types[c.type]['replies'][0]}")
        await cls.wait_for(msg)
    
    @staticmethod
    def get_type(cmd):
        if cmd == "start":
            return "start"
        elif cmd == "settings":
            next(cmd)
            if cmd == "bot":
                return "bot-settings"
            elif cmd == "shiritori":
                return "shiritori-settings"

    
    def __init__(self, msg):
        self.channel = msg.channel
        self.user = msg.author
        
        cmd = Command(msg.content)
        self.type = self.get_type(cmd)
        
        self.sentences = []
        self.index = 0
        

class Shiritori:
    words = {}  # all the words that exist
    active_games = {}
    
    @classmethod
    def init(cls):
        _f = open("words.txt", "r")
        cls.words = set(map(lambda x: x.replace("\n", ""), _f.readlines()))
        _f.close()

    def __init__(self, convo, thread):
        self.stopped = False
        self.thread = thread
        self.turn = 0
        ccmd = convo.sentences[0]
        self.alive = 1 if ccmd == "yes" else 0
        self.users = [[convo.user, True, 0]] if ccmd == "yes" else []
        self.death_order = []
        
        if ccmd:
            next(ccmd)
            for i in iter(ccmd):
                user = client.get_user(int(re.search(r"[0-9]+", i).group(0)))
                if not BOT_INVINCIBLE or user != client.user:
                    self.alive += 1
                self.users.append([user, True, 0])

        self.total_alive = int(self.alive)
        self.constraints = list(map(lambda x: x.upper(), convo.sentences[1]))
        self.time = float(convo.sentences[2][0])
        self.active_games[thread] = self
        self.last_word = None
        self.amount = len(self.users)
        self.host = convo.user

        self.said_words = set()
        self.first = True

    def guess_word(self):
        choises = filter(lambda x: self.word_valid(x), self.words)
        return random.choice(list(choises))
    
    def remove_player(self):
        del self.a

    def get_next_turn(self):
        c = (self.turn + 1) % self.amount
        while True:
            if self.users[c][1] == True:
                return c
            c += 1
            c %= self.amount

    def kill(self):
        self.death_order.append(int(self.turn))
        self.users[self.turn][1] = False
        if not BOT_INVINCIBLE or self.users[self.turn][0] != client.user:
            self.alive -= 1
        if self.alive <= 1:
            return True
        return False
    
    async def end_game(self):
        self.stopped = True
        j = 0
        for user in self.users:
            if user[1]:
                self.death_order.append(j)
            j += 1
        string = []
        num = 1
        for i in self.death_order[::-1]:
            user = self.users[i]
            string.append(f"{num}. {user[0].mention} - score: {user[2]}")
            num += 1
        string = '\n'.join(string)
        await self.thread.send(Texts.format(Texts.get("game-ended"), SCORES=string))
        del self.active_games[self.thread]
        try:
            await client.wait_for('message', timeout=45, check=
                                        (lambda m: m.author == self.host and m.channel == self.thread and m.content == f"{PREFIX}again"))
        except asyncio.TimeoutError:
            await self.thread.delete()
        else:
            self.stopped = False
            self.turn = 0
            self.alive = self.total_alive
            self.active_games[self.thread] = self
            self.last_word = None
            self.said_words = set()
            self.first = True
            self.death_order = []
            for i in self.users:
                i[1] = True
                i[2] = 0

            await self.thread.send(Texts.format(Texts.get("game-restarted"), ORDER=" -> ".join(map(lambda x: x[0].mention, self.users)), MENTION= self.current().mention, END=", ".join(self.constraints), TIME=str(self.time)))
            
            if self.current() == client.user:
                await asyncio.sleep(7.5)
                await self.thread.send(self.guess_word())
                self.first = False
            
        
    
    def current(self):
        return self.users[self.turn][0]
        
    async def await_turn(self):
        
        try:
            message = await client.wait_for('message', timeout=self.time, check=
                                        (lambda m: m.author == self.current() and m.channel == self.thread))
        except asyncio.TimeoutError:
            if self.stopped:
                return
            loser = self.current().name
            await self.thread.send(f"{loser} has timedout and lost.")
            if self.kill():
                await self.end_game()
                return

            self.turn = self.get_next_turn()

            await self.thread.send(f"its {self.current().mention}'s turn.")
            await self.await_turn()
            return
        else:
            if self.stopped:
                return
            if re.search(r"\A[a-zA-Z]+\Z", message.content) is None:
                loser = self.current().name
                await self.thread.send(f"{self.current().name} is a dumbass and lost.")
                if self.kill():
                    await self.end_game()
                    return

                self.turn = self.get_next_turn()
                    
                await self.thread.send(f"its {self.current().mention}'s turn.")
                await self.await_turn()
                return

            if not self.word_valid(message.content):
                loser = self.current().name
                await self.thread.send(f"{loser} wrote an invalid word.")
                if self.kill():
                    await self.end_game()
                    return
                
                self.turn = self.get_next_turn()
                
                await self.thread.send(f"its {self.current().mention}'s turn.")
                await self.await_turn()
                return

            self.users[self.turn][2] += 1
            self.turn = self.get_next_turn()
            self.last_word = message.content.upper()
            self.said_words.add(message.content.upper())
            await self.thread.send(f"its {self.current().mention}'s turn.")
            await self.await_turn()
            
                

    async def handle_message(self, message):
        if client.user.mention in message.content and message.author == client.user and not self.stopped and not self.first:
            c = -0.25 if BOT_INVINCIBLE else 0.25
            await delayed_message(self.thread, random.uniform(0.25, self.time + c), self.guess_word())
            return
        if (message.author == self.host) and (message.content.lower() in (f"{PREFIX}end", f"{PREFIX}stop")):
            await self.end_game()
            return
            
        if (message.author != client.user) and (not message.is_system()) and message.author != self.current():
            await message.delete()
            return

        if not self.first:
            return

        if message.author == client.user and client.user != self.current():
            return
        
        if re.search(r"\A[a-zA-Z]+\Z", message.content) is None:
            await self.thread.send(f"try again but now use your head")
            return
        
        word = message.content.upper()
        for i in self.constraints:
            if word.endswith(i):
                await self.thread.send(f"read the rules idiot")
                return
        
        if word not in self.words:
            await self.thread.send(f"how did you fuck up this bad? that's not a real word")
            return

        self.first = False
        self.said_words.add(word)
        self.turn = self.get_next_turn()
        self.last_word = word
        await self.thread.send(f"GAME STARTED!\nits {self.current().mention}'s turn.")
        await self.await_turn()

            
    def word_valid(self, word):
        word = word.upper()
        
        if word in self.said_words:
            return False

        if not self.first:
            if word[0] != self.last_word[-1]:
                return False
            
        for i in self.constraints:
            if word.endswith(i):
                return False

        if word not in self.words:
            return False
        
        return True
        
        
async def handle_message(message):
    cmd = Command(message.content)
    if cmd == "ping":
        await message.reply("pong")
    elif cmd == "cock":
        await message.reply("balls")
    elif cmd == "start":
        if isinstance(message.channel, discord.TextChannel):
            await Conversation.start(message)
    elif cmd == "help":
        await message.channel.send(Texts.get("help", message.author.mention))
    elif cmd == "rules":
        await message.channel.send(Texts.get("rules", message.author.mention))
    elif cmd == "settings":
        await message.channel.send("nothing here yet lol")

async def handle_convo(message):
    if message.content.upper() in [f"{PREFIX}END", f"{PREFIX}QUIT", f"{PREFIX}STOP", f"{PREFIX}EXIT"]:
        await message.channel.send("conversation stopped")
        del Conversation.active_convos[(message.author, message.channel)]
        return

    
    cmd = Command(message.content)
    convo = Conversation.active_convos[(message.author, message.channel)]

    error = Check.check(convo, cmd)
    if not error:
        await message.channel.send(f"{message.author.mention}\ninvalid input, try again. type {PREFIX}EXIT to stop\n{Texts.get_convo_text(convo)}")
        await Conversation.wait_for(message)
        return
    if isinstance(error, str):
        await message.channel.send(f"{error}\n{message.author.mention}\ninvalid input, try again. type {PREFIX}EXIT to stop\n{Texts.get_convo_text(convo)}")
        await Conversation.wait_for(message)
        return
        
    convo.sentences.append(cmd)
    convo.index += 1
    
    msg = await convo.channel.send(f"{message.author.mention}\n{Texts.get_convo_text(convo)}")
    
    if convo.index == len(Conversation.types[convo.type]["replies"]) - 1:
        del Conversation.active_convos[(message.author, message.channel)]
        await Conversation.types[convo.type]["func"](convo, msg)
    else:
        await Conversation.wait_for(message)

@client.event
async def on_ready():
    print('Logged on as {0}!'.format(client.user))

@client.event
async def on_message(message):
    # if message.content == f"{PREFIX}balls":
    #     c = Conversation(message)
    #     c.sentences.append(Command(f"{PREFIX}yes {client.user.mention} <@932532081517527042>")) #  
    #     c.sentences.append(Command(f"{PREFIX}"))
    #     c.sentences.append(Command(f"{PREFIX}5"))
    #     await create_shiritori(c, message)
    #     return

    if message.channel in Shiritori.active_games:
        await Shiritori.active_games[message.channel].handle_message(message)
        return
    
    if message.author == client.user:
        return

    if message.content.startswith(PREFIX):
        if (message.author, message.channel) not in Conversation.active_convos:
            await handle_message(message)

Texts.init()
Conversation.init()
Shiritori.init()
keep_alive()
client.run(TOKEN)
