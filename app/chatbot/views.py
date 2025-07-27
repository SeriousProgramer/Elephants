# chatbot/views.py
import os, json, openai
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

openai.api_key = os.getenv("OPENAI_API_KEY")

# --- 1) serve the initial question  -----------------
def chat_page(request):
    # let GPT phrase the question once
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly assistant."},
            {"role": "user",   "content": "Ask the user what their 3 favourite foods are in one short sentence."}
        ]
    )
    question = completion.choices[0].message.content.strip()
    return JsonResponse({"question": question})         # or render a template

# --- 2) accept the user's answer  --------------------
@csrf_exempt
def store_answer(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data   = json.loads(request.body or "{}")
    answer = data.get("answer", "")

    # TODO: persist answer for later vegetarian filter
    # Conversation.objects.create(text=answer)  # if you add a model

    # ask GPT to acknowledge
    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a friendly assistant."},
            {"role": "user",   "content": f"The user said their favourite foods are: {answer}. Reply politely in one sentence."}
        ]
    )
    bot_reply = completion.choices[0].message.content.strip()
    return JsonResponse({"reply": bot_reply})
