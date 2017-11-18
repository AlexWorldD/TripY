import worker.api as worker

if __name__ == '__main__':
    # worker.main_page('Пермь')
    # worker.hotels_page(referer='https://www.tripadvisor.com/Tourism-g298507-St_Petersburg_Northwestern_District-Vacations.html')
    hotel = worker.Hotel(url='/Hotel_Review-g298507-d300292-Reviews-Radisson_Royal_Hotel_St_Petersburg-St_Petersburg_Northwestern_District.html')
    hotel.download()