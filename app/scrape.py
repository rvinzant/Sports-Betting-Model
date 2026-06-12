import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.nba.com/schedule" 
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html')
    print(soup)

if __name__=="__main__":
    main()