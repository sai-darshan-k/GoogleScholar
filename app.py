from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

class GoogleScholarScraper:
    def __init__(self):
        pass

    def get_data_from_profile_link(self, profile_link):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = requests.get(profile_link, headers=headers)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract name
                name_element = soup.find('div', {'id': 'gsc_prf_in'})
                name = name_element.text.strip() if name_element else "Name not found"

                # Extract citations, h-index, and i10-index
                citation_table = soup.find_all('td', {'class': 'gsc_rsb_std'})
                if len(citation_table) >= 3:
                    citations = int(citation_table[0].text.strip()) if citation_table[0].text else 0
                    h_index = citation_table[1].text.strip() if citation_table[1].text else "H-Index not found"
                    i10_index = citation_table[2].text.strip() if citation_table[2].text else "i10-Index not found"
                else:
                    citations, h_index, i10_index = 0, "H-Index not found", "i10-Index not found"

                # Fetch yearly citations
                yearly_citations = {}
                graph_element = soup.find('div', {'id': 'gsc_rsb_cit'})
                if graph_element:
                    bar_elements = graph_element.find_all('span', {'class': 'gsc_g_t'})
                    value_elements = graph_element.find_all('span', {'class': 'gsc_g_al'})

                    for year_element, count_element in zip(bar_elements, value_elements):
                        year = int(year_element.text.strip())
                        count = int(count_element.text.strip())
                        if 2020 <= year <= 2024:  # Adjust the year range as needed
                            yearly_citations[str(year)] = count

                # Fetch papers details (title, citations, year)
                papers = []
                paper_elements = soup.find_all('tr', {'class': 'gsc_a_tr'})
                for paper_element in paper_elements:
                    title_element = paper_element.find('a', {'class': 'gsc_a_at'})
                    title = title_element.text if title_element else "No Title"
                    link = f"https://scholar.google.com{title_element['href']}" if title_element else "#"

                    citation_element = paper_element.find('a', {'class': 'gsc_a_ac'})
                    paper_citations = citation_element.text.strip() if citation_element and citation_element.text else "0"

                    year_element = paper_element.find('span', {'class': 'gsc_a_h'})
                    year = year_element.text.strip() if year_element else "Unknown Year"

                    papers.append({
                        'title': title,
                        'link': link,
                        'citations': paper_citations,
                        'year': year
                    })

                return {
                    'Name': name,
                    'Citations': citations,  # Total citations
                    'H_Index': h_index,
                    'i10_Index': i10_index,
                    'Yearly_Citations': yearly_citations,
                    'Papers': papers
                }
            else:
                return {'error': f'Failed to retrieve data. Status code: {response.status_code}'}
        except Exception as e:
            return {'error': str(e)}

    def scraping_multiple_faculties(self, profile_links):
        data_list = []
        for profile_link in profile_links:
            faculty_data = self.get_data_from_profile_link(profile_link)
            if faculty_data:
                data_list.append(faculty_data)
        return data_list

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['GET'])
def scrape():
    profile_links = [
        "https://scholar.google.com/citations?user=fzs9d1IAAAAJ&hl=en",
        "https://scholar.google.com/citations?user=-ZYIiGAAAAAJ&hl=en",
        # Add additional profile links here
    ]
    
    scraper = GoogleScholarScraper()
    data = scraper.scraping_multiple_faculties(profile_links)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
