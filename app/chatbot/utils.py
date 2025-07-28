# chatbot/utils.py  (create this file)
import openai, os
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_foods(foods: str) -> tuple[bool, str]:
    """
    Returns (is_veg_or_vegan, label) where label ∈ {"vegan","vegetarian","non-veg"}.
    """
    resp = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0,               # deterministic classification
        messages=[
            {"role": "system", "content":
             "You are a nutrition expert. "
             "Given exactly three food items, respond with one word: "
             "'vegan', 'vegetarian', or 'non-veg'."},
            {"role": "user",
             "content": f"Classify this list: {foods}"}
        ]
    )
    label = resp.choices[0].message.content.strip().lower()
    return label in ("vegan", "vegetarian"), label
