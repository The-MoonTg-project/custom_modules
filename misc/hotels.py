import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import logging



from utils.scripts import import_library
from utils.misc import modules_help, prefix


serpapi = import_library("serpapi")
from serpapi import GoogleSearch


# Setup logging
logging.basicConfig(level=logging.INFO)


def search_hotels(location, check_in_date, check_out_date):
    params = {
        "engine": "google_hotels",
        "q": location,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "INR",
        "gl": "in",
        "hl": "en",
        "api_key": "****"  # Replace with your SerpApi key
    }
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if "properties" not in results:
        return "No hotels found for the given criteria."
    
    properties = results["properties"]
    hotel_list = []
    
    for property in properties:
        name = property.get("name", "No Name")
        description = property.get("description", "No description available.")
        logo = property.get("logo", "No logo available.")
        rate_per_night = property.get("rate_per_night", {})  # Updated to use new structure
        lowest = rate_per_night.get("lowest", "Not available")
        extracted_lowest = rate_per_night.get("extracted_lowest", "Not available")
        before_taxes_fees = rate_per_night.get("before_taxes_fees", "Not available")
        extracted_before_taxes_fees = rate_per_night.get("extracted_before_taxes_fees", "Not available")
        check_in_time = property.get("check_in_time", "Not available")
        check_out_time = property.get("check_out_time", "Not available")
        prices = property.get("prices", [])
        nearby_places = property.get("nearby_places", [])
        amenities = property.get("amenities", [])
        hotel_class = property.get("hotel_class", "Not available")
        extracted_hotel_class = property.get("extracted_hotel_class", "Not available")
        images = property.get("images", [])
        overall_rating = property.get("overall_rating", "Not available")
        reviews = property.get("reviews", 0)
        ratings = property.get("ratings", [])
        location_rating = property.get("location_rating", "Not available")
        reviews_breakdown = property.get("reviews_breakdown", [])
        property_token = property.get("property_token", "Not available")
        serpapi_property_details_link = property.get("serpapi_property_details_link", "Not available")
        type_property = property.get("type", "Not available")  # Added field for type
        
        # Additional Fields
        link = property.get("link", "No link available.")
        sponsored = property.get("sponsored", False)
        eco_certified = property.get("eco_certified", False)
        gps_coordinates = property.get("gps_coordinates", {})
        latitude = gps_coordinates.get("latitude", "Not available")
        longitude = gps_coordinates.get("longitude", "Not available")
        
        hotel_info = f"• 🏢{name}\n"
        hotel_info += f"🧾Description: {description}\n"
        hotel_info += f"💳Rate per Night: Lowest: {lowest}, Extracted Lowest: {extracted_lowest}, Before Taxes/Fees: {before_taxes_fees}, Extracted Before Taxes/Fees: {extracted_before_taxes_fees}\n"
        hotel_info += f"🕝Check-in Time: {check_in_time}\n"
        hotel_info += f"🕗Check-out Time: {check_out_time}\n"
        
        # Prices from various sources
        if prices:
            hotel_info += "Prices from different sources:\n"
            for price in prices:
                source = price.get("source", "Unknown")
                logo = price.get("logo", "No logo")
                rate = price.get("rate_per_night", {}).get("lowest", "Not available")
                hotel_info += f"  - Source: {source}, Logo: {logo}, Rate: {rate}\n"
        
        hotel_info += f"👀Hotel Class: {hotel_class} (Extracted: {extracted_hotel_class})\n"
        hotel_info += f"💠Overall Rating: {overall_rating}\n"
        hotel_info += f"👁️‍🗨️Reviews: {reviews}\n"
        
        # Ratings
        if ratings:
            hotel_info += "Rating Breakdown:\n"
            for rating in ratings:
                stars = rating.get("stars", "Unknown")
                count = rating.get("count", 0)
                hotel_info += f"  - {stars} stars: {count} reviews\n"
        
        # Location Rating
        hotel_info += f"🧭Location Rating: {location_rating}\n"
        
        # Reviews Breakdown
        if reviews_breakdown:
            hotel_info += "Reviews Breakdown:\n"
            for breakdown in reviews_breakdown:
                name = breakdown.get("name", "Unknown category")
                description = breakdown.get("description", "No description")
                positive = breakdown.get("positive", 0)
                negative = breakdown.get("negative", 0)
                neutral = breakdown.get("neutral", 0)
                hotel_info += f"  - {name}: {description}, Positive: {positive}, Negative: {negative}, Neutral: {neutral}\n"
        
        # Images
        if images:
            hotel_info += "Images:\n"
            for image in images:
                thumbnail = image.get("thumbnail", "No thumbnail")
                original_image = image.get("original_image", "No original image")
                hotel_info += f"  - Thumbnail: {thumbnail}, Original Image: {original_image}\n"
        
        # Amenities
        if amenities:
            hotel_info += "Amenities:\n"
            for amenity in amenities:
                hotel_info += f"  - {amenity}\n"
        
        hotel_info += "Nearby Places:\n"
        for place in nearby_places:
            place_name = place.get("name", "Unnamed place")
            for transport in place.get("transportations", []):
                transport_type = transport.get("type", "Unknown transport")
                transport_duration = transport.get("duration", "Unknown duration")
                hotel_info += f"  - {place_name}: {transport_type} ({transport_duration})\n"
        
        hotel_info += f"🔗Link: {link}\n"
        hotel_info += f"📎Logo: {logo}\n"
        hotel_info += f"🧰Sponsored: {sponsored}\n"
        hotel_info += f"☘️Eco-certified: {eco_certified}\n"
        hotel_info += f"📡GPS Coordinates: Latitude: {latitude}, Longitude: {longitude}\n"
        hotel_info += f"🪙Property Token: {property_token}\n"
        hotel_info += f"📱SerpApi Details Link: {serpapi_property_details_link}\n"
        hotel_info += "-" * 40
        
        hotel_list.append(hotel_info)
    
    return "\n\n".join(hotel_list)





# Command handler to trigger hotel search
@Client.on_message(filters.command(["hotels"], prefix) & filters.me)
async def hotel_search(client, message):
    # Expecting the user to provide location, check-in, and check-out dates
    try:
        args = message.text.split(" ", 1)[1].strip().split(",")
        if len(args) != 3:
            await message.reply("Please provide location, check-in date, and check-out date in the format:\n`{prefix}hotels location, check_in_date, check_out_date`")
            return

        location = args[0].strip()
        check_in_date = args[1].strip()
        check_out_date = args[2].strip()
        
        # Run the search
        response = search_hotels(location, check_in_date, check_out_date)
        
        # Try sending the response
        try:
            await message.reply(response)
        except MessageTooLong:
            # Save the large response to a file
            with open("hotel_info.txt", "w") as f:
                f.write(response)
            
            # Read general details to include in the caption
            general_details = "🏨 Here's the hotel information for your search results 🌍💼"
            
            # Send the file with a caption
            await message.reply_document(
                "hotel_info.txt",
                caption=f"<u><b>Hotel Information</b></u>:\n{general_details}",
            )
            
            # Clean up by removing the file
            os.remove("hotel_info.txt")
    
    except Exception as e:
        await message.reply(f"Error: {str(e)}")



modules_help["hotels"] = {
    "hotels [search hotels]*": "search hotels."
}

