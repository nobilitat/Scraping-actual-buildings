import requests
from bs4 import BeautifulSoup
import re
import pandas as pd 


def link_definition():
    """Сбор ссылок строящихся объектов из источника."""

    response = requests.get("https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/единый-реестр-застройщиков?subject=27")
    soup = BeautifulSoup(response.text, 'lxml')

    paginaiton = soup.find_all("a", class_="pagination-item")
    paginaiton = [i.text for i in paginaiton]
    last_page = max(paginaiton)

    with open("link/links.txt", "w+") as file_links:
            file_links.close()

    a = []
    for i in paginaiton:
        url = f'https://xn--80az8a.xn--d1aqf.xn--p1ai/сервисы/единый-реестр-застройщиков?subject=27&page={int(i)-1}&limit=10'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        links = soup.find_all('a')

        for line in str(links).split():
            a.append(re.findall('https:\/\/[^"]+\/\d{1,5}(?=")', line))

    b = [j for k in a for j in k if j]
    b = set(b)
    for i in b:
        with open("link/links.txt", "a", encoding="utf-8") as file_links:
            file_links.write(str(i)+'\n')


def table_formation():
    """Формирование таблицы из строящихся объектов и их параметров."""

    index_record = 0

    df = pd.DataFrame({
                'id_object': [],
                'addres_object': [],
                'developer_object': [],
                'group_company': [],
                'amount_floors': [],
                'amount_apartments': [],
                'area': [],
                'commissioning': [],
        })

    with open("link/links.txt", "r", encoding="utf-8") as file_links:
        for link in file_links:
            # Страница застройщика
            developer_page = requests.get(link)

            try:
                re.search('строящийся дом', developer_page.text)
            except:
                print("Объект проблемный")
                # Начать новую итерацию
                continue
            
            # Ссылка на строящйся объект
            link_building = re.findall('https:\/[^"]+(?=;)', developer_page.text)

            if link_building is None:
                continue

            link_building = change_link(link_building)
            print("ccылка")
            print(link_building)

            building_page = requests.get(link_building)

            if (re.search('Результатов не найдено',building_page.text) 
                or re.search('Единый реестр проблемных объектов',building_page.text)):
                print('Результатов не найдено... Переход к следующей ссылке\n')
                continue

            soup = BeautifulSoup(building_page.text, 'lxml')
            all_buildings = soup.find_all('div', class_='styles__Row-sc-13ibavg-0')

            
            for building in all_buildings:
                # Id Строящегося объекта
                id_object = building.find('span', 
                            class_='styles__Ellipsis-sc-1fw79ul-0 cDcbYl styles__Child-sc-cx1nz2-0 styles__Primary-sc-cx1nz2-1 bcibid')
                # Адрес Строящегося объекта
                addres_object = building.find('a', 
                                class_='styles__Address-sc-j3mki0-0 hLRgrJ')
                # Застройщик
                developer_object = building.find('span', 
                                   class_='styles__Ellipsis-sc-1fw79ul-0 cDcbYl styles__Child-sc-b0i2cq-0 styles__Primary-sc-b0i2cq-1 hvMGzU')
                # Группа компаний
                if building.find('span', class_='styles__Ellipsis-sc-1fw79ul-0 cDcbYl styles__Child-sc-b0i2cq-0 styles__Secondary-sc-b0i2cq-2 dViVBC') is not None:
                    group_company = building.find('span', 
                                    class_='styles__Ellipsis-sc-1fw79ul-0 cDcbYl styles__Child-sc-b0i2cq-0 styles__Secondary-sc-b0i2cq-2 dViVBC')
                # Количество этажей и квартир
                floors_and_apartments = building.find_all('div', 
                                        class_='styles__Cell-sc-7809tj-0 ibavEN Newbuindings Newbuildings_small')
                amount_floors = floors_and_apartments[0].text
                amount_apartments = floors_and_apartments[1].text
                # Площадь объекта и ввод в эксплуатацию
                area_and_commissioning = building.find_all('div', 
                                         class_='styles__Cell-sc-7809tj-0 ibavEN Newbuindings BuildersTable_normal')
                area = area_and_commissioning[1].text
                commissioning = area_and_commissioning[2].text
                
                df.loc[index_record] = [id_object.text, addres_object.text, developer_object.text, group_company.text, 
                                    amount_floors, amount_apartments, area, commissioning]
                index_record +=1
    return df


def change_link(link_building):
    """Дописывание гет параметров к ссылке"""

    link_building = link_building[1]
    link_building =  re.sub('&amp;', '', link_building)
    fromQuarter = '2021-10-01'
    link_building = link_building + f'&page=0&limit=10&place=0-24&fromQuarter={fromQuarter}&objStatus=0'
    return link_building
        

def saving_to_file(df):
    """Сохранение dataframe в файл"""
    
    df.to_csv('result/actual_building.csv')
    df.to_excel('result/actual_building.xlsx')