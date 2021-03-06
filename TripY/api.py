import urllib
import os, sys
import time
import requests
from .crawler import Crawler
from .entity import to_numbers, link_paths
from pymongo import MongoClient
from TripY.cluster_managment import default_config as CONFIG

client = MongoClient(CONFIG.MONGO)
DB = client.TripY

sys.path.insert(0, os.path.abspath(".."))
try:
    from lxml import html, etree
except:
    print("Please install `Python lXML` with this command before using `TripY`:")
    print()
    print("sudo apt-get install python3-lxml")
    quit()


def main_page(query):
    download_start = time.time()
    RESULT = {}
    url = 'https://www.tripadvisor.ru/TypeAheadJson?action=API' \
          '&types=geo,hotel,vr,eat,attr' \
          '&max=6' \
          '&scoreThreshold=0.5' \
          '&strictAnd=false' \
          '&typeahead1_5=true' \
          '&disableMaxGroupSize=true' \
          '&geoBoostFix=true' \
          '&neighborhood_geos=true' \
          '&details=true' \
          '&link_type=geo,hotel,vr,eat,attr' \
          '&uiOrigin=GEOSCOPE' \
          '&source=GEOSCOPE' \
          '&query=' + urllib.parse.quote(query)
    #  GET to TripAdvisor for required location:
    api_response = requests.get(url).json()
    url_from_autocomplete = "http://www.tripadvisor.com" + api_response['results'][0]['url']
    print("URL for required location: ", url_from_autocomplete)

    # Parsing main INFO from RESPONSE:

    RESULT['GEO_ID'] = api_response['results'][0]['value']
    RESULT['Location'] = api_response['results'][0]['details']['name']
    RESULT['Country'] = api_response['results'][0]['details']['parent_name']
    RESULT['Continent'] = api_response['results'][0]['details']['grandparent_name']
    RESULT['Coordinates'] = [float(t) for t in api_response['results'][0]['coords'].split(',')]

    # Start crawling MAIN-PAGE HTML page about required location:
    print("Downloading search results page")
    page_response = requests.post(url=url_from_autocomplete).text
    # urllib.request.urlretrieve(url_from_autocomplete, 'test.html') # Test downloading page for visual comparing.
    parser = html.fromstring(page_response)
    # Get INFO from main page:
    XPATH_TEXT = '//*[@id="taplc_expanding_read_more_box_0"]/div/div[1]/text()'
    _descr = parser.xpath(XPATH_TEXT)

    RESULT['Description'] = _descr[0][1:-1] if len(_descr) > 0 else ''

    # Specify all possible places for city
    possible_types = link_paths.keys()
    # possible_types = ['hotel', 'restaurant', 'attraction']  # for testing
    # possible_types = ['hotel', 'restaurant']  # for testing
    # _links = {'hotel': [
    #     "/Hotel_Review-g298507-d300401-Reviews-Renaissance_St_Petersburg_Baltic_Hotel-St_Petersburg_Northwestern_District.html"],
    #     'restaurant': [
    #         "/Restaurant_Review-g298507-d5247712-Reviews-Percorso-St_Petersburg_Northwestern_District.html"]}
    _links = {'hotel': [
        '/Hotel_Review-g298516-d7277751-Reviews-Hotel_Benefit-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2696301-Reviews-Hotel_Kruise-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2694937-Reviews-Profsoyuznaya-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2706222-Reviews-Marmelade-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1190029-Reviews-Hilton_Garden_Inn_Perm-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1793164-Reviews-Hotel_Vizit-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d6220354-Reviews-Austeria-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d579116-Reviews-Ural-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d305181-Reviews-Sport_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1200106-Reviews-Prikamie-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2704745-Reviews-Scorpion_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d6668344-Reviews-Hotel_Tentorium-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d7892827-Reviews-Mini_hotel_Venezia-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d305180-Reviews-Hotel_Mikos-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1176379-Reviews-Zhemchuzhina-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2680942-Reviews-Eva-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1135916-Reviews-Amaks_Premier-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d6208049-Reviews-Travel_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d4241855-Reviews-City_Star-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d2664202-Reviews-Hotel_Vicont-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d12959660-Reviews-Aura_City_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d608176-Reviews-New_Star-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d6585734-Reviews-Avant-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d579122-Reviews-Tourist_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d1191027-Reviews-Kama_Business_Hotel-Perm_Permsky_District_Perm_Krai_Volga_District.html',
        '/Hotel_Review-g298516-d501269-Reviews-Best_Eastern_Hotel_Almaz_Urala-Perm_Permsky_District_Perm_Krai_Volga_District.html'],
        'restaurant': [
            '/Restaurant_Review-g298516-d10329311-Reviews-Chaika_ZaZa-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d12072808-Reviews-REBRA_Shop-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6076975-Reviews-Khutorok-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6076857-Reviews-Sufra-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d12614129-Reviews-Rob_Roy-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6077064-Reviews-Khutorok-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6495789-Reviews-Expedicia_Severnaya_Kukhnya-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d12288833-Reviews-Lombardia_Cafe-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6988325-Reviews-Permskaya_Kukhnya-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d8867932-Reviews-Gala_Cafe-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d8348349-Reviews-Oblaka-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6495962-Reviews-Restaurant_Parmesan-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d8348290-Reviews-Nikala_Pirosmani-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6076360-Reviews-Coffeeshop_Company-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6743141-Reviews-Cheshire_Cat_Cheese-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6076649-Reviews-Kredo-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d12190943-Reviews-BarBurger-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d10727282-Reviews-Fresh_Market-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d2722005-Reviews-Oliva-Perm_Permsky_District_Perm_Krai_Volga_District.html',
            '/Restaurant_Review-g298516-d6077002-Reviews-Chaikhana-Perm_Permsky_District_Perm_Krai_Volga_District.html']}
    _crawlers = []
    for key in possible_types:
        # TODO test different xpathes and there performance
        XPATH_URL = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/@href')
        XPATH_NUMBERS = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/span[3]/text()')
        XPATH_REVIEW_NUMBERS = parser.xpath(
            '//*[@id="BODYCON"]/div[1]/div[1]/div/div[2]/div[2]/ul/li[contains(@class,"' + key + '")]/a/span[4]/text()')
        _url = XPATH_URL[0] if len(XPATH_URL) > 0 else ''
        _numbers = to_numbers(XPATH_NUMBERS[0]) if len(XPATH_NUMBERS) else 0
        _r_num = to_numbers(XPATH_REVIEW_NUMBERS[0]) if len(XPATH_REVIEW_NUMBERS) else 0
        crawler = Crawler(url=_url,
                          numbers=_numbers,
                          r_num=_r_num,
                          path=link_paths[key],
                          key=key,
                          geo_id=RESULT['GEO_ID'],
                          reviews=CONFIG._REVIEWS
                          )
        # DEV mode, looking just one link
        if not CONFIG._DEV:
            crawler.collect_links()
            while len(crawler.links)<crawler.numbers-10:
                print('Recollect links due to the lack of them...')
                crawler.collect_links()
        else:
            crawler.links = _links[key]
        print('%d links collected' % len(crawler.links))
        _crawlers.append(crawler)
        # crawler.collect_data()
        del crawler
    for craw in _crawlers:
        craw.collect_data()
        print(craw.key, 'DONE')
    DB['GEO'].insert_one(RESULT)
    # RESULT['Entities'][key + 's'] = [entity.dictify() for entity in crawler.data]
    download_end = time.time()
    print("Finished broadcasting links from MAIN page to workers: ", download_end - download_start, ' s')
    print("Please wait the end of crawling... May be a cup of coffee? :)")
    print('You can find your data in MongoDB ->', CONFIG.MONGO)
    return RESULT
