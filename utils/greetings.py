import random
from pyrogram import Client, filters
from pyrogram.types import Message
from utils import modules_help, prefix

CONGOS = [
    "`Congratulations and BRAVO!`",
    "`You did it! So proud of you!`",
    "`This calls for celebrating! Congratulations!`",
    "`I knew it was only a matter of time. Well done!`",
    "`Congratulations on your well-deserved success.`",
    "`Heartfelt congratulations to you.`",
    "`Warmest congratulations on your achievement.`",
    "`Congratulations and best wishes for your next adventure!`",
    "`So pleased to see you accomplishing great things.`",
    "`Feeling so much joy for you today. What an impressive achievement!`",
]
GDMORNING = [
    "`May this morning offer you new hope for life! May you be happy and enjoy every moment of it. Good morning!`",
    "`A new day has come with so many new opportunities for you. Grab them all and make the best out of your day. Here’s me wishing you a good morning!`",
    "`Welcome this beautiful morning with a smile on your face. I hope you’ll have a great day today. Wishing you a very good morning!`",
    "`Mornings come with a blank canvas. Paint it as you like and call it a day. Wake up now and start creating your perfect day. Good morning!`",
    "`Wake up like the sun every morning and light up the world your awesomeness. You have so many great things to achieve today. Good morning!`",
    "╔══╗────╔╗╔═╦═╗──────╔╗\n║╔═╬═╦═╦╝║║║║║╠═╦╦╦═╦╬╬═╦╦═╗\n║╚╗║╬║╬║╬║║║║║║╬║╔╣║║║║║║║╬║\n╚══╩═╩═╩═╝╚╩═╩╩═╩╝╚╩═╩╩╩═╬╗║\n─────────────────────────╚═╝❤",
]
GDNIGHT = [
    "`Have a very good night, friend! You are wonderful!`",
    "`Friend, you do not hesitate to get things done! Take tonight to relax and do more, tomorrow! Good Night`",
    "`Rest soundly, Good Night!`",
    "🌙.     *       ☄️      \n🌟   .  *       .         \n                       *   .      🛰     .        ✨      *\n  .     *   SLEEP WELL        🚀     \n      .              . . SWEET DREAMS 🌙\n. *       🌏 GOOD NIGHT         *\n                     🌙.     *       ☄️      \n🌟   .  *       .         \n                       *   .      🛰     .        ✨      *",
    "｡♥️｡･ﾟ♡ﾟ･｡♥️° ♥️｡･ﾟ♡ﾟ\n╱╱╱╱╱╱╱╭╮╱╱╱╭╮╱╭╮╭╮\n╭━┳━┳━┳╯┃╭━┳╋╋━┫╰┫╰╮\n┃╋┃╋┃╋┃╋┃┃┃┃┃┃╋┃┃┃╭┫\n┣╮┣━┻━┻━╯╰┻━┻╋╮┣┻┻━╯\n╰━╯╱╱╱╱╱╱╱╱╱╱╰━╯\n｡♥️｡･ﾟ♡ﾟ･｡♥️° ♥️｡･ﾟ♡ﾟ",
]
GDNOON = [
    "`Good Afternoon!`",
    "`Forget about yesterday, think about tommorow.. The victory will be yours.`",
    "`Do what you have to do right now.. Good Afternoon.`",
]
HLLO = [
    "╔┓┏╦━╦┓╔┓╔━━╗\n║┗┛║┗╣┃║┃║ X X ║\n║┏┓║┏╣┗╣┗╣╰╯║\n╚┛┗╩━╩━╩━╩━━╝",
    "██╗░░██╗██╗\n██║░░██║██║\n███████║██║\n██╔══██║██║\n██║░░██║██║\n╚═╝░░╚═╝╚═╝",
    "█░█ █▀█ █░█░█ █▀▄ █▄█ █\n█▀█ █▄█ ▀▄▀▄▀ █▄▀ ░█░ ▄",
    "▒█░▒█ █▀▀ █░░█ █\n▒█▀▀█ █▀▀ █▄▄█ ▀\n▒█░▒█ ▀▀▀ ▄▄▄█ ▄",
]
HBDAY = [
	"`Count your life by smiles, not tears. Count your age by friends, not years. Happy birthday!`",
	"`Happy birthday! I hope all your birthday wishes and dreams come true.`",
	"`A wish for you on your birthday, whatever you ask may you receive, whatever you seek may you find, whatever you wish may it be fulfilled on your birthday and always. Happy birthday!`",
	"`Another adventure filled year awaits you. Welcome it by celebrating your birthday with pomp and splendor. Wishing you a very happy and fun-filled birthday!`",
	"`May the joy that you have spread in the past come back to you on this day. Wishing you a very happy birthday!`",
	"`Happy birthday! Your life is just about to pick up speed and blast off into the stratosphere. Wear a seat belt and be sure to enjoy the journey. Happy birthday!`",
	"`This birthday, I wish you abundant happiness and love. May all your dreams turn into reality and may lady luck visit your home today. Happy birthday to one of the sweetest people I’ve ever known.`",
	"`May you be gifted with life’s biggest joys and never-ending bliss. After all, you yourself are a gift to earth, so you deserve the best. Happy birthday.`",
	"`Count not the candles…see the lights they give. Count not the years, but the life you live. Wishing you a wonderful time ahead. Happy birthday.`",
	"`Forget the past; look forward to the future, for the best things are yet to come.`",
	"`Birthdays are a new start, a fresh beginning and a time to pursue new endeavors with new goals. Move forward with confidence and courage. You are a very special person. May today and all of your days be amazing!`",
	"`Your birthday is the first day of another 365-day journey. Be the shining thread in the beautiful tapestry of the world to make this year the best ever. Enjoy the ride.`",
	"`Be happy! Today is the day you were brought into this world to be a blessing and inspiration to the people around you! You are a wonderful person! May you be given more birthdays to fulfill all of your dreams!`",
	"`You’re older today than yesterday but younger than tomorrow, happy birthday!`",
	"`Forget about the past, you can’t change it. Forget about the future, you can’t predict it. And forget about the present, I didn’t get you one. Happy birthday!`",
	"`Happy birthday to one of the few people whose birthday I can remember without a Facebook reminder.`",
	"`Don’t get all weird about getting older! Our age is merely the number of years the world has been enjoying us!`",
	"`As you get older three things happen. The first is your memory goes, and I can’t remember the other two. Happy birthday!`",
	"`Wishing you a day filled with happiness and a year filled with joy. Happy birthday!`",
	"`Sending you smiles for every moment of your special day…Have a wonderful time and a very happy birthday!`",
	"`Hope your special day brings you all that your heart desires! Here’s wishing you a day full of pleasant surprises! Happy birthday!`",
	"`On your birthday we wish for you that whatever you want most in life it comes to you just the way you imagined it or better. Happy birthday!`",
	"`Sending your way a bouquet of happiness…To wish you a very happy birthday!`",
	"`Wishing you a beautiful day with good health and happiness forever. Happy birthday!`",
	"`It’s a smile from me… To wish you a day that brings the same kind of happiness and joy that you bring to me. Happy birthday!`",
	"`On this wonderful day, I wish you the best that life has to offer! Happy birthday!`",
	"`I may not be by your side celebrating your special day with you, but I want you to know that I’m thinking of you and wishing you a wonderful birthday.`",
	"`I wish for all of your wishes to come true. Happy birthday!`",
	"`Many years ago on this day, God decided to send an angel to earth. The angel was meant to touch lives and that happened! Happy birthday my sweet angel!`",
	"`Sending you a birthday wish wrapped with all my love. Have a very happy birthday!`",
	"`Happy birthday to you. From good friends and true, from old friends and new, may good luck go with you and happiness too!`",
	"`A simple celebration, a gathering of friends; here wishing you great happiness and a joy that never ends.`",
	"`It’s always a treat to wish happy birthday to someone so sweet.`",
	"`Happy birthday to one of my best friends. Here’s to another year of laughing at our own jokes and keeping each other sane! Love you and happy birthday!`",
	"`On this special day, I raise a toast to you and your life. Happy birthday.`",
	"`You look younger than ever! Happy birthday!`",
	"`Words alone are not enough to express how happy I am you are celebrating another year of your life! My wish for you on your birthday is that you are, and will always be, happy and healthy. Don’t ever change! Happy birthday my dear.`",
	"`I can’t believe how lucky I am to have found a friend like you. You make every day of my life so special. It’s my goal to make sure your birthday is one of the most special days ever. I can’t wait to celebrate with you!`",
	"`A friend like you is more priceless than the most beautiful diamond. You are not only strong and wise, but kind and thoughtful as well. Your birthday is the perfect opportunity to show you how much I care and how grateful I am to have you in my life. Happy birthday!`",
	"`I hope that today, at your party, you dance and others sing as you celebrate with joy your best birthday`",
]

