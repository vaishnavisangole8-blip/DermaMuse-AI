"""
Module 7, 8, 9 – Recommendation Engine
  • Personalized Day/Night Routine
  • Product Recommendation with compatibility score
  • Budget Calculation
  • Product Comparison

Compatibility Score Formula:
  Final Score = 0.40×SkinMatch + 0.30×ConcernMatch
              + 0.20×BudgetMatch + 0.10×(Rating/5×100)
"""

from database.db import query


# ── Routine templates ─────────────────────────────────────────────────────────

ROUTINES = {
    'Oily': {
        'day': [
            {'step': 1, 'product': 'Gentle Foaming Cleanser',      'purpose': 'Removes excess oil without stripping skin', 'price_range': '₹150–₹300'},
            {'step': 2, 'product': 'Oil-free Lightweight Moisturizer','purpose': 'Hydrates without clogging pores',          'price_range': '₹200–₹400'},
            {'step': 3, 'product': 'Broad-spectrum Sunscreen SPF 50','purpose': 'UV protection, matte finish',              'price_range': '₹300–₹500'},
        ],
        'night': [
            {'step': 1, 'product': 'Foaming/Gel Cleanser',          'purpose': 'Deep cleanse end-of-day buildup',           'price_range': '₹150–₹300'},
            {'step': 2, 'product': 'Niacinamide Serum',             'purpose': 'Controls sebum, minimises pores',           'price_range': '₹300–₹600'},
            {'step': 3, 'product': 'Oil-free Night Moisturizer',    'purpose': 'Repair without heaviness',                  'price_range': '₹200–₹400'},
        ],
    },
    'Dry': {
        'day': [
            {'step': 1, 'product': 'Cream/Hydrating Cleanser',      'purpose': 'Cleanses without drying skin',             'price_range': '₹200–₹400'},
            {'step': 2, 'product': 'Rich Moisturizer with HA',      'purpose': 'Deep hydration, plumps skin',              'price_range': '₹300–₹600'},
            {'step': 3, 'product': 'Hydrating Sunscreen SPF 30+',   'purpose': 'UV protection + moisture',                 'price_range': '₹300–₹500'},
        ],
        'night': [
            {'step': 1, 'product': 'Gentle Cream Cleanser',         'purpose': 'Softly removes impurities',                'price_range': '₹200–₹400'},
            {'step': 2, 'product': 'Hyaluronic Acid Serum',         'purpose': 'Deep overnight hydration',                 'price_range': '₹300–₹700'},
            {'step': 3, 'product': 'Rich Night Cream with Ceramides','purpose': 'Barrier repair while sleeping',           'price_range': '₹400–₹800'},
        ],
    },
    'Combination': {
        'day': [
            {'step': 1, 'product': 'Balancing Gel Cleanser',        'purpose': 'Balances oily & dry zones',                'price_range': '₹150–₹350'},
            {'step': 2, 'product': 'Lightweight Balancing Moisturizer','purpose': 'Hydrates dry areas, controls T-zone',   'price_range': '₹250–₹500'},
            {'step': 3, 'product': 'Broad-spectrum Sunscreen SPF 40','purpose': 'Protection without greasiness',           'price_range': '₹300–₹500'},
        ],
        'night': [
            {'step': 1, 'product': 'Gel/Foam Cleanser',             'purpose': 'Balanced deep cleanse',                   'price_range': '₹150–₹300'},
            {'step': 2, 'product': 'Niacinamide + HA Serum',        'purpose': 'Dual action: oil control + hydration',    'price_range': '₹350–₹650'},
            {'step': 3, 'product': 'Balancing Night Cream',         'purpose': 'Zone-specific overnight repair',          'price_range': '₹300–₹550'},
        ],
    },
    'Normal': {
        'day': [
            {'step': 1, 'product': 'Gentle Daily Cleanser',         'purpose': 'Maintains skin clarity',                  'price_range': '₹150–₹300'},
            {'step': 2, 'product': 'Daily Moisturizer',             'purpose': 'Maintains skin barrier',                  'price_range': '₹200–₹450'},
            {'step': 3, 'product': 'Sunscreen SPF 30+',             'purpose': 'Daily UV protection',                     'price_range': '₹250–₹450'},
        ],
        'night': [
            {'step': 1, 'product': 'Gentle Cleanser',               'purpose': 'Removes daily grime',                     'price_range': '₹150–₹300'},
            {'step': 2, 'product': 'Vitamin C Serum',               'purpose': 'Brightening & antioxidant protection',   'price_range': '₹300–₹700'},
            {'step': 3, 'product': 'Night Moisturizer',             'purpose': 'Skin repair & maintenance',               'price_range': '₹250–₹500'},
        ],
    },
}

ACNE_ADDONS = {
    'day_note':   'Consider a Salicylic Acid spot treatment. Consult a dermatologist for persistent acne.',
    'night_note': 'A BHA (Salicylic Acid) toner or Benzoyl Peroxide treatment may help. Patch-test first.',
}

SENSITIVITY_ADDONS = {
    'note': 'Avoid fragranced products. Look for "Hypoallergenic" and "Dermatologist-tested" labels.',
}


