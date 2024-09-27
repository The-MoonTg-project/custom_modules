from pyrogram import Client, filters
import pubchempy as pcp
from utils.scripts import format_exc, import_library

pubchempy = import_library("pubchempy")



@Client.on_message(filters.command("camistry"))
async def fetch_chemical_data_with_visual(client, message):
    query = " ".join(message.text.split()[1:])  # Combine query words properly

    try:
        # Fetch chemical data by name
        results = pcp.get_compounds(query, 'name', record_type='3d')

        if results:
            compound = results[0]

            # Send chemical information without SMILES structure
            info = (
                f"**Chemical Data for {compound.iupac_name}**\n\n"
                f"**Molecular Formula:** {compound.molecular_formula}\n"
                f"**Molecular Weight:** {compound.molecular_weight}\n"
                f"**CID:** {compound.cid}\n"
                f"**Synonyms:** {', '.join(compound.synonyms[:5])}\n"
            )
            await message.reply(info)
        else:
            await message.reply(f"No chemical data found for the query: '{query}'")

    except pcp.PubChemHTTPError as http_err:
        await message.reply(f"HTTP error occurred: {str(http_err)}")

    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")



INATURALIST_API_URL = "https://api.inaturalist.org/v1/observations"

# Create the Pyrogram Client

# Function to get marine life details from iNaturalist API
def get_marine_life_details(species_name):
    params = {
        "taxon_name": species_name,
        "quality_grade": "research",
        "iconic_taxa": "Mollusca,Fish,Crustacea",
        "per_page": 1
    }

    response = requests.get(INATURALIST_API_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["total_results"] > 0:
            observation = data["results"][0]
            species = observation["taxon"]["name"]
            common_name = observation["taxon"]["preferred_common_name"]
            photo_url = observation["photos"][0]["url"] if observation["photos"] else "No photo available"
            description = observation["description"] if "description" in observation else "No description available."
            return {
                "species": species,
                "common_name": common_name,
                "photo_url": photo_url,
                "description": description
            }
        else:
            return {"error": "No marine life found for this species."}
    else:
        return {"error": f"Error {response.status_code}: Unable to connect to iNaturalist API."}

# Command handler for marine life details
# Command handler for marine life details
@app.on_message(filters.command("marine_life"))
async def marine_life_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("Please specify a species name. Example: /marine_life dolphin")
        return

    species_name = " ".join(message.command[1:])
    marine_life = get_marine_life_details(species_name)

    if "error" in marine_life:
        await message.reply_text(marine_life["error"])
    else:
        reply_text = (
            f"**Species**: {marine_life['species']}\n"
            f"**Common Name**: {marine_life['common_name']}\n"
            f"**Description**: {marine_life['description']}\n"
            f"[Photo Link]({marine_life['photo_url']})"
        )
        await message.reply_text(reply_text, disable_web_page_preview=False)
