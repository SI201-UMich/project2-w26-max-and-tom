# SI 201 HW4 (Library Checkout System)
# Your name: Haoxiang Huang
# Your student id: 6885 7185
# Your email: tomhuang@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""

def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Tom Huang
    # ==============================
    
    # Open HTML from path (Added encoding just in case said above)
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse through (from Runestone) (bug fix to read from the content in first iteration, not the html path)
    soup = BeautifulSoup(content, "html.parser")

    # Empty listing
    listings = []
    
    # Find all the listing cards containing titles and links (rewrote format from first wrong iteration)
    for tag in soup.find_all("a", href=True):
        href = tag.get("href", "")

        # Extract the listing ID from the URL (the number after /rooms/)
        if "/rooms/" in href:
            parts = href.split("/rooms/")

            # Check and strip to match (Claude helped to correct the syntax for listing id below from first iteration)
            if len(parts) > 1:
                listing_id = parts[1].split("?")[0].strip() 

                # Get the title from the tag's text content
                title = tag.get_text(" ", strip=True)
                
                if listing_id.isdigit() and title:
                    listings.append((title, listing_id))

    return listings

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================

def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Tom Huang
    # ==============================

    # Build the file path from the listing_id (Copied the initial set up from first function)
    html_path = f"listing_{listing_id}.html"
    
    with open(html_path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    '''
    Policy Numbre
    '''
    policy_number = "Exempt"

    for tag in soup.find_all(string=True):
        text = tag.strip()
        if "pending" in text.lower():
            policy_number = "Pending"
            break

        # RegEx to match (Claude helped fixing the not enclosed RegEx)
        if re.search(r'20\d{2}-00\d{4}STR', text) or re.search(r'STR-000\d{4}', text):
            match = re.search(r'(20\d{2}-00\d{4}STR|STR-000\d{4})', text)
            if match:
                policy_number = match.group(1)
                break

    '''
    Host Type
    '''
    host_type = "regular"

    for tag in soup.find_all(string=True):
        if "superhost" in tag.strip().lower():
            host_type = "Superhost"
            break

    '''
    Host name
    '''
    host_name = ""
    for tag in soup.find_all(string=True):
        text = tag.strip()

        # Host name typically appears after Hosted by
        if "hosted by" in text.lower():
            
            # Sometimes the name is in the same string, sometimes in the next sibling
            name = re.sub(r'(?i)hosted by\s*', '', text).strip()
            if name:
                host_name = name
            else:

                # Try the next sibling tag's text
                parent = tag.parent
                if parent and parent.next_sibling:
                    host_name = parent.next_sibling.get_text(strip=True)
        break

    '''
    Room Type
    '''
    # Based on listing subtitle: Private -> Private Room, Shared -> Shared Room, else Entire Room
    room_type = "Entire Room"
    for tag in soup.find_all(string=True):
        text = tag.strip().lower()
        if "private" in text:
            room_type = "Private Room"
            break
        if "shared" in text:
            room_type = "Shared Room"
            break

    # Location Rating (Fixed it so it can contain float numbers)
    location_rating = 0.0
    for tag in soup.find_all(string=True):
        text = tag.strip().lower()
        if "location" in text:

            # Look for a float number near this tag
            parent = tag.parent
            if parent:
                siblings = parent.find_next_siblings()
                for sib in siblings:
                    sib_text = sib.get_text(strip=True)
                    match = re.search(r'\d\.\d', sib_text)
                    if match:
                        location_rating = float(match.group())
                        break
            break

    # Return the collection from instruction (I spaved it out so I)
    return {
            listing_id: 
                {
                "policy_number": policy_number,
                "host_type": host_type,
                "host_name": host_name,
                "room_type": room_type,
                "location_rating": location_rating
                }
            }

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Tom Huang
    # ==============================

    # Empty list
    results = []

    # Load pairing from html_path
    basic_listings = load_listing_results(html_path)

    # For each listing id, scrape details from saved html info (Claude helped figure out the inner dict)
    for title, listing_id in basic_listings:
        details_dict = get_listing_details(listing_id)
        details = details_dict.get(listing_id, {})

        policy_number = details.get("policy_number", "Pending")
        host_type = details.get("host_type", "regular")
        host_name = details.get("host_name", "")
        room_type = details.get("room_type", "")
        location_rating = details.get("location_rating", 0.0)

        results.append(
            (title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        )

    return results

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Max VanDoren
    # ==============================

    sortedData = sorted(data, key=lambda x: x[6], reverse=True)

    outFile = open(filename, 'w', encoding="utf-8-sig")
    csvWriter = csv.writer(outFile)

    csvWriter.writerow(['Listing Title', 'Listing ID', 'Policy Number', 'Host Type', 'Host Name', 'Room Type', 'Location Rating'])

    for listing in sortedData:
        csvWriter.writerow(listing)

    outFile.close()
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Max VanDoren
    # ==============================
    
    roomTypeRatings = {}

    for listing in data:
        if listing[6] != 0.0:
            if listing[5] not in roomTypeRatings:
                roomTypeRatings[listing[5]] = [0, 0]
            roomTypeRatings[listing[5]][0] += listing[6]
            roomTypeRatings[listing[5]][1] += 1

    for roomType, totalRatings in roomTypeRatings.items():
        roomTypeRatings[roomType] = totalRatings[0] / totalRatings[1]

    return roomTypeRatings

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE: Max VanDoren
    # ==============================
    invalidPolicies = []


    for listing in data:
        if listing[2] == 'Pending' or listing[2] == 'Exempt':
            continue
        else:
            if re.search(r'^20\d{2}-00\d{4}STR$', listing[2]) or re.search(r'^STR-000\d{4}$', listing[2]):
                continue
            else:
                invalidPolicies.append(listing[1])

    return invalidPolicies

    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    titleList = []

    r = requests.get('https://scholar.google.com/scholar?hl=en&as_sdt=0%2C23&q=airbnb&btnG=')
    bs = BeautifulSoup(r.content, 'html.parser')

    tagList = bs.findall('h3', class_="gs_rt")

    for tag in tagList:
        titleList.append(tag.text.strip())

    return titleList
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        pass

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        pass

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        pass

    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        # TODO: Read the CSV back in and store rows in a list.
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        pass

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        pass


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)