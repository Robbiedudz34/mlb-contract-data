# MLB Contract & Player Stats Scraper

## 📌 Overview
This script extracts MLB contract details and player statistics from multiple sources, including Spotrac and Baseball-Reference. It dynamically detects different web structures (tables, lists) and saves data into structured CSV files for further analysis. The base use of websites can be changed, with enabling different tags for pulling data.

## 🚀 Features
- Extracts contract data from **Spotrac** (tables & list-based structures)
- Extracts **largest contracts** from **Baseball-Reference**
- Scrapes **player statistics (batting & pitching)** from Baseball-Reference player profiles
- Automatically handles **rate limits** and prevents request blocking
- Saves data to **organized CSV files** for easy analysis

## 🛠️ Requirements
- **Python 3.8+**
- Required libraries (install using pip):
  ```sh
  pip install requests beautifulsoup4 pandas
  ```
- Environment variable for `USER_AGENT` to prevent detection
- Saved file set to an environment variable for security, change to your preferred location

### **Saved CSVs:**
- `mlb_contracts.csv` – Spotrac MLB contracts
- `mlb_avgvalue.csv` – MLB average contract value rankings
- `mlb_lengthofcontract.csv` – MLB contract length rankings
- `baseball_reference_largest_contracts.csv` – Largest contracts (Baseball-Reference)
- `batter_statistics.csv` – Player batting stats
- `pitcher_statistics.csv` – Player pitching stats

## ⚙️ How It Works
1. **Scrapes Contract Data**
   - Spotrac pages are processed dynamically for **table** or **list** structures.
   - Baseball-Reference **largest contracts table** is extracted.

2. **Extracts Player Profiles**
   - Finds and stores player profile URLs from Baseball-Reference.

3. **Scrapes Player Stats**
   - Detects **batting (`players_standard_batting`)** or **pitching (`players_standard_pitching`)** data.
   - Saves data into corresponding CSV files.

## 📌 Usage Instructions
1. Clone the repository:
   ```sh
   git clone https://github.com/your-username/mlb-contract-scraper.git
   cd mlb-contract-scraper
   ```
2. Set up the environment variable for `USER_AGENT` and set output location:
   ```sh
   export USER_AGENT="Your_User_Agent_String"
   ```
   *(For Windows: `set USER_AGENT=Your_User_Agent_String`)*
3. Run the script:
   ```sh
   python contract_scraper.py
   ```
4. Check the output CSV files in the specified directory.

## 🔄 Handling Rate Limits
- If `429 Too Many Requests` occurs, the script will **wait before retrying**.
- Increase delay in `time.sleep(random.uniform(5, 10))` if needed.
- Manually export data from Baseball-Reference if necessary.

## 🔧 Future Improvements
- Implement **proxies** for better scraping efficiency.
- Add **historical player performance analysis**.
- Create **data visualization** for contract value insights.

---
**📩 Contact & Contributions**
Feel free to contribute or report issues on GitHub!
