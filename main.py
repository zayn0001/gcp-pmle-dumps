import streamlit as st
import json
import os
import random

st.set_page_config(page_title="AI Flashcards", layout="wide")

st.title("🧠 AI Flashcards Quiz App")

# ------------------------------------------------
# Load questions from ./data folder
# ------------------------------------------------
DATA_DIR = "data"

def load_questions(data_dir=DATA_DIR):
    """Load all .json or .jsonl question files."""
    questions = []
    for file in os.listdir(data_dir):
        if file.endswith(".json") or file.endswith(".jsonl"):
            with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
                data = json.load(f)
                questions.extend(data)
    return questions


questions = load_questions()
if not questions:
    st.error("⚠️ No JSON files found in `data/` folder. Please add some question files.")
    st.stop()

# ------------------------------------------------
# Sidebar settings
# ------------------------------------------------
st.sidebar.header("⚙️ Settings")

# Optional random seed for reproducibility
seed_value = st.sidebar.text_input(
    "Random seed (leave blank for random order):",
    value="0",
    help="Enter a number or text — same seed gives same order each time."
)
if seed_value.strip():
    try:
        random.seed(int(seed_value))
    except ValueError:
        random.seed(seed_value.strip())
else:
    random.seed()  # randomize every run

# Collect all unique sections
sections = sorted(list({q.get("section_name", "Unknown Section") for q in questions}))
selected_sections = st.sidebar.multiselect(
    "📘 Filter by section:",
    options=sections,
    default=sections,  # show all by default
)

# Apply section filter
filtered_questions = [q for q in questions if q.get("section_name", "Unknown Section") in selected_sections]

if not filtered_questions:
    st.warning("No questions found for the selected section(s).")
    st.stop()

# Shuffle question + answer order
random.shuffle(filtered_questions)

# ------------------------------------------------
# Sidebar navigation
# ------------------------------------------------

if "current_index" not in st.session_state:
    st.session_state.current_index = 1

total = len(filtered_questions)

# ------------------------------------------------
# Display flashcard
# ------------------------------------------------
index = st.session_state.current_index
question = filtered_questions[index - 1]
prompt = question["prompt"]
answers = question["answers"]
random.shuffle(answers)

st.subheader(f"Question {index}/{total}")
st.markdown(f"**{prompt}**")
# ------------------------------------------------
# Direct jump to question
# ------------------------------------------------
with st.sidebar.expander("🔢 Jump to question"):
    jump_index = st.number_input(
        "Enter question number:",
        min_value=1,
        max_value=total,
        value=st.session_state.current_index,
        step=1
    )
    if st.button("Go to question"):
        st.session_state.current_index = jump_index
        st.rerun()


selected = st.radio(
    "Select your answer:",
    [a["text"] for a in answers],
    key=f"answer_{index}",
)

if st.button("Check Answer", key=f"check_{index}"):
    correct = next(a for a in answers if a["isCorrect"])
    if selected == correct["text"]:
        st.success("✅ Correct!")
        st.info(correct["explanation"])
    else:
        st.error("❌ Incorrect!")
        chosen_exp = next(a for a in answers if a["text"] == selected)["explanation"]
        st.warning(chosen_exp)
        st.info(f"**Correct answer:** {correct['text']}")
        st.caption(correct["explanation"])

# ------------------------------------------------
# Metadata + navigation
# ------------------------------------------------
with st.expander("📚 View metadata"):
    st.write(f"**Section:** {question.get('section_name', 'N/A')}")
    st.write(f"**Bloom Level:** {question.get('bloom_level', 'N/A')}")
    st.write(f"**Tags:** {', '.join(question.get('tags', []))}")

col1, col2 = st.columns(2)
if col1.button("⬅ Previous", disabled=st.session_state.current_index == 1):
    st.session_state.current_index -= 1
    st.rerun()

if col2.button("Next ➡", disabled=st.session_state.current_index == total):
    st.session_state.current_index += 1
    st.rerun()

