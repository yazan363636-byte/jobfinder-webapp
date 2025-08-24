import requests

# Словарь соответствия городов и area_id
CITY_TO_AREA = {
    "Москва": 1,
    "Санкт-Петербург": 2,
    "Новосибирск": 3,
    "Екатеринбург": 4,
    "Казань": 8,
    "Нижний Новгород": 66,
    "Челябинск": 10,
    "Самара": 78,
    "Омск": 5,
    "Ростов-на-Дону": 76,
    "Уфа": 9,
    "Красноярск": 19,
    "Воронеж": 113,
    "Пермь": 21,
    "Волгоград": 7,
}

# Допустимые значения опыта для API
EXPERIENCE_MAP = {
    "noExperience": "noExperience",
    "between1And3": "between1And3",
    "between3And6": "between3And6",
    "moreThan6": "moreThan6"
}

def search_vacancies(text, city=None, salary=None, experience=None):
    """
    Поиск вакансий на HH.ru по ключевым словам, городу, зарплате и опыту.
    :param text: текст запроса (например, "Python разработчик")
    :param city: город (например, "Москва")
    :param salary: минимальная зарплата (целое число)
    :param experience: опыт (ключ из EXPERIENCE_MAP)
    :return: список вакансий
    """
    url = "https://api.hh.ru/vacancies"

    # Подготовка параметров
    params = {
        'text': text.strip() if text else "",
        'area': CITY_TO_AREA.get(city),
        'salary': int(salary) if salary and str(salary).isdigit() else None,
        'experience': EXPERIENCE_MAP.get(experience),
        'per_page': 5,
        'order_by': 'relevance'
    }

    # Убираем None
    params = {k: v for k, v in params.items() if v is not None}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Ошибка при запросе к HH.ru: {e}")
        return []

    data = response.json()

    vacancies = []
    for item in data.get('items', []):
        # Обработка зарплаты
        salary_info = item.get('salary')
        if salary_info:
            from_val = salary_info.get('from')
            to_val = salary_info.get('to')
            currency = salary_info.get('currency', 'RUR')

            parts = []
            if from_val:
                parts.append(f"{from_val:,}".replace(',', ' '))
            if to_val and to_val != from_val:
                parts.append(f"{to_val:,}".replace(',', ' '))
            salary_str = " – ".join(parts) + f" {currency}"
        else:
            salary_str = "Не указана"

        # Получаем данные о вакансии
        title = item['name']
        company = item['employer']['name'] if item['employer'] else "Не указано"
        url = item['alternate_url']

        # Добавляем в список
        vacancies.append({
            'id': item['id'],
            'title': title,
            'company': company,
            'salary': salary_str,
            'url': url
        })

    return vacancies