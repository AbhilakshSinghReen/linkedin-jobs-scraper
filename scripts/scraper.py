from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import pandas as pd
from datetime import datetime


def get_soup_from_file(file_path):
    soup = ''
    with open(file_path, encoding="utf8") as html_file:
        soup = BeautifulSoup(html_file, 'lxml')

    return soup

def trim_url_to_remove_query_parameters(url):
    parsed_url = urlsplit(url)
    trimmed_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
    return trimmed_url


if __name__ == "__main__":
    soup = get_soup_from_file("Worldwide Remote Internship - 2023-01-17.html")

    job_cards = soup.find_all('div', class_='base-card')
    print(f"Number of jobs scraped: {len(job_cards)}")

    extracted_jobs = []
    for job_card in job_cards:
        # company name, job title, location, date posted, job link
        job_details = {
            'companyName': '',
            'role': '',
            'location': '',
            'datePosted':'',
            'link':''
        }

        card_subtitle_tag = job_card.find('h4', class_='base-search-card__subtitle')
        if card_subtitle_tag:
            job_details['companyName'] = card_subtitle_tag.get_text().strip()
        else:
            continue

        card_title_tag = job_card.find('h3', class_='base-search-card__title')
        if card_title_tag:
            job_details['role'] = card_title_tag.get_text().strip()
        else:
            continue

        job_location_span_tag = job_card.find('span', class_='job-search-card__location')
        if job_location_span_tag:
            job_details['location'] = job_location_span_tag.get_text().strip()
        else:
            continue
        
        job_posted_time_tag = job_card.find('time', class_='job-search-card__listdate')
        if job_posted_time_tag:
            job_posted_datetime = str(job_posted_time_tag.attrs.get('datetime')).strip()
            job_details['datePosted'] = job_posted_datetime
        else:
            job_posted_time_tag = job_card.find('time', class_='job-search-card__listdate--new')
            if job_posted_time_tag:
                job_posted_datetime = str(job_posted_time_tag.attrs.get('datetime')).strip()
                job_details['datePosted'] = job_posted_datetime
            else:
                continue

        job_link_tag = job_card.find('a', class_='base-card__full-link')
        if job_link_tag:
            job_link = str(job_link_tag.attrs.get('href')).strip()
            job_link = trim_url_to_remove_query_parameters(job_link)
            job_details['link'] = job_link
        else:
            continue

        extracted_jobs.append(job_details)

    print(f"Number of jobs parsed successfully: {len(extracted_jobs)}")
    
    extracted_jobs = sorted(extracted_jobs, key=lambda x: datetime.strptime(x['datePosted'], '%Y-%m-%d'))


    # Add the checked column
    for job in extracted_jobs:
        job['checked'] = 0

    # Save into CSV
    df = pd.DataFrame(extracted_jobs)
    df.to_csv('Worldwide Remote Internship - 2023-01-17.csv', index=False)
    