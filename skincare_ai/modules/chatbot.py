"""
Module 12 – AI Chatbot
Rule-based NLP chatbot that answers skincare questions.
Understands: routines, product queries, budget, ingredients, comparisons.
"""

import re
from database.db import query

# ── Intent patterns ───────────────────────────────────────────────────────────

INTENTS = [
    ('morning_routine',   r'morning|day.?routine|am routine'),
    ('night_routine',     r'night|evening|pm routine|night.?routine'),
    ('oily_skin',         r'oily skin|oiliness|sebum|shiny'),
    ('dry_skin',          r'dry skin|dryness|flaky|dehydrat'),
    ('acne',              r'acne|pimple|breakout|blemish|spot'),
    ('sensitive',         r'sensitive|redness|irritat|reaction'),
    ('budget_query',      r'budget|affordable|cheap|under ₹|within \d+|₹\d+'),
    ('product_best',      r'best product|recommend|suggest|which product'),
    ('ingredient_query',  r'ingredient|niacinamide|vitamin c|hyaluronic|salicylic|ceramide|retinol'),
    ('compare',           r'compare|vs|versus|difference between'),
    ('spf_sunscreen',     r'sunscreen|spf|sun protect'),
    ('moisturizer',       r'moisturis|moisturiz'),
    ('cleanser',          r'cleanser|face wash|wash'),
    ('serum',             r'serum|essence'),
    ('hello',             r'hello|hi |hey|namaste|hola'),
    ('thanks',            r'thank|thanks|shukriya'),
    ('help',              r'help|what can|kya kar|features'),
]


def detect_intent(text: str) -> str:
    text_lower = text.lower()
    for intent, pattern in INTENTS:
        if re.search(pattern, text_lower):
            return intent
    return 'unknown'


def extract_budget(text: str) -> int | None:
    m = re.search(r'₹?\s*(\d{3,5})', text)
    return int(m.group(1)) if m else None


# ── Response generators ───────────────────────────────────────────────────────

