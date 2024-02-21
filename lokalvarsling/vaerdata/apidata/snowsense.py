import requests
from bs4 import BeautifulSoup

def hent_snowsense(stasjon='Stavbrekka'):
    '''Funksjon som henter data fra snowsense.is og returnerer en liste med data for en gitt stasjon.
    Funksjonen skraper data fra snowsense nettsida.

    Args:
        stasjon (str): Navnet på stasjonen du vil hente data for.
    
    Returns:
        list: Liste med data for en gitt stasjon.
    '''
    # URL med data for leiting etter stasjoner
    url = 'https://snowsense.is/no'


    response = requests.get(url)

    # Sjekk om vi fikk en gyldig respons
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all table row elements
        rows = soup.find_all('tr')

        # Placeholder for the data
        stasjon_data = None

        # Loop through each row to find the 'Stavbrekka' entry
        for row in rows:
            if stasjon in row.text:
                # Extract the cells from the row
                cells = row.find_all('td')
                stasjon_data = [cell.get_text(strip=True) for cell in cells]
                break

        # Check if we found the data
        if stasjon_data:
            return stasjon_data
        else:
            return "Stavbrekka data not found."
        
        