import json
import re
from uuid import uuid4

from bs4 import BeautifulSoup


def extract_quiz_data(html_content):
    """
    Extracts quiz data (questions and answers) from the provided HTML content.

    The function specifically targets the <script type="application/ld+json"> block
    which contains the quiz data in a structured JSON-LD format.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the JSON-LD script tag
    quiz_script = soup.find('script', {'type': 'application/ld+json'})

    if not quiz_script:
        return []

    try:
        # Load the JSON data from the script tag content
        quiz_data = json.loads(quiz_script.string)

        # The relevant questions are in the 'hasPart' key
        questions_raw = quiz_data.get('hasPart', [])
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from script tag: {e}")
        return []

    extracted_questions = []

    for i, raw_item in enumerate(questions_raw):
        # Extract question text and separate options if present
        full_question_text = raw_item.get('text', '')

        # Split text into question and options (assuming options start with A., B., C., D.)
        parts = re.split(r'\n([A-D]\. )', full_question_text, flags=re.MULTILINE)

        # The main question is the first part
        question_text = parts[0].strip()

        # Reconstruct options into a list of tuples (option_label, option_text)
        options = []
        if len(parts) > 1:
            # Reconstruct the question_text without the options
            question_text = question_text

            for j in range(1, len(parts), 2):
                option_label = parts[j].strip()  # e.g., 'A.'
                option_text = parts[j + 1].strip()  # e.g., 'Tokenize all of the fields...'
                options.append({'text': f"{option_text}", 'isCorrect': False, 'explanation': ""})

        # Extract the accepted answer text
        accepted_answer_text = raw_item.get('acceptedAnswer', {}).get('text', '').strip()

        # Determine the correct option based on the accepted answer text
        correct_option_label = accepted_answer_text.split('\n')[0].strip()

        # If the correct_option_label is a clear option label (e.g., 'A', 'B'), mark it as correct
        if correct_option_label and len(
                correct_option_label) <= 2:  # Check if it's a short label like 'A', 'B', 'C', 'D'
            for option in options:
                # Check if the option text starts with the correct label
                if option['text'].startswith(correct_option_label):
                    option['isCorrect'] = True
                    break

        # Fallback if options list is empty or match failed, just use the raw answer as a "correct" option
        if not options:
            options = [{'text': accepted_answer_text, 'isCorrect': True, 'explanation': ""}]

        # Construct the final question JSON
        question_json = {
            "text": question_text,
            "isCorrect": True,  # Placeholder, not applicable for question itself
            "explanation": "",  # Placeholder, not applicable for question itself
        }

        # Create the final JSON object in the requested format
        final_json = {
            "question_id": str(uuid4()),
            "prompt": question_json['text'],
            "answers": options,
            "tags": [],
            "question_choice_type": "multiple_choice" if options and len(options) > 1 else "",
            "section_name": "",
            "bloom_level": "",
            "idea_text": ""
        }

        # Add the explanation part to the correct answer text if available
        if '\n' in accepted_answer_text:
            raw_explanation = accepted_answer_text.split('\n', 1)[1].strip().replace('\n', ' ')
            # Clean up the explanation a bit, removing extra hyphens and spaces
            raw_explanation = re.sub(r'^- ', '', raw_explanation).strip()
            raw_explanation = re.sub(r'^- ', '', raw_explanation).strip()

            # Find and update the correct answer's explanation
            for answer in final_json['answers']:
                if answer['isCorrect']:
                    # Heuristically check if the raw explanation seems non-empty
                    if raw_explanation and raw_explanation != correct_option_label:
                        answer['explanation'] = raw_explanation
                    break

        extracted_questions.append(final_json)

    return extracted_questions


# The provided HTML content is loaded from the file 'quizlet1.html'
# You would replace the following lines in a real environment to read the file
# with your specific file reading method.
with open("quizlet3.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Extract the data
extracted_data = extract_quiz_data(html_content)

# Format the output as a single JSON object (list of questions)
output_json = json.dumps(extracted_data, indent=2)
with open("data/file5.json", "w", encoding="utf-8") as file:
    json.dump(extracted_data, file, indent=4)  # indent=4 makes it pretty-printed
print(output_json)