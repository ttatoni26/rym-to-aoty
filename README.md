# Music Ratings Transfer

This project allows you to transfer your album ratings from RateYourMusic (RYM) to Album of the Year (AOTY) automatically using Python and Selenium.

## Features
- Reads your exported RYM ratings from a CSV file
- Uses an undetected Chrome driver to bypass Cloudflare
- Searches for albums on AOTY and submits your ratings

## Requirements
- Python 3.8+
- Google Chrome browser
- ChromeDriver (automatically handled by `undetected-chromedriver`)

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/ttatoni26/rym-to-aoty.git
   cd music_ratings
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Export your ratings from RateYourMusic as a CSV file.
2. Place the CSV file in the project directory.
3. Run the script:
   ```sh
   python main.py
   ```
4. Enter the path to your CSV file when prompted (e.g., `user-music-export.csv`).
5. Log in to your AOTY account in the opened browser window, confirm with enter in the terminal.
6. The script will automatically transfer your ratings.

## Notes
- You must log in to AOTY manually when prompted.
- The script will attempt to match albums and submit ratings. Some albums may not be found or may require manual review.

## Troubleshooting
- Make sure your CSV file is properly formatted and contains ratings.
- If Chrome or ChromeDriver versions mismatch, update your browser or the `undetected-chromedriver` package.

## License
MIT
