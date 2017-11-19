import worker.api as worker

if __name__ == '__main__':
    worker.main_page('Санкт')
    # worker.hotels_page(referer='https://www.tripadvisor.com/Tourism-g298507-St_Petersburg_Northwestern_District-Vacations.html')
    # hotel = worker.Hotel(
    #     url='/Hotel_Review-g298507-d543462-Reviews-Kempinski_Hotel_Moika_22-St_Petersburg_Northwestern_District.html')
    # # hotel = worker.Hotel(url='/Hotel_Review-g298507-d300108-Reviews-Astoria_Hotel-St_Petersburg_Northwestern_District.html')
    # # hotel = worker.Hotel(
    # #     url='/Hotel_Review-g298507-d2569226-Reviews-Domina_St_Petersburg-St_Petersburg_Northwestern_District.html')
    #
    # hotel.collect_main_info()