RESPONSES = {
    'hello': (
        "👋 Hello! I'm your AI Skincare Assistant.\n\n"
        "I can help you with:\n"
        "• 🌞 Morning & 🌙 Night routines\n"
        "• 🛒 Product recommendations\n"
        "• 💰 Budget-friendly suggestions\n"
        "• 🧪 Ingredient information\n"
        "• ⚖️ Product comparisons\n\n"
        "What would you like to know?"
    ),
    'thanks': "😊 You're welcome! Feel free to ask me anything about skincare.",
    'help': (
        "Here's what I can help you with:\n\n"
        "💬 Ask me:\n"
        "• 'What is a good morning routine for oily skin?'\n"
        "• 'Best products under ₹1000'\n"
        "• 'What does niacinamide do?'\n"
        "• 'Compare Product A vs Product B'\n"
        "• 'What should I use for acne?'"
    ),
    'morning_routine': (
        "🌞 **Recommended Morning Routine:**\n\n"
        "1️⃣ **Gentle Cleanser** — Removes overnight buildup\n"
        "2️⃣ **Lightweight Moisturizer** — Hydrates & preps skin\n"
        "3️⃣ **Broad-spectrum Sunscreen SPF 30+** — Essential daily protection\n\n"
        "💡 *Tip: Apply sunscreen as the last step, 15 min before sun exposure.*"
    ),
    'night_routine': (
        "🌙 **Recommended Night Routine:**\n\n"
        "1️⃣ **Cleanser** — Remove makeup, sunscreen & pollutants\n"
        "2️⃣ **Treatment Serum** — Target your skin concerns\n"
        "3️⃣ **Night Moisturizer** — Repair & nourish overnight\n\n"
        "💡 *Tip: Night is the best time for actives like retinol or AHAs.*"
    ),
    'oily_skin': (
        "🫧 **For Oily Skin:**\n\n"
        "✅ Use gel or foam-based cleansers\n"
        "✅ Choose oil-free, non-comedogenic moisturizers\n"
        "✅ Niacinamide serum helps control sebum production\n"
        "✅ Use mattifying sunscreen\n"
        "❌ Avoid heavy creams and oils\n\n"
        "📦 *Check the Product Recommendation section for oily skin products.*"
    ),
    'dry_skin': (
        "💧 **For Dry Skin:**\n\n"
        "✅ Use cream or oil-based cleansers\n"
        "✅ Apply Hyaluronic Acid serum on damp skin\n"
        "✅ Use rich moisturizers with ceramides\n"
        "✅ Avoid hot water & harsh scrubs\n"
        "❌ Skip alcohol-based toners\n\n"
        "📦 *Check the Product Recommendation section for dry skin products.*"
    ),
    'acne': (
        "🔴 **For Acne Concerns:**\n\n"
        "✅ Salicylic Acid (BHA) – unclogs pores\n"
        "✅ Niacinamide – reduces inflammation & redness\n"
        "✅ Benzoyl Peroxide – targets acne-causing bacteria\n"
        "✅ Keep hands away from face\n"
        "✅ Change pillowcases twice a week\n\n"
        "⚠️ *For persistent or severe acne, please consult a dermatologist.*"
    ),
    'sensitive': (
        "🌸 **For Sensitive Skin:**\n\n"
        "✅ Choose fragrance-free, hypoallergenic products\n"
        "✅ Patch test every new product\n"
        "✅ Use gentle, soap-free cleansers\n"
        "✅ Centella Asiatica & Aloe Vera help calm irritation\n"
        "❌ Avoid retinol, AHAs/BHAs when starting out\n\n"
        "⚠️ *If you experience persistent redness, consult a dermatologist.*"
    ),
    'spf_sunscreen': (
        "☀️ **About Sunscreen:**\n\n"
        "• SPF 30 blocks ~97% of UVB rays\n"
        "• SPF 50 blocks ~98% of UVB rays\n"
        "• Reapply every 2 hours when outdoors\n"
        "• Use broad-spectrum (UVA + UVB) protection\n"
        "• Apply as the LAST step of morning routine\n\n"
        "💡 *Sunscreen is the #1 anti-aging skincare product!*"
    ),
    'moisturizer': (
        "💦 **Choosing the Right Moisturizer:**\n\n"
        "• **Oily skin:** Gel or water-based, oil-free\n"
        "• **Dry skin:** Cream-based with ceramides / shea butter\n"
        "• **Combination:** Lightweight lotion\n"
        "• **Sensitive:** Fragrance-free with soothing ingredients\n\n"
        "🕐 *Apply moisturizer within 1-2 minutes of washing your face.*"
    ),
    'cleanser': (
        "🧴 **Choosing the Right Cleanser:**\n\n"
        "• **Oily/Acne skin:** Gel or foaming cleanser\n"
        "• **Dry skin:** Cream or milk cleanser\n"
        "• **Combination:** Gentle foam or gel\n"
        "• **Sensitive:** Soap-free, fragrance-free cleanser\n\n"
        "💡 *Cleanse twice daily — morning and night.*"
    ),
    'serum': (
        "💊 **About Serums:**\n\n"
        "Serums are concentrated treatments applied after cleansing:\n\n"
        "• **Vitamin C** → Brightening, antioxidant\n"
        "• **Hyaluronic Acid** → Hydration boost\n"
        "• **Niacinamide** → Oil control, pore minimizing\n"
        "• **Salicylic Acid** → Acne, pore clearing\n"
        "• **Retinol** → Anti-aging, cell turnover\n\n"
        "💡 *Apply serum after cleanser, before moisturizer.*"
    ),
    'ingredient_query': (
        "🧪 **Common Skincare Ingredients:**\n\n"
        "• **Niacinamide (B3)** → Oil control, brightening, pores\n"
        "• **Hyaluronic Acid** → Deep hydration\n"
        "• **Vitamin C** → Brightening, antioxidant\n"
        "• **Salicylic Acid** → Acne, exfoliation\n"
        "• **Ceramides** → Barrier repair\n"
        "• **Retinol** → Anti-aging\n\n"
        "🔍 *Visit the Ingredient Analyzer for detailed information!*"
    ),
    'compare': (
        "⚖️ **Product Comparison:**\n\n"
        "To compare products, visit the **Compare Products** section.\n"
        "Select two products to see a detailed comparison of:\n"
        "• Price\n"
        "• Skin Match Score\n"
        "• Concern Match Score\n"
        "• Rating\n"
        "• Final Compatibility Score\n\n"
        "The system will recommend the higher-scoring product."
    ),
    'unknown': (
        "🤔 I'm not sure I understood that. Here are some things I can help with:\n\n"
        "• Morning/Night skincare routines\n"
        "• Products for oily, dry, combination or sensitive skin\n"
        "• Ingredient information\n"
        "• Budget-friendly product recommendations\n"
        "• Product comparisons\n\n"
        "Try asking: *'What routine should I follow for oily skin?'*"
    ),
}


def get_budget_response(text: str) -> str:
    budget = extract_budget(text)
    if budget:
        products = query(
            'SELECT name, category, price, rating FROM products '
            'WHERE price <= %s ORDER BY rating DESC LIMIT 5',
            (budget,), fetchall=True
        )
        if products:
            lines = [f"💰 **Products within ₹{budget}:**\n"]
            for p in products:
                lines.append(f"• **{p['name']}** ({p['category']}) — ₹{p['price']} ⭐{p['rating']}")
            lines.append("\n🛒 *Visit Product Recommendations for full details & scores.*")
            return '\n'.join(lines)
        return f"No products found within ₹{budget} in our database. Try a higher budget."
    return RESPONSES['product_best']


def get_product_response() -> str:
    products = query(
        'SELECT name, category, price, rating FROM products ORDER BY rating DESC LIMIT 5',
        fetchall=True
    )
    if products:
        lines = ["🛒 **Top Rated Products:**\n"]
        for p in products:
            lines.append(f"• **{p['name']}** ({p['category']}) — ₹{p['price']} ⭐{p['rating']}")
        lines.append("\n🔍 *Visit Product Recommendations for personalized scores.*")
        return '\n'.join(lines)
    return "Visit the Product Recommendations section for personalized suggestions!"


# ── Main chatbot function ─────────────────────────────────────────────────────

def chatbot_respond(user_message: str, user_id: int = None) -> str:
    """Process user message and return bot response."""
    text = user_message.strip()
    if not text:
        return "Please type a message. I'm here to help! 😊"

    intent = detect_intent(text)

    # Special handling for budget/product intents requiring DB
    if intent == 'budget_query':
        return get_budget_response(text)
    if intent == 'product_best':
        return get_product_response()

    return RESPONSES.get(intent, RESPONSES['unknown'])