def get_routine(skin_type: str, scores: dict) -> dict:
    """Return day + night routine dict based on skin type and concern scores."""
    base_skin = skin_type if skin_type in ROUTINES else 'Normal'
    routine = {
        'day':   list(ROUTINES[base_skin]['day']),
        'night': list(ROUTINES[base_skin]['night']),
        'notes': [],
    }
    if scores.get('concern_score', 0) > 55:
        routine['notes'].append(ACNE_ADDONS['day_note'])
        routine['notes'].append(ACNE_ADDONS['night_note'])
    if scores.get('sensitivity_score', 0) > 60:
        routine['notes'].append(SENSITIVITY_ADDONS['note'])
    return routine


# ── Compatibility scoring ─────────────────────────────────────────────────────

def _skin_match(product: dict, skin_type: str) -> int:
    """0-100: does product's skin_types field include user's skin type?"""
    types = [t.strip().lower() for t in (product.get('skin_types') or '').split(',')]
    if skin_type.lower() in types or 'all' in types:
        return 100
    if 'combination' in types and skin_type.lower() in ('oily', 'dry', 'normal'):
        return 60
    return 30


def _concern_match(product: dict, scores: dict) -> int:
    """0-100: overlap between product concern_tags and user's high-scoring concerns."""
    tags = [t.strip().lower() for t in (product.get('concern_tags') or '').split(',')]
    user_concerns = []
    if scores.get('oiliness_score',    0) > 50: user_concerns.append('oiliness')
    if scores.get('dryness_score',     0) > 50: user_concerns.append('dryness')
    if scores.get('concern_score',     0) > 50: user_concerns.append('acne')
    if scores.get('sensitivity_score', 0) > 50: user_concerns.append('sensitivity')
    if scores.get('redness_score',     0) > 50: user_concerns.append('redness')
    if scores.get('pigmentation_score',0) > 50: user_concerns.append('pigmentation')

    if not user_concerns:
        return 70   # neutral skin → decent match
    overlap = sum(1 for c in user_concerns if c in tags)
    return min(100, int((overlap / len(user_concerns)) * 100) + 20)


def _budget_match(price: int, budget: int) -> int:
    """0-100: how comfortably does this product fit in the per-item budget?"""
    if budget <= 0:
        return 50
    ratio = price / budget
    if ratio <= 0.25:  return 100
    if ratio <= 0.40:  return 90
    if ratio <= 0.60:  return 75
    if ratio <= 0.80:  return 55
    if ratio <= 1.00:  return 35
    return 10


def compute_product_score(product: dict, skin_type: str,
                           scores: dict, budget: int) -> dict:
    """
    Final Product Score = 40%×SkinMatch + 30%×ConcernMatch
                        + 20%×BudgetMatch + 10%×(Rating×20)
    """
    per_item_budget = budget // 4 if budget else 500
    sm = _skin_match(product, skin_type)
    cm = _concern_match(product, scores)
    bm = _budget_match(product.get('price', 999), per_item_budget * 4)
    rm = int((float(product.get('rating', 4.0)) / 5.0) * 100)

    final = int(0.40 * sm + 0.30 * cm + 0.20 * bm + 0.10 * rm)
    return {
        'skin_match':    sm,
        'concern_match': cm,
        'budget_match':  bm,
        'rating_score':  rm,
        'final_score':   final,
    }


# ── Product recommendation ────────────────────────────────────────────────────

def recommend_products(skin_type: str, scores: dict,
                       budget: int, top_n: int = 5) -> list:
    """
    Filter → Score → Sort → Return top N products within budget.
    """
    products = query('SELECT * FROM products', fetchall=True)
    if not products:
        return []

    scored = []
    for p in products:
        if p['price'] > budget:
            continue
        sc = compute_product_score(p, skin_type, scores, budget)
        scored.append({**p, **sc})

    scored.sort(key=lambda x: x['final_score'], reverse=True)
    return scored[:top_n]


# ── Budget computation ────────────────────────────────────────────────────────

def compute_budget(recommended_products: list, budget: int) -> dict:
    """
    Returns budget breakdown: total used, remaining, items list.
    Greedily picks products that fit within budget.
    """
    selected  = []
    total_used = 0
    categories_covered = set()

    for p in recommended_products:
        cat = p.get('category', '')
        # Prefer one product per category
        if cat in categories_covered:
            continue
        if total_used + p['price'] <= budget:
            selected.append(p)
            total_used += p['price']
            categories_covered.add(cat)

    return {
        'budget':     budget,
        'used':       total_used,
        'remaining':  budget - total_used,
        'selected':   selected,
    }


# ── Product comparison ────────────────────────────────────────────────────────

def compare_products(product_ids: list, skin_type: str,
                     scores: dict, budget: int) -> list:
    """Return comparison data for two or more product IDs."""
    result = []
    for pid in product_ids:
        p = query('SELECT * FROM products WHERE product_id=%s',
                  (pid,), fetchone=True)
        if p:
            sc = compute_product_score(p, skin_type, scores, budget)
            result.append({**p, **sc})
    result.sort(key=lambda x: x['final_score'], reverse=True)
    return result
