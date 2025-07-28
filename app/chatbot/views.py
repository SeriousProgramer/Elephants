# chatbot/views.py
import os
import time
import openai  
from .utils import classify_foods
from .models import Conversation
from django.http import JsonResponse, HttpResponse
from .models import Conversation
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import base64

openai.api_key = os.getenv("OPENAI_API_KEY")


def _correct_format(foods: str) -> bool:
    items = [item.strip() for item in foods.split(",")]
    if len(items) != 3:
        return False
    return True

@csrf_exempt
def simulate_hundred_convos(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    MAX_RETRIES = 3

    results = []
    for i in range(1, 101):
        retry = 0
        while True:
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                temperature=1.2,
                messages=[
                    {"role": "system",
                    "content": (
                        "Respond with **exactly** three distinct food items from South India, "
                        "comma‑separated, no extra text.")},
                    {"role": "user", "content": "What are your 3 favourite foods?"}
                ]
            )
            foods = completion.choices[0].message.content.strip()

            if _correct_format(foods):
                break                    
            retry += 1
            if retry >= MAX_RETRIES:
                return JsonResponse(
                    {"error": f"GPT gave bad format after {MAX_RETRIES} tries: {foods}"},
                    status=500
                )
            # otherwise loop again and ask the model once more
            time.sleep(0.2)              # tiny pause before re‑prompt

        # ----- classification & DB save -------
        _, label = classify_foods(foods)
        Conversation.objects.create(foods_raw=foods, diet_label=label)
        results.append({"id": i, "foods": foods, "diet": label})
        time.sleep(0.25)

    return JsonResponse({"conversations": results})




API_USER = os.getenv("API_USER", "user")
API_PASS = os.getenv("API_PASS", "password")

def basic_auth_required(view):
    def wrapped(request, *args, **kwargs):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if auth.startswith("Basic "):
            creds = base64.b64decode(auth.split()[1]).decode()
            u,p = creds.split(":",1)
            if u == API_USER and p == API_PASS:
                return view(request, *args, **kwargs)
        resp = HttpResponse("Unauthorized", status=401)
        resp["WWW-Authenticate"] = 'Basic realm="VegAPI"'
        return resp
    return wrapped

def get_top_foods(veg_rows):
    """Count all individual foods and return top 3 most popular"""
    food_counts = {}
    for row in veg_rows:
        foods = [food.strip() for food in row.foods_raw.split(",")]
        for food in foods:
            if food:  # skip empty strings
                food_counts[food] = food_counts.get(food, 0) + 1
    
    # Sort by count (descending) and get top 3
    sorted_foods = sorted(food_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"food": food, "count": count} for food, count in sorted_foods[:3]]

@csrf_exempt
@basic_auth_required
def veg_api(request):
    veg_rows = Conversation.objects.filter(diet_label__in=["vegan","vegetarian"])
    data = [
      {"foods": r.foods_raw, "diet": r.diet_label, "time": r.created_at.isoformat()}
      for r in veg_rows
    ]
    top_foods = get_top_foods(veg_rows)
    return JsonResponse({"results": data, "top_foods": top_foods})