@Client.on_message(filters.command(["congo"], prefix) & filters.me)
async def cong(client: Client, message: Message):
    await message.edit(random.choice(CONGOS))
    
@Client.on_message(filters.command(["gdm"], prefix) & filters.me)
async def hello_morning(client: Client, message: Message):
    await message.edit(random.choice(GDMORNING))
    
@Client.on_message(filters.command(["gdn"], prefix) & filters.me)
async def hello_night(client: Client, message: Message):
    await message.edit(random.choice(GDNIGHT))
    
@Client.on_message(filters.command(["gaf"], prefix) & filters.me)
async def gnoon(client: Client, message: Message):
    await message.edit(random.choice(GDNOON))
    
@Client.on_message(filters.command(["hi"], prefix) & filters.me)
async def hillo(client: Client, message: Message):
    await message.edit(random.choice(HLLO))

@Client.on_message(filters.command(["hello"], prefix) & filters.me)
async def hello(client: Client, message: Message):
    await message.edit("╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╔╝╔╝╔╝╝\n╝╝╝╔╔╔╔╝╝╝╔╔╔╔╔╝╝╝╝╔╝╔╝╔╝\n╝╔██████╔███████╝╝╝╝╔╝╔╝╔\n╝╔██████╝╔█████╔╝╝╝╔╝╝╝╔╝\n╝╝╝████╝╝╝█████╝╝╝╔╝╔╝╝╝╔\n╝╝╔████████████╝╝╝╝╔╝╔╝╔╝\n╝╝╔████████████╝╝╝╔╝╔╝╔╝╔\n╝╝╝████╝╝╝█████╝╝╝╝╔╝╔╝╔╝\n╝╝██████╝╔█████╔╝╝╔╝╔╝╔╝╔\n╝███████╝███████╝╝╝╝╝╔╝╝╝\n╝╝╝╔╔╔╔╝╝╝╔╔╔╔╝╝╝╝╝╝╝╝╝╝╝\n╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝\n╔╝╝╝╝╝╝╝╝╝╔╔╔╔╔╔╔╔╔╔██╝╝╝\n╝╝╝╝╝╝╝╔╝╔█████████████╝╝\n╔╝╔╝╔╝╔╝╝╝╔█████╔╔╔╔███╝╝\n╝╔╝╔╝╔╝╔╝╝╝█████╝╝██╝█╔╝╝\n╔╝╔╝╔╝╔╝╝╝╝█████████╝╝╝╝╝\n╝╔╝╔╝╔╝╔╝╝╝█████████╝╝╝╝╝\n╔╝╔╝╔╝╔╝╝╝╝█████╝╝██╝╝╔╔╝\n╝╔╝╔╝╝╝╔╝╝╝█████╝╝╝╝╝███╝\n╔╝╔╝╔╝╔╝╝╝╔█████████████╝\n╝╔╝╝╝╔╝╝╝╔█████████████╝╝\n╔╝╝╝╔╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝\n╝╔╝╔╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝\n╝╝╔╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╔╝╔\n╝╔╝╝╝╔████████╝╝╝╝╝╔╝╔╝╔╝\n╔╝╝╝╝╔███████╔╝╝╝╝╔╝╔╝╔╝╔\n╝╔╝╝╝╝╝█████╝╝╝╝╝╔╝╔╝╔╝╔╝\n╔╝╔╝╝╝╝█████╔╝╝╝╝╝╝╝╔╝╔╝╔\n╝╔╝╔╝╝╝█████╔╝╝╝╝╝╝╝╝╔╝╝╝\n╔╝╔╝╝╝╝█████╝╝╝╝╔╔╝╝╔╝╔╝╔\n╝╔╝╔╝╝╝█████╝╝╝╝██╔╝╝╝╝╔╝\n╔╝╔╝╝╝╔███████████╔╝╝╝╔╝╔\n╝╔╝╝╝╔████████████╝╝╝╔╝╔╝\n╔╝╔╝╝╝╝╝╝╝╝╝╝╝╝╔╔╝╝╝╔╝╝╝╔\n╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╔╝╔╝\n╝╝╝╝╝╝╝╝╝╝╝╝╔╝╝╝╝╝╔╝╔╝╔╝╔\n╝╝╔██████╝╝╝╝╔╝╔╝╔╝╔╝╔╝╔╝\n╝████████╔╝╝╔╝╔╝╔╝╔╝╝╝╔╝╔\n╝╝╔█████╔╝╝╝╝╔╝╝╝╔╝╔╝╔╝╝╝\n╝╝╝█████╝╝╝╝╝╝╔╝╔╝╔╝╔╝╔╝╔\n╝╝╝█████╝╝╝╝╝╝╝╝╝╔╝╔╝╔╝╔╝\n╔╝╝█████╝╝╝╝╝╝╝╝╔╝╝╝╔╝╔╝╔\n╝╝╝█████╝╝╝╝██╝╝╝╔╝╔╝╝╝╔╝\n╝╝╝█████╔╝╝███╝╝╔╝╝╝╔╝╔╝╔\n╝╔████████████╝╝╝╔╝╝╝╔╝╔╝\n╝╔███████████╝╝╝╝╝╝╝╝╝╝╝╔\n╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝\n╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝╝\n╝╝╝╝╝╝╝╝╝╔████╝╝╝╔████╔╝╝\n╝╔╝╝╝╝╝╝███████╔████████╝\n╝╝╔╝╔╝╝█████████████████╝\n╝╔╝╔╝╝╝╔████████████████╝\n╝╝╔╝╔╝╝╝███████████████╔╝\n╝╝╝╔╝╔╝╝╝█████████████╔╝╝\n╔╝╔╝╝╝╝╝╝╝███████████╔╝╝╝\n╝╔╝╔╝╔╝╝╝╝╝█████████╝╝╝╝╝\n╔╝╔╝╝╝╔╝╔╝╝╝╝██████╝╝╝╝╝╔\n╝╔╝╔╝╔╝╔╝╝╝╝╝╝╔██╝╝╝╝╝╝╔╝\n╔╝╔╝╔╝╔╝╔╝╔╝╝╝╝╝╝╝╝╝╝╝╔╝╔\n╝╔╝╝╝╔╝╔╝╔╝╔╝╝╝╝╝╝╝╝╝╝╝╔╝")
   
@Client.on_message(filters.command(["hbd"], prefix) & filters.me)
async def urday(client: Client, message: Message):
    await message.edit(random.choice(HBDAY))
    
@Client.on_message(filters.command(["wc"], prefix) & filters.me)
async def wcart(client: Client, message: Message):
    await message.edit("▒█░░▒█ █▀▀ █░░ █▀▀ █▀▀█ █▀▄▀█ █▀▀\n▒█▒█▒█ █▀▀ █░░ █░░ █░░█ █░▀░█ █▀▀\n▒█▄▀▄█ ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀▀ ▀░░░▀ ▀▀▀")

modules_help["greetings"] = {
    "congo": "Say Congratulations",
    "gdm": "Say Good Morning",
    "gdn": "Say Good Night",
    "gaf": "Say Good Afternoon",
    "hi": "Fancy Hi/Hello",
    "hello": "Giant Hello Art",
    "hbd": "Say Happy Birthday",
    "wc": "Says Welcome"
}
