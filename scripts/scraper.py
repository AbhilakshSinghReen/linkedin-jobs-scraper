from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import pandas as pd
from datetime import datetime, date

start_date_str = "2023-01-29"
prev_scraped_file_path = "Worldwide Remote Internship - 2023-01-31.csv"
save_file_path = f'Software Engineer Internship Worldwide Remote - {date.today()}.csv'

start_date = datetime.strptime(start_date_str, "%Y-%m-%d")

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
    avoided_due_to_date_count = 0
    parsed_new_count = 0
    parsed_old_count = 0
    
    # Read old CSV
    df = pd.read_csv(prev_scraped_file_path)
    extracted_jobs = df.to_dict("records")
    parsed_old_count = len(extracted_jobs)

    soup = get_soup_from_file("target.html")

    job_cards = soup.find_all('div', class_='base-card')
    print(f"Number of jobs scraped: {len(job_cards)}")

    

    # extracted_jobs = []
    for job_card in job_cards:
        # company name, job title, location, date posted, job link
        job_details = {
            'companyName': '',
            'role': '',
            'location': '',
            'datePosted':'',
            'link':'',
            'checked': 0,
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


        # If date < start date, don't add
        job_date = datetime.strptime(job_details['datePosted'], "%Y-%m-%d")

        if job_date < start_date:
            avoided_due_to_date_count += 1
            continue


        extracted_jobs.append(job_details)
        parsed_new_count += 1

    print(f"Number of old jobs loaded: {parsed_old_count}")
    print(f"Number of new jobs parsed successfully: {parsed_new_count}")
    print(f"Number of jobs avoided due to date: {avoided_due_to_date_count}")

    # De duplicate extracted jobs, unique key is link
    # On duplicate, set checked to 1 if either one had checked set to 1
    extracted_jobs = sorted(extracted_jobs, key=lambda d: d['link']) 

    deduped_extracted_jobs = []

    i = 0
    while i < (len(extracted_jobs) - 1):
        if (extracted_jobs[i]['link'] != extracted_jobs[i + 1]['link']):
            # No problem, just add
            deduped_extracted_jobs.append(extracted_jobs[i])
            i += 1
        else:
            checked = 0

            j = i
            while (j < len(extracted_jobs) and extracted_jobs[j]['link'] == extracted_jobs[i]['link']):
                checked += extracted_jobs[j]['checked']
                j += 1
            
            # Add only 1
            if checked > 0:
                checked = 1

            deduped_extracted_jobs.append(extracted_jobs[i])
            deduped_extracted_jobs[-1]['checked'] = checked
            
            i = j
    
    if len(extracted_jobs) > 0:
        if len(deduped_extracted_jobs) == 0:
            deduped_extracted_jobs.append(extracted_jobs[-1])
        elif deduped_extracted_jobs[-1]['link'] != extracted_jobs[-1]['link']:
            deduped_extracted_jobs.append(extracted_jobs[-1])

        pass


    
    deduped_extracted_jobs = sorted(deduped_extracted_jobs, key=lambda x: datetime.strptime(x['datePosted'], '%Y-%m-%d'))

    # Save into CSV
    df = pd.DataFrame(deduped_extracted_jobs)
    df.to_csv(save_file_path, index=False)
    