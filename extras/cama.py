from pyrogram import Client, filters
import requests

from utils.scripts import format_exc, import_library

from utils.misc import modules_help, prefix

pcp = import_library("pubchempy")

INATURALIST_API_URL = "https://api.inaturalist.org/v1/observations"


def get_marine_life_details(species_name):
    params = {
        "taxon_name": species_name,
        "quality_grade": "research",
        "iconic_taxa": "Mollusca,Fish,Crustacea",
        "per_page": 1,
    }

    response = requests.get(INATURALIST_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["total_results"] > 0:
            observation = data["results"][0]
            species = observation["taxon"]["name"]
            common_name = observation["taxon"]["preferred_common_name"]
            photo_url = (
                observation["photos"][0]["url"]
                if observation["photos"]
                else "No photo available"
            )
            description = (
                observation["description"]
                if "description" in observation
                else "No description available."
            )
            return {
                "species": species,
                "common_name": common_name,
                "photo_url": photo_url,
                "description": description,
            }
        else:
            return {"error": "No marine life found for this species."}
    else:
        return {
            "error": f"Error {response.status_code}: Unable to connect to iNaturalist API."
        }


@Client.on_message(filters.command("camistry", prefix) & filters.me)
async def fetch_chemical_data_with_visual(_, message):
    query = " ".join(message.text.split()[1:])  # Combine query words properly

    try:
        # Fetch chemical data by name
        results = pcp.get_compounds(query, "name", record_type="3d")

        if results:
            compound = results[0]

            # Send chemical information without SMILES structure
            info = (
                f"<b>Chemical Data for {compound.iupac_name}</b>\n\n"
                f"<b>Molecular Formula:</b> <code>{compound.molecular_formula}</code>\n"
                f"<b>Molecular Weight:</b> <code>{compound.molecular_weight}</code>\n"
                f"<b>CID:</b> <code>{compound.cid}</code>\n"
                f"<b>Synonyms:</b> <code>{', '.join(compound.synonyms[:5])}</code>\n"
            )
            await message.edit_text(info)
        else:
            await message.edit_text(f"No chemical data found for the query: '{query}'")

    except pcp.PubChemHTTPError as http_err:
        await message.edit_text(f"HTTP error occurred: {format_exc(http_err)}")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("marinelife", prefix) & filters.me)
async def marine_life_command(_, message):
    if len(message.command) < 2:
        await message.edit_text(
            f"Please specify a species name. Example: {prefix}marinelife dolphin"
        )
        return

    species_name = " ".join(message.command[1:])
    marine_life = get_marine_life_details(species_name)

    if "error" in marine_life:
        await message.edit_text(marine_life["error"])
    else:
        reply_text = (
            f"<b>Species</b>: <code>{marine_life['species']}</code>\n"
            f"<b>Common Name</b>: <code>{marine_life['common_name']}</code>\n"
            f"<b>Description</b>: <code>{marine_life['description']}</code>\n"
            f"<a href='{marine_life['photo_url']}'>Photo</a>"
        )
        await message.edit_text(reply_text)


modules_help["cama"] = {
    "camistry [text]": " getting camicale info",
    "marinelife [text]": " getting marinelife info",
}
