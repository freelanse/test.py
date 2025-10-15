import re
from flask import Flask, request, jsonify

app = Flask(__name__)

BRANDS = [
    "Apple", "Dell", "HP", "Lenovo", "Nike", "Adidas", "Samsung", "Sony", "LG", "Huawei"
]

CATEGORIES = {
    "electronics": ["phone", "smartphone", "laptop", "tv", "headphones", "camera"],
    "home appliances": ["refrigerator", "washing machine", "microwave", "vacuum cleaner"],
    "clothing": ["t-shirt", "jeans", "dress", "jacket", "куртка", "футболка", "джинсы"],
    "footwear": ["sneakers", "shoes", "boots", "кроссовки", "ботинки"]
}

TIME_PATTERNS = {
    "morning": [r'\b(утро|morning|am|forenoon)\b'],
    "afternoon": [r'\b(день|day|afternoon|pm)\b'],
    "evening": [r'\b(вечер|evening|night)\b'],
    "night": [r'\b(ночь|late night)\b']
}

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r'[^\w\s:]', '', text)
    return text

def extract_zip_code(text: str) -> str | None:
    match = re.search(r'\b\d{5,6}\b', text)
    return match.group(0) if match else None

def extract_brand(text: str) -> str | None:
    for brand in BRANDS:
        if re.search(r'\b' + re.escape(brand.lower()) + r'\b', text.lower()):
            return brand
    return None

def extract_category(text: str) -> str | None:
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', text_lower):
                return category
    return None

def extract_time_preference(text: str) -> str | None:
    text_lower = text.lower()
    for label, patterns in TIME_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return label
    time_match = re.search(
        r'\b(?:at|around|by|в|к)\s*(\d{1,2}(?::\d{2})?\s*(?:am|pm|утра|дня|вечера|ночи)?)\b',
        text_lower
    )
    if time_match:
        return time_match.group(1).strip()
    return None

@app.route('/classify', methods=['POST'])
def classify_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    text_to_classify = data['text']
    cleaned_text = normalize_text(text_to_classify)
    result = {
        "zip": extract_zip_code(cleaned_text),
        "brand": extract_brand(cleaned_text),
        "category": extract_category(cleaned_text),
        "time_pref": extract_time_preference(cleaned_text)
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
