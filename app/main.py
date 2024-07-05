from flask import Flask, render_template, request
import requests
import time
import re
import psycopg2

app = Flask(__name__)

DATABASE = {
    'dbname': 'vacancies_db',
    'user': 'svyatoslavgrigorev',
    'password': '*****',
    'host': 'db',
    'port': '5432'
}

def clear_vacancies_table():
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM vacancies")
        cur.execute("ALTER SEQUENCE vacancies_id_seq RESTART WITH 1")
        conn.commit()
    except Exception as e:
        print(f"Ошибка при очистке: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def connect_db():
    conn = psycopg2.connect(**DATABASE)
    return conn

def insert_vacancy(vacancy):
    conn = connect_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO vacancies (hh_id, name, url, company, experience, description, salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            vacancy['id'],
            vacancy['name'],
            vacancy['url'],
            vacancy['company'],
            vacancy['experience'],
            vacancy['description'],
            vacancy['salary']
        ))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении вакансии: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def clean_highlight(text):
    return re.sub(r'<highlighttext>|</highlighttext>', '', text)

def Vacancies(keyword, company, experience):
    clear_vacancies_table()
    url = "https://api.hh.ru/vacancies"
    headers = {
        "User-Agent": "Your User Agent",
    }
    vacancies = []

    start_time = time.time()
    search_text = ""
    if keyword and company:
        search_text = f"{keyword} AND {company}"
    elif keyword:
        search_text = keyword
    elif company:
        search_text = company

    for page in range(200):
        params = {
            "text": search_text,
            "area": 1,  # (1 is Moscow)
            "page": page,
            "per_page": 100,
        }

        if experience:
            params["experience"] = experience

        response = requests.get(url, params=params, headers=headers)

        if response.status_code != 200:
            if response.status_code == 400:
                break
            continue

        data = response.json()
        items = data.get("items", [])
        for item in items:
            responsibility = clean_highlight(item.get("snippet", {}).get("responsibility") or "")
            requirement = clean_highlight(item.get("snippet", {}).get("requirement") or "")

            salary_data = item.get("salary") or {}
            from_salary = salary_data.get("from")
            to_salary = salary_data.get("to")
            curr_salary = salary_data.get("currency")
            if from_salary and to_salary and curr_salary:
                salary = f"от {from_salary or ''} до {to_salary or ''} {curr_salary or ''}"
            elif from_salary and curr_salary:
                salary = f"от {from_salary or ''} {curr_salary or ''}"
            elif to_salary and curr_salary:
                salary = f"до {to_salary} {curr_salary or ''}"
            else:
                salary = "Не указана"

            description = f"{responsibility} {requirement}"
            vacancy_data = {
                "id": item.get("id"),
                "name": item.get("name"),
                "url": item.get("alternate_url"),
                "company": item.get("employer", {}).get("name"),
                "experience": item.get("experience", {}).get("name"),
                "description": description,
                "salary": salary
            }

            insert_vacancy(vacancy_data)
            vacancies.append(vacancy_data)

        if page >= data.get('pages', 0) - 1:
            break

    end_time = time.time()
    elapsed_time = end_time - start_time

    return vacancies, elapsed_time


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form.get('keyword', '')
    company = request.form.get('company', '')
    experience = request.form.get('experience', '')

    vacancies, elapsed_time = Vacancies(keyword, company, experience)

    return render_template('results.html', vacancies=vacancies, elapsed_time=elapsed_time)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
