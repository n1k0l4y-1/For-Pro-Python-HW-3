import requests
import fake_headers
import bs4
import json


headers = fake_headers.Headers(browser='chrome', os='win')
headers_dict = headers.generate()

link = 'https://spb.hh.ru/search/vacancy'
params = {'area': ['1', '2'],
          'text': 'Python',
          'items_on_page': '20',
          'search_field': 'description'}


def get_open_job():
    request = requests.get(link, params=params, headers=headers_dict)
    html = request.text
    soup = bs4.BeautifulSoup(html, "lxml")
    all_job = soup.find_all('div', class_='serp-item')

    job_list = {}

    for job in all_job:
        href = job.find(class_='serp-item__title').get('href')
        job_request = requests.get(href, headers=headers_dict)
        job_html = job_request.text
        job_soup = bs4.BeautifulSoup(job_html, "lxml")
        description = job_soup.find('div', class_='vacancy-description')
        description_text = description.text
        if description_text.count('Django') or description_text.count('Flask'):
            company_name = job_soup.find('span', class_='vacancy-company-name').text
            salary = job_soup.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary is None:
                salary = 'ЗП не указана'
            else:
                salary = salary.text.replace('\u202f', '')
            city = job_soup.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text.split(',')[0]

            job_list.setdefault(company_name)
            job_list[company_name] = {'salary': salary}
            job_list[company_name].update({'city': city})
            job_list[company_name].update({'link': href})
    return job_list


def write_json():
    with open('hh_ru.json', 'w', encoding='utf-8') as f:
        json.dump(get_open_job(), f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    write_json()