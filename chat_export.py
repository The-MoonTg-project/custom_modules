from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix

import os
import datetime

# Function to generate HTML content
def generate_html(messages, owner_username, other_username, export_datetime):
    html = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DM with {owner_username}, {other_username}</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css">
    <style>
        body {{
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            background-color: #f4f4f9;
            color: #333;
            transition: background-color 0.3s, color 0.3s;
        }}
        body.dark {{
            background-color: #0d1117;
            color: #c9d1d9;
        }}
        .container {{
            max-width: 800px;
            margin: 20px auto;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: background-color 0.3s;
        }}
        body.dark .container {{
            background: #161b22;
        }}
        .message {{
            border-bottom: 1px solid #eee;
            padding: 10px 0;
            display: flex;
            flex-direction: column;
            word-wrap: break-word;
        }}
        .message:last-child {{
            border-bottom: none;
        }}
        .author {{
            font-weight: bold;
            transition: color 0.3s;
        }}
        .author.owner {{
            color: #C9DABF;
        }}
        .author.other {{
            color: #F7E7DC;
        }}
        .text {{
            margin: 5px 0 0 0;
        }}
        .timestamp {{
            font-size: 0.8em;
            color: #555;
            align-self: flex-end;
            transition: color 0.3s;
        }}
        body.dark .timestamp {{
            color: #8b949e;
        }}
        .search-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 10px;
        }}
        .toggle-button {{
            position: fixed;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            cursor: pointer;
            color: inherit;
            font-size: 1.5em;
        }}
        .search-bar {{
            width: 100%;
            max-width: 800px;
            padding: 10px;
            border-radius: 4px;
            border: 1px solid #ccc;
            margin-bottom: 10px;
            transition: background-color 0.3s, color 0.3s;
        }}
        body.dark .search-bar {{
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
        }}
        .sort-checkbox {{
            margin-top: 10px;
        }}
        h1 {{
            font-size: 1.5em;
            margin-bottom: 10px;
            text-align: center;
        }}
        .footer {{
            font-size: 0.8em;
            color: #555;
            margin-top: 20px;
            text-align: center;
        }}
        body.dark .footer {{
            color: #8b949e;
        }}
    </style>
    <script>
        function toggleTheme() {{
            document.body.classList.toggle('dark');
            localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
        }}

        function searchMessages() {{
            let input = document.getElementById('searchInput').value.toLowerCase();
            let messages = document.getElementsByClassName('message');
            for (let i = 0; i < messages.length; i++) {{
                let text = messages[i].innerText.toLowerCase();
                if (text.includes(input)) {{
                    messages[i].style.display = '';
                }} else {{
                    messages[i].style.display = 'none';
                }}
            }}
        }}

        function sortMessages() {{
            let checkbox = document.getElementById('sortCheckbox');
            let order = checkbox.checked ? 'asc' : 'desc';
            let messages = Array.from(document.getElementsByClassName('message'));
            messages.sort((a, b) => {{
                let dateA = new Date(a.getAttribute('data-timestamp'));
                let dateB = new Date(b.getAttribute('data-timestamp'));
                return order === 'asc' ? dateA - dateB : dateB - dateA;
            }});

            let container = document.getElementById('messages');
            container.innerHTML = '';
            messages.forEach(msg => container.appendChild(msg));
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            if (localStorage.getItem('theme') === 'dark') {{
                document.body.classList.add('dark');
            }}
            document.getElementById('sortCheckbox').addEventListener('change', sortMessages);
        }});
    </script>
</head>
<body>
    <button class="toggle-button" onclick="toggleTheme()">
        <i class="fas fa-adjust"></i>
    </button>
    <div class="container">
        <h1>DM with {owner_username}, {other_username}</h1>
        <div class="search-container">
            <input type="text" id="searchInput" class="search-bar" onkeyup="searchMessages()" placeholder="Search for messages...">
            <label class="sort-checkbox">
                <input type="checkbox" id="sortCheckbox"> Sort by Date
            </label>
        </div>
        <div id="messages">
    '''
    for msg in messages:
        author_class = "owner" if msg['author_color'] == "#C9DABF" else "other"
        html += f'''
        <div class="message" data-timestamp="{msg['timestamp']}">
            <div class="author {author_class}">{msg['author']}</div>
            <div class="text">{msg['text']}</div>
            <div class="timestamp">{msg['timestamp']}</div>
        </div>
        '''
    html += f'''
        </div>
        <div class="footer">
            Exported on {export_datetime}
        </div>
    </div>
</body>
</html>
    '''
    return html

# Command to export conversation
@Client.on_message(filters.command("exp_chat", prefix) & filters.me)
async def export_chat(client: Client, message: Message):
    please_wait = await message.edit("Please wait...")
    chat_id = message.chat.id
    owner = await client.get_me()
    owner_username = owner.username
    other_username = (await client.get_chat(chat_id)).title or (await client.get_chat(chat_id)).first_name or "Unknown"
    messages = []
    
    async for msg in client.get_chat_history(chat_id, limit=None):
        author_color = "#C9DABF" if msg.from_user and msg.from_user.id == owner.id else "#F7E7DC"
        messages.append({
            "author": msg.from_user.first_name if msg.from_user else "Unknown",
            "author_color": author_color,
            "text": msg.text or msg.caption or "",
            "timestamp": msg.date.strftime("%Y-%m-%d %H:%M:%S")
        })

    export_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html_content = generate_html(messages[::-1], owner_username, other_username, export_datetime)  # Reverse to maintain chronological order

    file_name = f"chat_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    file_path = os.path.join(os.getcwd(), file_name)
    
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    await client.send_document(chat_id, file_path)
    os.remove(file_path)  # Clean up the file after sending
    await please_wait.delete()

modules_help["export_chat"] = {
    "exp_chat": "Export all messages in the chat to a HTML file"
}
