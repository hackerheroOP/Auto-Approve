from os import environ
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, ChatPermissions, ChatJoinRequest
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv("stack.env")
ADMIN_USER_ID = int(environ['ADMIN_USER_ID'])


mongo_client = MongoClient(environ["MONGODB_URI"])
db = mongo_client['AutoApprove']
users_collection = db.users


#check 
check = users_collection.find_one({"user_id": ADMIN_USER_ID})
if check is None or check.get('role') != 'admin':
    users_collection.update_one(
        {"user_id": ADMIN_USER_ID},
        {"$set": {"user_id": ADMIN_USER_ID, "role": "admin"}},
        upsert=True
    )
    print('Added Admin In Sudo List')


bot = Client(
    "Auto Approved Bot",
    bot_token=environ["BOT_TOKEN"],
    api_id=int(environ["API_ID"]),
    api_hash=environ["API_HASH"]
)


@bot.on_message(filters.private & filters.command(["start"]))
async def start(client: bot, message: Message):
    approvedbot = await client.get_me()
    button = [
        [InlineKeyboardButton("➕️ Add Me To Your Chat ➕️", url=f"http://t.me/{approvedbot.username}?startgroup=botstart")],
        [InlineKeyboardButton("More about the Creator 👨‍💻", url="https://t.me/pro_morningstar")],
        [InlineKeyboardButton('Updates', url='https://t.me/Movies_Unloaded_Network'), InlineKeyboardButton('Support Group', url='https://t.me/Movies_Request_02')]
    ]
    await client.send_message(chat_id=message.chat.id, text=f"**Hello {message.from_user.mention}!\n\nI am the Auto Approver Join Request Bot. \nJust [Add Me To Your Group Channel](http://t.me/{approvedbot.username}?startgroup=botstart) to get started.**", reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)

@bot.on_chat_join_request(filters.group | filters.channel)
async def autoapprove(client: bot, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    print(f"{user.first_name} in {chat.title} Joined 🤝")
    await client.approve_chat_join_request(chat_id=chat.id, user_id=user.id)
    await client.send_message(chat_id=user.id, text=f"Greetings, {user.mention}!\n\nWe are delighted to inform you that your request to join {chat.title} has been approved!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Bot Support', url="https://t.me/Movies_Request_02"), InlineKeyboardButton('Bot Updates', url='https://t.me/Movies_Unloaded_Network')], [InlineKeyboardButton('Bot Dev', url='https://t.me/pro_morningstar')]]))
    users_collection.update_one(
        {"user_id": user.id},
        {"$set": {"user_id": user.id, "role": "user"}},
        upsert=True
    )

@bot.on_message(filters.command(["stats"]))
async def stats_command(client: bot, message: Message):
    admin_user = users_collection.find_one({"user_id": message.from_user.id, "role": "admin"})
    if admin_user:
        total_users = users_collection.count_documents({})
        await message.reply(f"Total users in the database: {total_users}")
 

@bot.on_message(filters.command(["addsudo"]))
async def addsudo_command(client: bot, message: Message):
    admin_user = users_collection.find_one({"user_id": message.from_user.id, "role": "admin"})
    if admin_user:
        replied_user_id = None
        if message.reply_to_message:
            replied_user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            replied_user_id = int(message.command[1])
        
        if replied_user_id:
            user_data = users_collection.find_one({"user_id": replied_user_id})
            if user_data:
                if user_data["role"] == "admin":
                    await message.reply("User is already an admin.")
                else:
                    users_collection.update_one(
                        {"user_id": replied_user_id},
                        {"$set": {"role": "admin"}}
                    )
                    await message.reply("User role updated to admin.")
            else:
                await message.reply("User not found in the database.")
        else:
            await message.reply("Please reply to a message or provide a user ID.")
    

@bot.on_message(filters.command(["rmsudo"]))
async def rmsudo_command(client: bot, message: Message):
    admin_user = users_collection.find_one({"user_id": message.from_user.id, "role": "admin"})
    if admin_user:
        replied_user_id = None
        if message.reply_to_message:
            replied_user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            replied_user_id = int(message.command[1])
        
        if replied_user_id:
            user_data = users_collection.find_one({"user_id": replied_user_id})
            if user_data:
                if user_data["role"] == "user":
                    await message.reply("User is already a regular user.")
                else:
                    users_collection.update_one(
                        {"user_id": replied_user_id},
                        {"$set": {"role": "user"}}
                    )
                    await message.reply("User role updated to user.")
            else:
                await message.reply("User not found in the database.")
        else:
            await message.reply("Please reply to a message or provide a user ID.")


print("Auto Approved Bot")
bot.run()
