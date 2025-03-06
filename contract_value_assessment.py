import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# List of pages to scrape - NOTE baseball-reference will rate limit when testing. Do not overuse.
urls = {
    "mlb_contracts": "https://www.spotrac.com/mlb/contracts/",
    "mlb_avgvalue": "https://www.spotrac.com/mlb/rankings/player/_/year/2025/sort/cap_base",
    "mlb_lengthofcontract": "https://www.spotrac.com/mlb/rankings/player/_/year/2025/sort/contract_length",
    "baseball_reference_largest_contracts": "https://www.baseball-reference.com/leaders/leaders_contract.shtml"
}

# Use environment variable for User-Agent, replace with your own directory and headers
headers = {"User-Agent": os.getenv("USER_AGENT")}
# Retrieve base directory from environment variable
base_dir = os.getenv("PYTHON_PROJECTS_DIR", os.path.join(os.path.expanduser("~"), "Documents", "Python"))

# Define project-specific output folder
project_folder = os.path.join(base_dir, "contract value analysis")
os.makedirs(project_folder, exist_ok=True)

# Define output file paths for player statistics
batter_stats_file = os.path.join(project_folder, "batter_statistics.csv")
pitcher_stats_file = os.path.join(project_folder, "pitcher_statistics.csv")

### **Functions for Extracting Different Data Formats**
def extract_table_format(table):
    """Extract data from standard table-based format."""
    if not table:
        return None

    headers_list = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = []

    for tr in table.find("tbody").find_all("tr"):
        first_col = tr.find("th")  # Check if first column is <th>
        cols = [td.text.strip() for td in tr.find_all("td")]

        if first_col:
            cols.insert(0, first_col.text.strip())  # Insert <th> value at start

        if len(cols) == len(headers_list):  # Ensure correct column count
            rows.append(cols)

    return pd.DataFrame(rows, columns=headers_list) if rows else None

# Spotrac avgvalue and lengthofcontract pages have a list-based format
def extract_list_format(soup):
    """Extract data from list-based table format (Spotrac)."""
    list_items = soup.find_all("li", class_="list-group-item")

    if not list_items:
        return None

    data = []
    for item in list_items:
        rank = item.find("div", class_="fs-3").text.strip() if item.find("div", class_="fs-3") else ""
        player = item.find("div", class_="link").text.strip() if item.find("div", class_="link") else ""
        team_position = item.find("small").text.strip() if item.find("small") else ""
        contract_value = item.find_all("span")[-1].text.strip() if item.find_all("span") else ""

        data.append([rank, player, team_position, contract_value])

    headers_list = ["Rank", "Player", "Team/Position", "Contract Value"]
    return pd.DataFrame(data, columns=headers_list) if data else None

# Baseball-Reference's largest contracts table has a unique format for first column
def extract_baseball_reference_format(table):
    """Extract data from Baseball-Reference's largest contracts table."""
    if not table:
        return None

    headers_list = [th.text.strip() for th in table.find("thead").find_all("th")]
    rows = []

    for tr in table.find("tbody").find_all("tr"):
        cols = [td.text.strip() for td in tr.find_all("td")]
        first_col = tr.find("th").text.strip() if tr.find("th") else ""
        cols.insert(0, first_col)  # Insert first column (ranking)

        if len(cols) == len(headers_list):  # Ensure correct number of columns
            rows.append(cols)

    return pd.DataFrame(rows, columns=headers_list) if rows else None

# Extract player names and profile URLs from Baseball-Reference contracts table
def extract_player_urls(table):
    """Extract player names and profile URLs from the Baseball-Reference contracts table."""
    players = []
    
    for tr in table.find("tbody").find_all("tr"):
        player_td = tr.find("td", {"data-stat": "player"})  # Correct field
        if player_td and player_td.find("a"):
            player_name = player_td.get_text(strip=True)  # Extract player name
            player_href = player_td.find("a")["href"]  # Extract relative URL
            player_url = "https://www.baseball-reference.com" + player_href  # Complete URL
            players.append((player_name, player_url))
    
    return players

