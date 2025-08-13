import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import quote
import re

class RYMtoAOTYTransfer:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        self.driver = None
        self.ratings_data = []
        
    def setup_driver(self):
        options = uc.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize undetected chromedriver
        self.driver = uc.Chrome(options=options, version_main=None)
        self.driver.maximize_window()
        
    def load_csv_data(self):
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    if row.get('Rating') and row['Rating'].strip():
                        try:
                            
                            rym_rating = float(row['Rating'])
                            aoty_rating = int(rym_rating * 10)
                            
                            
                            album_data = {
                                'artist': row.get('First Name', '').strip(),
                                'artist_last': row.get('Last Name', '').strip(),
                                'album': row.get('Title', '').strip(),
                                'release_date': row.get('Release_Date', '').strip(),
                                'rating': aoty_rating,
                                'rym_rating': rym_rating
                            }
                            
                            
                            if album_data['artist_last']:
                                album_data['full_artist'] = f"{album_data['artist']} {album_data['artist_last']}"
                            else:
                                album_data['full_artist'] = album_data['artist']
                            
                            self.ratings_data.append(album_data)
                            
                        except ValueError:
                            print(f"Invalid rating value: {row.get('Rating')}")
                            
            print(f"Loaded {len(self.ratings_data)} albums with ratings from CSV")
            return True
            
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_file_path}")
            return False
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def wait_for_login(self):
        print("Opening Album of the Year website...")
        self.driver.get("https://www.albumoftheyear.org")
        
        print("\n" + "="*50)
        print("Please log in to your AOTY account manually.")
        print("Press ENTER when you're logged in and ready to continue...")
        print("="*50)
        input()
        
        print("Login confirmed. Starting rating transfer...")

        
    def search_and_click_album(self, artist, album, year):
        try:
            
            search_query = f"{artist} {album}"
            search_url = f"https://www.albumoftheyear.org/search/?q={quote(search_query)}"
            
            self.driver.get(search_url)
            time.sleep(1)  # Wait for results to load
            
            
            album_links = self.driver.find_elements(By.CSS_SELECTOR, "a.albumTitle")
            
            if not album_links:
                
                album_links = self.driver.find_elements(By.CSS_SELECTOR, ".albumListTitle a")
            
            if not album_links:
                
                album_links = self.driver.find_elements(By.CSS_SELECTOR, "div.albumBlock a")
            
            if not album_links:
                
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                album_links = [link for link in all_links if '/album/' in link.get_attribute('href') or '']
            
            
            best_match = None
            for link in album_links:
                link_text = link.text.lower()
                
                if album.lower() in link_text:
                    best_match = link
                    break
            
            
            if not best_match and album_links:
                best_match = album_links[0]
            
            if best_match:
                
                print(f"   Clicking on album: {best_match.text[:50]}...")
                self.driver.execute_script("arguments[0].scrollIntoView(true);", best_match)
                time.sleep(1)
                best_match.click()
                time.sleep(1)
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error searching/clicking album: {e}")
            return False
    
    def rate_album(self, album_data):
        """Rate a single album on AOTY"""
        try:
            print(f"\nProcessing: {album_data['full_artist']} - {album_data['album']}")
            print(f"RYM Rating: {album_data['rym_rating']} -> AOTY Rating: {album_data['rating']}")
            
            # Extract year from release date if available
            year = ""
            if album_data['release_date']:
                year_match = re.search(r'\d{4}', album_data['release_date'])
                if year_match:
                    year = year_match.group()
            
            # Search for the album and click on it
            if not self.search_and_click_album(
                album_data['full_artist'], 
                album_data['album'],
                year
            ):
                print(f"❌ Album not found or couldn't click: {album_data['full_artist']} - {album_data['album']}")
                return False
            
            
            wait = WebDriverWait(self.driver, 10)
            
            try:
                
                rating_input = None
                
                
                try:
                    rating_input = wait.until(
                        EC.presence_of_element_located((By.XPATH, "/html/body/span/div[4]/div[2]/div[1]/div[2]/div/div[4]/div[1]/div/input"))
                    )
                except:
                    pass
                
                
                if not rating_input:
                    try:
                        rating_input = self.driver.find_element(By.CSS_SELECTOR, "input.ratingInput")
                    except:
                        pass
                
                if not rating_input:
                    try:
                        rating_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'][placeholder*='Rate']")
                    except:
                        pass
                
                if not rating_input:
                    try:
                        
                        rating_input = self.driver.find_element(By.CSS_SELECTOR, "div.userRating input")
                    except:
                        pass
                
                if not rating_input:
                    print("❌ Could not find rating input field")
                    return False
                
                
                self.driver.execute_script("arguments[0].scrollIntoView(true);", rating_input)
                time.sleep(1)
                
                
                rating_input.clear()
                time.sleep(0.5)
                
                
                rating_input.send_keys(str(album_data['rating']))
                time.sleep(0.5)
                
                
                rating_button = None
                
                
                try:
                    rating_button = self.driver.find_element(By.XPATH, "/html/body/span/div[4]/div[2]/div[1]/div[2]/div/div[4]/div[1]/div/a/div")
                except:
                    pass
                
                
                if not rating_button:
                    try:
                        rating_button = self.driver.find_element(By.CSS_SELECTOR, "a.rateButton")
                    except:
                        pass
                
                if not rating_button:
                    try:
                        rating_button = self.driver.find_element(By.CSS_SELECTOR, "div.userRating a")
                    except:
                        pass
                
                if not rating_button:
                    try:
                        
                        parent = rating_input.find_element(By.XPATH, "./..")
                        rating_button = parent.find_element(By.TAG_NAME, "a")
                    except:
                        pass
                
                if rating_button:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", rating_button)
                    time.sleep(0.5)
                    rating_button.click()
                    print(f"✅ Successfully rated: {album_data['rating']}/100")
                else:
                    
                    rating_input.send_keys(Keys.RETURN)
                    print(f"✅ Successfully rated (via Enter): {album_data['rating']}/100")
                
                time.sleep(1)
                return True
                
            except Exception as e:
                print(f"❌ Could not rate album - might already be rated or page structure changed: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing album: {e}")
            return False
    
    def transfer_all_ratings(self):
        
        if not self.load_csv_data():
            return
        
        if not self.ratings_data:
            print("No ratings found in CSV file")
            return
        
        
        print("Setting up Chrome driver...")
        self.setup_driver()
        
        try:
            
            self.wait_for_login()
            
            
            successful = 0
            failed = 0
            
            for i, album_data in enumerate(self.ratings_data, 1):
                print(f"\n[{i}/{len(self.ratings_data)}]", end=" ")
                
                if self.rate_album(album_data):
                    successful += 1
                else:
                    failed += 1
                
                
                if i < len(self.ratings_data):
                    time.sleep(1)
            
            
            print("\n" + "="*50)
            print(f"Transfer Complete!")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📊 Total processed: {len(self.ratings_data)}")
            print("="*50)
            
        except KeyboardInterrupt:
            print("\n\nTransfer interrupted by user")
            
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            
        finally:
            print("\nPress ENTER to close the browser...")
            input()
            if self.driver:
                self.driver.quit()

def main():
    
    csv_file = input("Enter the path to your RYM CSV file: ").strip()
    
    
    if csv_file.startswith('"') and csv_file.endswith('"'):
        csv_file = csv_file[1:-1]
    
    
    transfer = RYMtoAOTYTransfer(csv_file)
    transfer.transfer_all_ratings()

if __name__ == "__main__":
    main()
