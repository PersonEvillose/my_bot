import streamlit as st
import openai
import random
import re

# === НАСТРОЙКИ ===
openai.api_key = "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"


# Загрузка карт из файла
def load_cards():
    with open("cards.txt", "r", encoding="utf-8") as f:
        content = f.read()
    # Разделяем по маркеру карт
    cards_raw = re.split(r'--- НАЧАЛО КАРТЫ: ', content)
    cards = {}
    for card_raw in cards_raw[1:]:  # первый элемент пустой
        lines = card_raw.strip().split('\n')
        name = lines[0].strip()
        description = '\n'.join(lines[1:]).replace('--- КОНЕЦ КАРТЫ ---', '').strip()
        cards[name] = description
    return cards

cards_db = load_cards()

# Поиск похожей карты (простой)
def find_card(query):
    query_lower = query.lower()
    for name, desc in cards_db.items():
        if name.lower() in query_lower or any(kw in query_lower for kw in desc.lower().split()[:10]):
            return name, desc
    return None, None

# Функция ответа бота
def get_bot_response(user_input, card_name, card_desc):
    prompt = f"""Ты — оракул канала "Ключ к матрице реальности".
Пользователь спрашивает: {user_input}

Выпала карта: {card_name}
Описание карты: {card_desc}

Ответь развёрнуто, обращаясь на "ты", объясни значение карты применительно к вопросу пользователя. Закончи вдохновляющей фразой в стиле канала. Не придумывай карты, которых нет в колоде."""
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=500
    )
    return response.choices[0].message.content

# === ИНТЕРФЕЙС ===
st.set_page_config(page_title="Ключ к матрице реальности", page_icon="🔮")
st.title("🔮 Ключ к матрице реальности")
st.caption("Чат-оракул для работы с гипнокартами")

# Боковая панель с раскладами
with st.sidebar:
    st.header("Расклады")
    if st.button("🎲 Карта дня"):
        card_name = random.choice(list(cards_db.keys()))
        st.session_state["selected_card"] = card_name
        st.session_state["card_desc"] = cards_db[card_name]
        st.success(f"Выпала карта: **{card_name}**")
        st.write(st.session_state["card_desc"][:300] + "...")
    
    if st.button("🃏 Расклад из трёх карт"):
        cards = random.sample(list(cards_db.keys()), 3)
        st.session_state["spread"] = [(name, cards_db[name]) for name in cards]

# Основной чат
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Спросите о карте или сделайте расклад..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Матрица отвечает..."):
            # Проверяем, есть ли в запросе название карты
            card_name, card_desc = find_card(prompt)
            if card_name:
                response = get_bot_response(prompt, card_name, card_desc)
            elif "расклад" in prompt.lower():
                cards = random.sample(list(cards_db.keys()), 3)
                response = "**Ваш расклад:**\n\n"
                for name in cards:
                    response += f"**{name}**\n{cards_db[name][:200]}...\n\n"
                response += "Подробное толкование — напишите название любой из выпавших карт."
            else:
                response = "Какая карта вас интересует? Напишите её название, или нажмите «Карта дня»."
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})