# Extract player statistics from Baseball-Reference player profile pages, dependent on pitcher or batter stats.
def extract_player_stats(player_name, player_url, batter_file, pitcher_file):
    """Extract batting and/or pitching stats from a player's profile page."""
    time.sleep(3)  # Increase delay to reduce request blocking

    try:
        response = requests.get(player_url, headers=headers, timeout=10)  # Increased timeout
        response.encoding = 'utf-8'  # Ensure proper encoding

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Check for batting stats
            batter_table = soup.find("table", {"id": "players_standard_batting"})
            if batter_table:
                headers_batter = [th.text.strip() for th in batter_table.find("thead").find_all("th")]
                rows_batter = []

                for tr in batter_table.find("tbody").find_all("tr"):
                    cols = [td.text.strip() for td in tr.find_all("td")]
                    first_col = tr.find("th").text.strip() if tr.find("th") else ""
                    cols.insert(0, first_col)  # Add first column (Year, etc.)

                    if len(cols) == len(headers_batter):
                        rows_batter.append(cols)

                if rows_batter:
                    df_batter = pd.DataFrame(rows_batter, columns=headers_batter)
                    df_batter.insert(0, "Player", player_name)  # Add player name
                    df_batter.to_csv(batter_file, mode="a", header=not os.path.exists(batter_file), index=False)
                    print(f"✅ Batting stats added for {player_name}")

            # Check for pitching stats
            pitcher_table = soup.find("table", {"id": "players_standard_pitching"})
            if pitcher_table:
                headers_pitcher = [th.text.strip() for th in pitcher_table.find("thead").find_all("th")]
                rows_pitcher = []

                for tr in pitcher_table.find("tbody").find_all("tr"):
                    cols = [td.text.strip() for td in tr.find_all("td")]
                    first_col = tr.find("th").text.strip() if tr.find("th") else ""
                    cols.insert(0, first_col)  # Add first column (Year, etc.)

                    if len(cols) == len(headers_pitcher):
                        rows_pitcher.append(cols)

                if rows_pitcher:
                    df_pitcher = pd.DataFrame(rows_pitcher, columns=headers_pitcher)
                    df_pitcher.insert(0, "Player", player_name)  # Add player name
                    df_pitcher.to_csv(pitcher_file, mode="a", header=not os.path.exists(pitcher_file), index=False)
                    print(f"✅ Pitching stats added for {player_name}")

        else:
            print(f"❌ Failed to retrieve stats for {player_name} - HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        print(f"⏳ Timeout error for {player_name}, skipping...")
    except requests.exceptions.RequestException as e:
        print(f"⚠ Error retrieving {player_name}: {e}")

for filename, url in urls.items():
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to retrieve {url} - HTTP Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Content (first 500 characters):\n{response.text[:500]}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        if "baseball-reference.com" in url:
            table = soup.find("table", {"id": "largest_contracts"})
            if table:
                df = extract_baseball_reference_format(table)
                print(f"✔ Detected **Baseball-Reference Format** for {filename}")

                # Save Baseball-Reference contracts table
                if df is not None:
                    file_path = os.path.join(project_folder, f"{filename}.csv")
                    df.to_csv(file_path, index=False)
                    print(f"✅ Saved data to {file_path}")

                # Extract player statistics from profile URLs
                player_list = extract_player_urls(table)

                # Extract player stats and save them directly
                for player_name, player_url in player_list:
                    print(f"📊 Extracting stats for {player_name}...")
                    extract_player_stats(player_name, player_url, batter_stats_file, pitcher_stats_file)

            else:
                print(f"⚠ No table found for {filename}. Skipping.")

        else:
            table = soup.find("table", {"id": "table"})
            df = extract_table_format(table) if table and table.find("tr") else extract_list_format(soup)

            if df is not None:
                print(f"✔ Detected **TABLE or LIST FORMAT** for {filename}")
                
                # Save Spotrac tables
                file_path = os.path.join(project_folder, f"{filename}.csv")
                df.to_csv(file_path, index=False)
                print(f"✅ Saved data to {file_path}")
            else:
                print(f"⚠ No recognized structure found for {filename}. Skipping.")

    else:
        print(f"❌ Failed to retrieve: {url}")
