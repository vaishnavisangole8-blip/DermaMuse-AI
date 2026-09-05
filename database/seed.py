"""
Product Database Seed Script
Run once after creating the schema:
    python database/seed.py
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mysql.connector
from config import Config

def get_conn():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST, user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD, database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT, charset='utf8mb4'
    )

PRODUCTS = [
    # ── Cleansers ──────────────────────────────────────────
    ('Cetaphil Gentle Skin Cleanser','Cetaphil','Cleanser',399,
     'Mild soap-free cleanser for all skin types.',
     'Cetyl Alcohol,Propylene Glycol,Glycerin',
     'Normal,Dry,Sensitive','Dryness,Sensitivity',4.5),

    ('Minimalist Salicylic Acid 2% Face Wash','Minimalist','Cleanser',249,
     'BHA cleanser that unclogs pores and controls acne.',
     'Salicylic Acid,Niacinamide',
     'Oily,Combination','Acne,Oiliness',4.4),

    ('Himalaya Purifying Neem Face Wash','Himalaya','Cleanser',175,
     'Herbal cleanser with neem and turmeric for acne-prone skin.',
     'Neem Extract,Turmeric',
     'Oily,Combination','Acne,Oiliness',4.2),

    ('Plum E-Luminence Simply Clearing Face Wash','Plum','Cleanser',295,
     'Gentle daily face wash with Vitamin E.',
     'Vitamin E,Glycerin',
     'Normal,Combination','Dryness,Oiliness',4.3),

    ('The Derma Co 1% Salicylic Acid Face Wash','The Derma Co','Cleanser',299,
     'Oil-control face wash with BHA for blackheads.',
     'Salicylic Acid,Aloe Vera',
     'Oily,Combination','Acne,Oiliness',4.3),

    # ── Moisturizers ───────────────────────────────────────
    ('Neutrogena Hydro Boost Water Gel','Neutrogena','Moisturizer',699,
     'Lightweight gel with hyaluronic acid. Non-greasy.',
     'Hyaluronic Acid,Glycerin',
     'Oily,Combination,Normal','Dryness,Oiliness',4.6),

    ('Minimalist 10% Niacinamide Face Moisturizer','Minimalist','Moisturizer',399,
     'Lightweight moisturizer for oil control and pore minimizing.',
     'Niacinamide,Hyaluronic Acid',
     'Oily,Combination','Oiliness,Redness,Pigmentation',4.5),

    ('Cetaphil Moisturizing Cream','Cetaphil','Moisturizer',549,
     'Rich cream for dry and sensitive skin. Fragrance-free.',
     'Glycerin,Petrolatum,Dimethicone',
     'Dry,Sensitive','Dryness,Sensitivity',4.7),

    ('Dot & Key Watermelon Cooling Moisturizer','Dot & Key','Moisturizer',495,
     'Hydrating gel-cream with watermelon extract.',
     'Watermelon Extract,Glycerin',
     'Normal,Oily,Combination','Dryness,Oiliness',4.3),

    ('Plum Hello Aloe Caring Day Moisturizer','Plum','Moisturizer',375,
     'Aloe-based daily moisturizer. Oil-free and non-comedogenic.',
     'Aloe Vera,Green Tea',
     'Normal,Oily','Dryness,Oiliness',4.2),

    ('Mamaearth Ubtan Face Moisturizer','Mamaearth','Moisturizer',299,
     'Turmeric and saffron moisturizer for glowing skin.',
     'Turmeric,Saffron,Kojic Acid',
     'Normal,Dry,Combination','Pigmentation,Dryness',4.1),

    ('CeraVe Moisturizing Cream','CeraVe','Moisturizer',899,
     'Ceramide-rich cream that restores skin barrier.',
     'Ceramides,Hyaluronic Acid,Niacinamide',
     'Dry,Sensitive,Normal','Dryness,Sensitivity',4.8),

    # ── Sunscreens ─────────────────────────────────────────
    ('Minimalist SPF 50 PA++++ Sunscreen','Minimalist','Sunscreen',349,
     'Broad spectrum SPF 50. No white cast. Matte finish.',
     'Zinc Oxide,Titanium Dioxide,Niacinamide',
     'Oily,Combination,Normal','Oiliness,Pigmentation',4.5),

    ('Lotus Herbals Safe Sun SPF 50','Lotus Herbals','Sunscreen',299,
     'Lightweight broad spectrum UVA/UVB protection.',
     'Avobenzone,Octinoxate,Aloe Vera',
     'Normal,Combination,Oily','Pigmentation',4.2),

    ("Re'equil Ultra Matte Dry Touch SPF 50","Re'equil",'Sunscreen',495,
     'Mattifying sunscreen PA++++ for oily skin.',
     'Uvinul A Plus,Tinosorb S',
     'Oily,Combination','Oiliness,Pigmentation',4.6),

    ('Neutrogena Ultra Sheer Dry-Touch SPF 50+','Neutrogena','Sunscreen',549,
     'Helioplex technology. Ultra-light non-greasy.',
     'Avobenzone,Homosalate,Helioplex',
     'Normal,Combination,Oily','Pigmentation',4.5),

    # ── Serums ─────────────────────────────────────────────
    ('Minimalist 10% Niacinamide Serum','Minimalist','Serum',599,
     'High-concentration niacinamide for pores and oil control.',
     'Niacinamide 10%,Zinc PCA',
     'Oily,Combination','Oiliness,Redness,Pigmentation,Acne',4.6),

    ('Minimalist 5% Vitamin C Serum','Minimalist','Serum',569,
     'Stable Vitamin C derivative for brightening.',
     'Ascorbyl Glucoside,Ferulic Acid',
     'Normal,Dry,Combination','Pigmentation,Redness',4.4),

    ('The Ordinary Hyaluronic Acid 2% + B5','The Ordinary','Serum',790,
     'Multi-depth hydration with HA and Vitamin B5.',
     'Hyaluronic Acid,Vitamin B5',
     'Dry,Normal,Sensitive','Dryness,Sensitivity',4.7),

    ('Dot & Key 20% Vitamin C + E Face Serum','Dot & Key','Serum',895,
     'Brightening serum with Vitamin C and E.',
     'Ascorbic Acid,Vitamin E,Ferulic Acid',
     'Normal,Dry,Combination','Pigmentation,Dryness',4.4),

    ('Plum 15% Vitamin C Face Serum','Plum','Serum',799,
     'Lightweight Vitamin C serum with ethyl ascorbic acid.',
     'Ethyl Ascorbic Acid,Niacinamide',
     'Normal,Oily,Combination','Pigmentation,Oiliness',4.3),

    ('Mamaearth Skin Correct Face Serum','Mamaearth','Serum',549,
     'Kojic acid and niacinamide for even skin tone.',
     'Kojic Acid,Niacinamide,Turmeric',
     'Normal,Dry,Combination','Pigmentation,Redness',4.1),

    # ── Toners ─────────────────────────────────────────────
    ('Minimalist 7% Glycolic Acid Toner','Minimalist','Toner',449,
     'AHA toner for exfoliation and brightness.',
     'Glycolic Acid,Aloe Vera',
     'Normal,Oily,Combination','Pigmentation,Acne,Oiliness',4.4),

    ('Plum Green Tea Alcohol-Free Toner','Plum','Toner',255,
     'Oil-control toner with green tea and glycolic acid.',
     'Green Tea,Glycolic Acid,Willow Bark',
     'Oily,Combination','Oiliness,Acne',4.3),

    # ── Treatments ─────────────────────────────────────────
    ('Minimalist 2% Salicylic Acid Serum','Minimalist','Treatment',499,
     'BHA serum targeting acne, whiteheads and blackheads.',
     'Salicylic Acid 2%,LHA,Glycolic Acid',
     'Oily,Combination','Acne,Oiliness',4.5),

    ('The Derma Co Acne Spot Corrector','The Derma Co','Treatment',349,
     'Fast-acting spot treatment with salicylic acid and tea tree.',
     'Salicylic Acid,Tea Tree Oil,Niacinamide',
     'Oily,Combination','Acne',4.3),

    # ── Face Masks ─────────────────────────────────────────
    ('Mamaearth Charcoal Face Mask','Mamaearth','Face Mask',299,
     'Deep cleansing clay mask with activated charcoal.',
     'Activated Charcoal,Kaolin Clay,Tea Tree',
     'Oily,Combination','Acne,Oiliness',4.1),

    ('Plum Grape Seed & Sea Buckthorn Face Mask','Plum','Face Mask',375,
     'Antioxidant mask for dull and tired skin.',
     'Grape Seed Extract,Sea Buckthorn,Vitamin E',
     'Normal,Dry,Combination','Dryness,Pigmentation',4.2),

    # ── Exfoliators ────────────────────────────────────────
    ('Minimalist AHA 25% + BHA 2% Peeling Solution','Minimalist','Exfoliator',649,
     'Chemical exfoliant for texture, pores and radiance.',
     'Glycolic Acid,Lactic Acid,Salicylic Acid',
     'Normal,Oily,Combination','Pigmentation,Acne,Oiliness',4.4),

    ('St. Ives Fresh Skin Apricot Scrub','St. Ives','Exfoliator',349,
     'Physical scrub with apricot seed powder.',
     'Walnut Shell Powder,Glycerin,Apricot Extract',
     'Normal,Oily,Combination','Oiliness,Pigmentation',4.0),
]

INGREDIENTS = [
    ('Niacinamide',
     'Oil control, minimizes pores, reduces uneven skin tone',
     'Oily, Combination, All skin types',
     'Start with low concentration if sensitive',
     88,
     'Vitamin B3 that regulates sebum, tightens pores, and strengthens the skin barrier.'),

    ('Hyaluronic Acid',
     'Deep hydration, plumping, moisture retention',
     'All skin types, especially Dry and Dehydrated',
     'Apply on damp skin and seal with moisturizer in dry climates',
     95,
     'Humectant that holds up to 1000x its weight in water. Essential for long-lasting hydration.'),

    ('Salicylic Acid',
     'Unclogs pores, treats acne, blackheads, whiteheads',
     'Oily, Acne-prone, Combination',
     'Avoid during pregnancy; may dry out sensitive skin',
     82,
     'Beta-hydroxy acid (BHA) that penetrates oil to dissolve dead skin cells inside pores.'),

    ('Vitamin C',
     'Brightening, antioxidant protection, even skin tone',
     'Normal, Dry, Combination',
     'Avoid mixing with retinol in the same routine; may tingle on sensitive skin',
     85,
     'Powerful antioxidant that neutralizes free radicals and brightens the appearance of dull skin.'),

    ('Ceramides',
     'Barrier repair, moisture retention, skin protection',
     'Dry, Sensitive, All skin types',
     'No known contraindications',
     92,
     'Lipids that form the skin barrier and help retain moisture. Key for repairing dry, damaged skin.'),

    ('Retinol',
     'Anti-aging, cell turnover, fine lines, uneven texture',
     'Normal, Combination (not sensitive)',
     'Avoid during pregnancy; start low (0.025%) and build up; always use SPF next day',
     78,
     'Vitamin A derivative that speeds cell turnover and boosts collagen. Use at night only.'),

    ('Glycolic Acid',
     'Exfoliation, brightening, texture improvement',
     'Normal, Oily, Combination',
     'Increases sun sensitivity; always use SPF',
     80,
     'AHA derived from sugarcane. Exfoliates the skin surface to improve texture and radiance.'),

    ('Aloe Vera',
     'Soothing, calming, light hydration, after-sun care',
     'Sensitive, All skin types',
     'Rare allergies possible; do a patch test',
     90,
     'Gentle plant extract with anti-inflammatory properties. Ideal for calming irritated skin.'),

    ('Centella Asiatica',
     'Soothing, barrier repair, calming redness',
     'Sensitive, Acne-prone, All skin types',
     'No known contraindications',
     91,
     'K-Beauty hero ingredient known for healing, calming, and reducing irritation.'),

    ('Benzoyl Peroxide',
     'Kills acne-causing bacteria, reduces inflammatory acne',
     'Oily, Acne-prone',
     'Can bleach fabric; avoid eyes; may dry out skin — follow with moisturizer',
     75,
     'Antibacterial ingredient effective against C. acnes. Start with 2.5% concentration.'),
]


def seed():
    print("Connecting to database...")
    conn = get_conn()
    cur  = conn.cursor()

    # ── Products ──────────────────────────────────────────
    print("Seeding products...")
    cur.execute("SELECT COUNT(*) FROM products")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  {count} products already exist. Skipping product seed.")
    else:
        sql = """INSERT INTO products
                 (name,brand,category,price,description,ingredients,
                  skin_types,concern_tags,rating)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cur.executemany(sql, PRODUCTS)
        conn.commit()
        print(f"  ✅ {len(PRODUCTS)} products inserted.")

    # ── Ingredients ───────────────────────────────────────
    print("Seeding ingredients...")
    cur.execute("SELECT COUNT(*) FROM ingredients_info")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"  {count} ingredients already exist. Skipping ingredient seed.")
    else:
        sql = """INSERT INTO ingredients_info
                 (name,common_use,suitable_for,avoid_for,compatibility,description)
                 VALUES (%s,%s,%s,%s,%s,%s)"""
        cur.executemany(sql, INGREDIENTS)
        conn.commit()
        print(f"  ✅ {len(INGREDIENTS)} ingredients inserted.")

    cur.close()
    conn.close()
    print("\n✅ Database seeded successfully!")
    print("You can now run the app: python app.py")


if __name__ == '__main__':
    seed()
