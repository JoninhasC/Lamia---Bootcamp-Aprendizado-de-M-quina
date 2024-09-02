from bs4 import BeautifulSoup
import requests
import time
import os


def find_jobs():
    print('Put some skill that you are not familiar with')
    unfamiliar_skill = input('>')
    print(f'Filtering out {unfamiliar_skill}')

    # Fetch and parse the HTML content
    html_text = requests.get(
        'https://www.timesjobs.com/candidate/job-search.html?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords=python&txtLocation=').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')

    # Ensure the directory exists
    if not os.path.exists('post'):
        os.makedirs('post')

    for index, job in enumerate(jobs):
        published_date = job.find('span', class_='sim-posted').span.text.strip()
        if '1 day' in published_date or 'few' in published_date:
            company_name = job.find('h3', class_='joblist-comp-name').text.strip()
            skills = job.find('span', class_='srp-skills').text.strip()
            more_info = job.header.h2.a['href']
            if unfamiliar_skill.lower() not in skills.lower():
                with open(f'post/{index}.txt', 'w') as file:
                    file.write(f"Company Name: {company_name}\n")
                    file.write(f"Required Skills: {skills}\n")
                    file.write(f"More Info: {more_info}\n")
                print(f'File saved: post/{index}.txt')


if __name__ == '__main__':
    while True:
        find_jobs()
        time_wait = 10
        print(f'Waiting {time_wait} minutes...')
        time.sleep(time_wait * 60)
