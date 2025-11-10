import streamlit as st
import json
import os
import random
from collections import deque

st.set_page_config(page_title="AI Flashcards", layout="wide")

st.title("🧠 Ml Engineer Flash cards")

# ------------------------------------------------
# Load questions
# ------------------------------------------------
DATA_DIR = "data"

def load_questions(data_dir=DATA_DIR):
    """Load all .json or .jsonl question files."""
    questions = []
    for file in os.listdir(data_dir):
        if file.endswith(".json") or file.endswith(".jsonl"):
            if file in ["file3.json"]:
                continue
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
    default=sections,
)

filtered_questions = [q for q in questions if q.get("section_name", "Unknown Section") in selected_sections]
if not filtered_questions:
    st.warning("No questions found for the selected section(s).")
    st.stop()

# Shuffle
random.shuffle(filtered_questions)

# ------------------------------------------------
# Session state initialization
# ------------------------------------------------
if "current_index" not in st.session_state:
    st.session_state.current_index = 1

if "results" not in st.session_state:
    st.session_state.results = []  # store True/False for each answered question

if "recent_results" not in st.session_state:
    st.session_state.recent_results = deque(maxlen=10)  # rolling average over last 5

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
# Jump to question
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

# ------------------------------------------------
# Answer checking
# ------------------------------------------------
selected = st.radio(
    "Select your answer:",
    [a["text"] for a in answers],
    key=f"answer_{index}",
)

if st.button("Check Answer", key=f"check_{index}"):
    correct = next(a for a in answers if a["isCorrect"])
    is_correct = selected == correct["text"]

    # Store results
    st.session_state.results.append(is_correct)
    st.session_state.recent_results.append(is_correct)

    # Feedback
    if is_correct:
        st.success("✅ Correct!")
        st.info(correct["explanation"])
    else:
        st.error("❌ Incorrect!")
        chosen_exp = next(a for a in answers if a["text"] == selected)["explanation"]
        st.warning(chosen_exp)
        st.info(f"**Correct answer:** {correct['text']}")
        st.caption(correct["explanation"])

# ------------------------------------------------
# Stats display
# ------------------------------------------------
if st.session_state.results:
    total_attempts = len(st.session_state.results)
    total_correct = sum(st.session_state.results)
    overall_accuracy = total_correct / total_attempts * 100

    recent_correct = sum(st.session_state.recent_results)
    recent_accuracy = recent_correct / len(st.session_state.recent_results) * 100

    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Performance")
    st.sidebar.metric("Overall Accuracy", f"{overall_accuracy:.1f}%")
    st.sidebar.metric("Last 5 Accuracy", f"{recent_accuracy:.1f}%")

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


st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: grey;'>© 2025 Mishal Faisal | Built with ❤️ using Streamlit</p>",
    unsafe_allow_html=True
)
