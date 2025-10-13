import json
import re
import uuid

from bs4 import BeautifulSoup

# Read the HTML file
with open('quizlet3.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all divs with aria-label="Term"
term_divs = soup.find_all('div', {'aria-label': 'Term'})
result = []
# For each div, find spans with class="TermText" and print their inner HTML
for div in term_divs:
    spans = div.find_all('span', {'class': 'TermText'})
    question_text = spans[0].decode_contents()
    if len(spans) < 2:
        print(f"⚠️ No answer span found for question: {question_text}")
        answer_text_raw = ""
    else:
        answer_text_raw = spans[1].decode_contents()

    answer_soup = BeautifulSoup(answer_text_raw, 'html.parser')
    answer_text_raw = answer_soup.get_text(strip=True)  # extract pure text like "B"
    # --- Parse the question and options ---
    # Example: "You are building... How should you configure? A. ... B. ... C. ... D. ..."
    # Split on capital letter + dot pattern
    parts = re.split(r"\b([A-D])\.\s*", question_text)

    prompt = parts[0].strip()
    options = []
    # Build options list from the split groups
    # parts = [question, "A", "optionA", "B", "optionB", ...]
    for i in range(1, len(parts) - 1, 2):
        label = parts[i]
        text = parts[i + 1].strip()
        souper = BeautifulSoup(text, 'html.parser')
        text = souper.get_text(strip=True)
        options.append({
            "text": f"{text}",
            "isCorrect": False,
            "explanation": "",
            "letter": label
        })

    # --- Identify correct option ---
    correct_label_match = re.match(r"([A-D])", answer_text_raw)
    correct_label = correct_label_match.group(1) if correct_label_match else None
    if not correct_label and len(answer_text_raw) > 0:
        correct_label = answer_text_raw[0].upper()
    if correct_label:
        for opt in options:
            if opt["letter"] == correct_label:
                opt["isCorrect"] = True
            del opt["letter"]
    else:
        print(f"⚠️ No correct answer label found in answer text: {answer_text_raw}")

    # --- Build question object ---
    q_obj = {
        "question_id": uuid.uuid4().hex[:24],
        "prompt": prompt,
        "answers": options,
        "tags": [],
        "question_choice_type": "multiple_choice",
        "section_name": "",
        "bloom_level": "",
        "idea_text": ""
    }

    result.append(q_obj)


# print(result)

# Save to JSON
with open("data/file5.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f"✅ Extracted {len(result)} MCQs into quizlet_mcq_structured.json")
