import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import time
import csv
import re


# Function to scrape book data from a single page
def scrape_books(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for request errors
        response.encoding = 'utf-8'  # Explicitly set encoding to UTF-8
        soup = BeautifulSoup(response.text, 'html.parser')

        books = []
        # Find all book articles on the page
        for book in soup.find_all('article', class_='product_pod'):
            try:
                # Extract title
                title = book.h3.a['title'].strip()

                # Extract price (remove currency symbol and convert to float)
                price_text = book.find('p', class_='price_color').text.strip()
                # Use regex to extract numeric value (e.g., '51.77' from 'Â£51.77' or '£51.77')
                price_match = re.search(r'\d+\.\d{2}', price_text)
                if price_match:
                    price = float(price_match.group())
                else:
                    print(f"Skipping book '{title}' due to invalid price format: {price_text}")
                    continue

                # Extract star rating (convert text to number)
                rating_class = book.find('p', class_='star-rating')['class']
                rating_text = rating_class[1]  # Get the rating (e.g., 'One', 'Two')
                rating = {
                    'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
                }.get(rating_text, 0)

                books.append({
                    'title': title,
                    'price': price,
                    'rating': rating
                })
            except Exception as e:
                print(f"Error processing book: {e}")
                continue

        return books
    except Exception as e:
        print(f"Error during scraping: {e}")
        return []


# Function to save data to CSV
def save_to_csv(books, filename='books.csv'):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'price', 'rating'])
            writer.writeheader()
            for book in books:
                writer.writerow(book)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


# Function to analyze and visualize data
def analyze_data(csv_file='books.csv'):
    try:
        # Read CSV into pandas DataFrame
        df = pd.read_csv(csv_file)

        # Basic analysis
        avg_price = df['price'].mean()
        rating_counts = df['rating'].value_counts().sort_index()

        print(f"\nAnalysis Results:")
        print(f"Average Book Price: £{avg_price:.2f}")
        print("\nRating Distribution:")
        for rating, count in rating_counts.items():
            print(f"{rating} Star(s): {count} books")

        # Create histogram of prices
        plt.figure(figsize=(10, 6))
        plt.hist(df['price'], bins=10, edgecolor='black', color='skyblue')
        plt.title('Distribution of Book Prices')
        plt.xlabel('Price (£)')
        plt.ylabel('Number of Books')
        plt.grid(True, alpha=0.3)
        plt.savefig('price_distribution.png')
        print("\nPrice distribution histogram saved as 'price_distribution.png'")

    except Exception as e:
        print(f"Error during analysis: {e}")


# Main execution
def main():
    url = 'http://books.toscrape.com/'
    print(f"Scraping books from {url}")

    # Scrape books
    books = scrape_books(url)
    if not books:
        print("No books scraped. Exiting.")
        return

    print(f"Scraped {len(books)} books")

    # Save to CSV
    save_to_csv(books)

    # Analyze data and create visualization
    analyze_data()


if __name__ == "__main__":
    # Add a small delay to be polite to the server
    time.sleep(1)
    main()