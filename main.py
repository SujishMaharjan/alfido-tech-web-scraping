import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

headers = {
    'User-Agent':"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}


# Function to get HTML content from a webpage
def get_html(url):
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve content from {url}")
        return None

# Function to extract data based on user input for tag and class name
def extract_data(soup, data_type, tag, class_name):
    if data_type in ['headlines', 'products', 'jobs']:
        # Use the provided tag and class to find the elements
        return [element.get_text().strip() for element in soup.find_all(tag, class_=class_name)]
    else:
        print("Unsupported data type")
        return []

# Function to scrape data from multiple pages (pagination support)
def scrape_data(url, data_type, tag, class_name, max_pages=1):
    all_data = []
    for page in range(1, max_pages + 1):
        paginated_url = f"{url}?page={page}"
        html_content = get_html(paginated_url)
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            data = extract_data(soup, data_type, tag, class_name)
            if data:
                all_data.extend(data)
        else:
            break
    return all_data

# Function to save data to CSV
def save_to_csv(data, filename):
    df = pd.DataFrame(data, columns=['Data'])
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

# Function to save data to SQLite database
def save_to_db(data, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS ScrapedData (id INTEGER PRIMARY KEY, data TEXT)')
    for item in data:
        cursor.execute('INSERT INTO ScrapedData (data) VALUES (?)', (item,))
    conn.commit()
    conn.close()
    print(f"Data saved to {db_name} database")

# Main function
def main():
    url = input("Enter the URL to scrape: ")
    data_type = input("Enter the type of data to scrape (headlines/products/jobs): ").lower()
    
    # User provides tag and class name
    tag = input("Enter the HTML tag for the data (e.g., h1, div, h2): ")
    class_name = input("Enter the class name for the data (leave blank if no class is needed): ")
    
    max_pages = int(input("Enter the number of pages to scrape: "))
    
    data = scrape_data(url, data_type, tag, class_name, max_pages)
    
    if data:
        save_option = input("Save data to (1) CSV or (2) Database? Enter 1 or 2: ")
        if save_option == '1':
            filename = input("Enter the CSV filename: ")
            save_to_csv(data, filename)
        elif save_option == '2':
            db_name = input("Enter the database name (with .db extension): ")
            save_to_db(data, db_name)
        else:
            print("Invalid option. Exiting.")
    else:
        print("No data scraped.")

if __name__ == "__main__":
    main()
