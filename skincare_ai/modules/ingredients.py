"""
Module 11 – Ingredient Analyzer
Returns ingredient info from DB or built-in knowledge base.
"""

from database.db import query

# Built-in fallback knowledge base
INGREDIENT_KB = {
    'niacinamide': {
        'name': 'Niacinamide',
        'common_use': 'Oil control, minimizes appearance of pores, reduces uneven skin tone, brightening',
        'suitable_for': 'Oily, Combination, All skin types',
        'avoid_for': 'Generally well-tolerated; start with low concentration if sensitive',
        'compatibility': 88,
        'description': (
            'Niacinamide (Vitamin B3) is a versatile ingredient. It helps regulate sebum production, '
            'visibly tighten pores, and improve the appearance of uneven skin tone. '
            'It also strengthens the skin barrier and reduces redness. '
            'Suitable for most skin types.'
        ),
    },
    'vitamin c': {
        'name': 'Vitamin C (Ascorbic Acid)',
        'common_use': 'Brightening, antioxidant protection, supports even skin tone',
        'suitable_for': 'Normal, Dry, Combination',
        'avoid_for': 'Very sensitive skin (may tingle); avoid combining with retinol in same routine',
        'compatibility': 85,
        'description': (
            'Vitamin C is a powerful antioxidant that neutralizes free radicals from UV and pollution. '
            'It helps brighten the appearance of dull skin and supports a more even tone. '
            'Use in the morning routine under sunscreen for best results.'
        ),
    },
    'hyaluronic acid': {
        'name': 'Hyaluronic Acid',
        'common_use': 'Deep hydration, plumping, moisture retention',
        'suitable_for': 'All skin types, especially Dry and Dehydrated',
        'avoid_for': 'Avoid in very dry environments without sealing with moisturizer',
        'compatibility': 95,
        'description': (
            'Hyaluronic Acid (HA) is a humectant that attracts and retains moisture. '
            'It can hold up to 1000x its weight in water, making it excellent for hydration. '
            'Apply on slightly damp skin and seal with moisturizer for maximum effect.'
        ),
    },
    'salicylic acid': {
        'name': 'Salicylic Acid (BHA)',
        'common_use': 'Unclogs pores, exfoliates, targets acne and blackheads',
        'suitable_for': 'Oily, Acne-prone, Combination',
        'avoid_for': 'Sensitive or dry skin (may be drying); avoid during pregnancy',
        'compatibility': 82,
        'description': (
            'Salicylic Acid is a beta-hydroxy acid (BHA) that penetrates pores to dissolve '
            'excess oil and dead skin cells. It is effective for treating blackheads, whiteheads, '
            'and mild acne. Start with lower concentrations (0.5–1%) and increase gradually.'
        ),
    },
    'ceramides': {
        'name': 'Ceramides',
        'common_use': 'Barrier repair, moisture retention, skin protection',
        'suitable_for': 'Dry, Sensitive, All skin types (especially compromised barrier)',
        'avoid_for': 'No known contraindications',
        'compatibility': 92,
        'description': (
            'Ceramides are lipids naturally found in the skin. They help maintain the skin barrier '
            'and retain moisture. Products with ceramides are excellent for repairing dry, '
            'compromised skin and strengthening the protective barrier.'
        ),
    },
    'retinol': {
        'name': 'Retinol (Vitamin A)',
        'common_use': 'Anti-aging, cell turnover, fine lines, uneven texture',
        'suitable_for': 'Normal, Combination (not sensitive)',
        'avoid_for': 'Sensitive skin, pregnant/nursing individuals; avoid daytime use',
        'compatibility': 78,
        'description': (
            'Retinol stimulates cell turnover and collagen production. It helps with the appearance '
            'of fine lines, uneven texture, and dullness. Start with low concentration (0.025%) '
            '2-3 times a week at night. Always follow with moisturizer and wear SPF during the day. '
            'Note: Consult a dermatologist before starting retinol.'
        ),
    },
    'glycolic acid': {
        'name': 'Glycolic Acid (AHA)',
        'common_use': 'Exfoliation, brightening, texture improvement',
        'suitable_for': 'Normal, Oily, Combination',
        'avoid_for': 'Sensitive skin; increases sun sensitivity — always use SPF',
        'compatibility': 80,
        'description': (
            'Glycolic Acid is an alpha-hydroxy acid (AHA) derived from sugarcane. '
            'It exfoliates the surface of the skin, improving texture, brightness, and the '
            'appearance of pores. Use at night; always apply sunscreen the next morning.'
        ),
    },
    'aloe vera': {
        'name': 'Aloe Vera',
        'common_use': 'Soothing, calming, hydration, after-sun care',
        'suitable_for': 'Sensitive, All skin types',
        'avoid_for': 'Rare allergies; do a patch test',
        'compatibility': 90,
        'description': (
            'Aloe Vera is a gentle, calming ingredient with anti-inflammatory properties. '
            'It soothes irritated skin, provides light hydration, and is commonly used '
            'for after-sun care and sensitive skin products.'
        ),
    },
    'centella asiatica': {
        'name': 'Centella Asiatica (Cica)',
        'common_use': 'Soothing, barrier repair, calming redness',
        'suitable_for': 'Sensitive, Acne-prone, All skin types',
        'avoid_for': 'No known contraindications',
        'compatibility': 91,
        'description': (
            'Centella Asiatica (Cica) is a plant extract known for its soothing and healing properties. '
            'It helps calm redness, support barrier repair, and reduce irritation. '
            'Very popular in K-Beauty formulations for sensitive and acne-prone skin.'
        ),
    },
    'benzoyl peroxide': {
        'name': 'Benzoyl Peroxide',
        'common_use': 'Reduces acne-causing bacteria, treats inflammatory acne',
        'suitable_for': 'Oily, Acne-prone',
        'avoid_for': 'Dry/sensitive skin; can bleach fabric; avoid eyes',
        'compatibility': 75,
        'description': (
            'Benzoyl Peroxide kills the bacteria (C. acnes) associated with acne. '
            'Start with 2.5% concentration to minimize dryness. Use a light application '
            'and always follow with moisturizer. Consult a dermatologist for persistent acne.'
        ),
    },
}


def get_ingredient_info(name: str) -> dict | None:
    """Look up ingredient: DB first, then built-in knowledge base."""
    # DB lookup
    row = query(
        'SELECT * FROM ingredients_info WHERE LOWER(name) LIKE %s',
        (f'%{name.lower()}%',), fetchone=True
    )
    if row:
        return row

    # Built-in KB lookup
    key = name.lower().strip()
    for kb_key, data in INGREDIENT_KB.items():
        if key in kb_key or kb_key in key:
            return data

    return None


def get_all_ingredients() -> list:
    """Return list of all ingredient names (DB + KB)."""
    db_rows = query('SELECT name FROM ingredients_info ORDER BY name', fetchall=True)
    db_names = [r['name'] for r in db_rows] if db_rows else []
    kb_names = [v['name'] for v in INGREDIENT_KB.values()]

    # Merge, deduplicate
    all_names = list({n.lower(): n for n in db_names + kb_names}.values())
    return sorted(all_names)
