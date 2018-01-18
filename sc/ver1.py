import json
import worker.api as worker

if __name__ == '__main__':
        
    query = input('Please enter a city: ')
    out = input('Please enter filename: ')
    plz_dont = ''
    while plz_dont != 'y' and plz_dont != 'yes' and plz_dont != 'n' and plz_dont != 'no':
        plz_dont = input('Do you actually need all these reviews? (y/n): ').lower()

    crawl_reviews = False if plz_dont == 'n' or plz_dont == 'no' else True
    
    out = open(out if len(out) > 0 else 'output.json', 'w')
    result = worker.main_page(query if len(query) > 0 else 'Санкт', crawl_reviews = crawl_reviews)
    json.dump(result, out, indent = 4)
    print('Done')
