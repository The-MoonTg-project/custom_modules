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
