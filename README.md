# 🏀 NBA Player Analytics - Value for Money (2025-26)

A professional Business Intelligence dashboard designed to evaluate NBA players' "Value for Money". This application compares real-time on-court performance with current salaries to identify undervalued and overpaid players.

## 👥 Project Team
* **Nathan GEHIN**
* **Kevin KONAN**
* **Marius HAVAN**

## 🌟 Key Features

1. **Automated Web Scraping**: Integrated system using `stats.nba.com` data. The application automatically detects if local data is outdated and triggers a fresh scrape and merge at startup.
2. **"Wemby-Proof" Defensive Scoring**: A custom weighted algorithm prioritizing Rim Protection (Blocks 50%) and physical presence (Rebounds 35%) to accurately reflect the impact of elite defenders.
3. **Intelligent Data Merging**: Robust system capable of reconciling international characters (*Dončić*) and abbreviated name formats (*V. Wembanyama*).
4. **Value Indicators**:
    * 🟢 **Underpaid**: Performance far exceeds current salary.
    * 🟡 **Well Paid**: Salary is perfectly aligned with statistical output.
    * 🔴 **Overpaid**: Statistical output does not justify the contract cost.

## 🏗️ Project Architecture

The project is structured to ensure clean separation between data acquisition, processing, and visualization:



```text
NBA_Value_for_money/
├── nba_app.py              # Main Entry Point: Flask server & Web Interface
├── requirements.txt        # Project dependencies (Pandas, Flask, Openpyxl)
├── README.md               # Documentation (English)
├── LICENSE                 # MIT License
├── .gitignore              # Files excluded from version control
│
├── data/                   # Data Storage
│   ├── NBA_Stat.xlsx       # Raw statistics from scraper
│   ├── NBA_Salary.xlsx     # Raw salary data
│   └── nba_data.xlsx       # Final processed and merged dataset
│
├── Scripts/                # Core Logic & Processing
│   ├── merge_data.py       # Handles data cleaning and fuzzy name matching
│   └── utils_nba.py        # Algorithmic core (Impact scores & VFM metrics)
│
└── Scrapers/               # Data Acquisition
    └── scrapers_stat.py    # Automated web scraper for NBA stats
