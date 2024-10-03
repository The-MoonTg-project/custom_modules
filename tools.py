from pyrogram import Client, filters
from pyrogram.types import Message
from pymongo import MongoClient
import re
import aiohttp
from pyrogram import enums
from utils.misc import modules_help, prefix


TMDB_API_KEY = " "


mongo_url_pattern = re.compile(r'mongodb(?:\+srv)?:\/\/[^\s]+')


@Client.on_message(filters.command("mongochk" ,prefix) & filters.me)
async def mongo_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Please enter your MongoDB URL after the command. Example: /mongochk your_mongodb_url")
        return

    mongo_url = message.command[1]
    if re.match(mongo_url_pattern, mongo_url):
        try:
            # Attempt to connect to the MongoDB instance
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
            client.server_info()  # Will cause an exception if connection fails
            await message.reply("𝗠𝗼𝗻𝗴𝗼𝗗𝗕 𝗨𝗥𝗟 𝗶𝘀 𝘃𝗮𝗹𝗶𝗱 𝗮𝗻𝗱 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹✅")
        except Exception as e:
            await message.reply(f"Failed to connect to MongoDB: {e}")
    else:
        await message.reply("𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗠𝗼𝗻𝗴𝗼𝗗𝗕 𝗨𝗥𝗟 𝗳𝗼𝗿𝗺𝗮𝘁💔")


@Client.on_message(filters.command("tmdb" ,prefix) & filters.me)
async def movie_command(client, message):
    try:
        # Check if the user provided a movie name after the /movie command
        if len(message.command) > 1:
            movie_name = " ".join(message.command[1:])

            # Fetch movie information from TMDb API
            movie_info = get_movie_info(movie_name)

            # Send the movie information as a reply
            await message.reply_text(movie_info)
        else:
            await message.reply_text("Please enter a movie name after the /movie command.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

def get_movie_info(movie_name):
    tmdb_api_url = f"https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": movie_name}
    
    response = requests.get(tmdb_api_url, params=params)
    data = response.json()

    if data.get("results"):
        # Get information about the first movie in the results
        movie = data["results"][0]
        
        # Fetch additional details using the movie ID
        details_url = f"https://api.themoviedb.org/3/movie/{movie['id']}"
        details_params = {"api_key": TMDB_API_KEY}
        details_response = requests.get(details_url, params=details_params)
        details_data = details_response.json()
        
        # Extract relevant information
        title = details_data.get("title", "N/A")
        release_date = details_data.get("release_date", "N/A")
        overview = details_data.get("overview", "N/A")
        providers = details_data.get("providers", "N/A")
        vote_average = details_data.get("vote_average", "N/A")
        
        # Extract actor names
        cast_url = f"https://api.themoviedb.org/3/movie/{movie['id']}/credits"
        cast_params = {"api_key": TMDB_API_KEY}
        cast_response = requests.get(cast_url, params=cast_params)
        cast_data = cast_response.json()
        actors = ", ".join([actor["name"] for actor in cast_data.get("cast", [])])
        
        # Extract total collection
        revenue = details_data.get("revenue", "N/A")
        
        # Format and return movie information
        info = (
            f"Title: {title}\n\n"
            f"Release Date: {release_date}\n\n"
            f"Overview: {overview}\n\n"
            f"Vote Average: {vote_average}\n\n"
            f"Actor Names: {actors}\n\n"
            f"Total Collection: {revenue}\n\n"
            f"Available Platforms: {providers}\n"
        )
        return info
    else:
        return "Movie not found or API request failed."


modules_help["tools"] = {
    "tmdb [movie name]": "get the movie name & details"
    "mongochk [url]" : " get mongo url alive or dead "
}
