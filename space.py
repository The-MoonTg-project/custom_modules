# Space-Track.org credentials
SPACETRACK_USER = "" # Your Space-Track username
SPACETRACK_PASS = ""  # Your Space-Track password

# Function to login to Space-Track.org and get an authentication session
def space_track_login():
    session = requests.Session()
    login_url = "https://www.space-track.org/ajaxauth/login"
    data = {
        'identity': SPACETRACK_USER,
        'password': SPACETRACK_PASS,
    }
    response = session.post(login_url, data=data)
    if response.status_code == 200:
        return session
    return None

# Function to fetch satellite details from Space-Track.org
def fetch_satellite_data(satellite_id):
    session = space_track_login()
    if not session:
        return None

    query_url = f"https://www.space-track.org/basicspacedata/query/class/tle_latest/NORAD_CAT_ID/{satellite_id}/orderby/epoch desc/limit/1/format/json"
    response = session.get(query_url)
    
    if response.status_code == 200:
        return response.json()[0]  # Return the latest TLE data
    return None

# Function for live tracking (returns satellite position over time)


# Command to get satellite data (TLE data, launch date, etc.)
@app.on_message(filters.command("satellite"))
async def get_satellite_info(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please provide a satellite ID.")
        return

    satellite_id = message.command[1]
    data = fetch_satellite_data(satellite_id)

    if data:
        info = f"""
        Satellite Name: {data['OBJECT_NAME']}
        NORAD ID: {data['NORAD_CAT_ID']}
        Epoch Time: {data['EPOCH']}
        Inclination: {data['INCLINATION']}°
        Right Ascension: {data['RA_OF_ASC_NODE']}°
        Eccentricity: {data['ECCENTRICITY']}
        Orbital Period: {data['MEAN_MOTION']}
        """
        await message.reply_text(info)
    else:
        await message.reply_text("Satellite data not found.")
      
