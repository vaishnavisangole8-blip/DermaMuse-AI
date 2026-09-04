"""
Product Routes – Modules 8, 9, 10, 11
Handles:
- Product listing
- Category filtering
- Product comparison
- Ingredient analyzer
- Product API
- Ingredient API
"""

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    jsonify,
    session
)

from modules.auth import login_required
from modules.recommendation import (
    recommend_products,
    compare_products
)
from modules.ingredients import (
    get_ingredient_info,
    get_all_ingredients
)
from database.db import query


product_bp = Blueprint(
    'products',
    __name__,
    url_prefix='/products'
)


# ============================================================
# PRODUCT LISTING
# ============================================================

@product_bp.route('/')
@login_required
def listing():

    # --------------------------------------------------------
    # Get latest skin analysis
    # --------------------------------------------------------

    analysis = query(
        '''
        SELECT *
        FROM skin_analyses
        WHERE user_id=%s
        ORDER BY analysis_date DESC
        LIMIT 1
        ''',
        (session['user_id'],),
        fetchone=True
    )

    skin_type = (
        analysis['skin_type']
        if analysis and analysis.get('skin_type')
        else 'Normal'
    )

    budget = (
        analysis['budget']
        if analysis and analysis.get('budget')
        else 1500
    )

    scores = analysis if analysis else {}

    # --------------------------------------------------------
    # Category filter from URL
    #
    # Example:
    # /products/?category=Cleanser
    # /products/?category=Sunscreen
    # /products/?category=Moisturizer
    # --------------------------------------------------------

    category = request.args.get('category', '').strip()

    allowed_categories = [
        'Cleanser',
        'Moisturizer',
        'Sunscreen',
        'Serum',
        'Toner',
        'Exfoliator',
        'Treatment'
    ]

    # Normalize category
    if category:
        category_map = {
            c.lower(): c
            for c in allowed_categories
        }

        category = category_map.get(
            category.lower(),
            ''
        )

    # --------------------------------------------------------
    # Get products
    # --------------------------------------------------------

    if category:

        all_products = query(
            '''
            SELECT *
            FROM products
            WHERE LOWER(TRIM(category)) = LOWER(%s)
            ORDER BY rating DESC
            ''',
            (category,),
            fetchall=True
        )

    else:

        all_products = query(
            '''
            SELECT *
            FROM products
            ORDER BY rating DESC
            ''',
            fetchall=True
        )

    all_products = all_products or []

    # --------------------------------------------------------
    # Personalized recommendations
    # --------------------------------------------------------

    recommended = recommend_products(
        skin_type,
        scores,
        budget,
        top_n=5
    ) or []

    # --------------------------------------------------------
    # IMPORTANT:
    # If category is selected, recommended products must
    # also belong to that category.
    # --------------------------------------------------------

    if category:

        recommended = [
            p for p in recommended
            if str(p.get('category', '')).strip().lower()
            == category.lower()
        ]

    return render_template(
        'products.html',
        all_products=all_products,
        recommended=recommended,
        analysis=analysis,
        user_name=session.get(
            'user_name',
            'User'
        ),
        selected_category=category
    )


# ============================================================
# PRODUCT COMPARISON
# ============================================================

@product_bp.route('/compare', methods=['GET', 'POST'])
@login_required
def compare():

    all_products = query(
        '''
        SELECT
            product_id,
            name,
            brand,
            category,
            price
        FROM products
        ORDER BY name
        ''',
        fetchall=True
    )

    comparison = None

    # --------------------------------------------------------
    # Latest analysis
    # --------------------------------------------------------

    analysis = query(
        '''
        SELECT *
        FROM skin_analyses
        WHERE user_id=%s
        ORDER BY analysis_date DESC
        LIMIT 1
        ''',
        (session['user_id'],),
        fetchone=True
    )

    skin_type = (
        analysis['skin_type']
        if analysis and analysis.get('skin_type')
        else 'Normal'
    )

    budget = (
        analysis['budget']
        if analysis and analysis.get('budget')
        else 1500
    )

    scores = analysis if analysis else {}

    # --------------------------------------------------------
    # Compare products
    # --------------------------------------------------------

    if request.method == 'POST':

        pid1 = request.form.get('product1')
        pid2 = request.form.get('product2')

        if pid1 and pid2 and pid1 != pid2:

            try:

                comparison = compare_products(
                    [
                        int(pid1),
                        int(pid2)
                    ],
                    skin_type,
                    scores,
                    budget
                )

            except (ValueError, TypeError):

                flash(
                    'Invalid product selection.',
                    'warning'
                )

        else:

            flash(
                'Please select two different products to compare.',
                'warning'
            )

    return render_template(
        'compare.html',
        all_products=all_products or [],
        comparison=comparison,
        user_name=session.get(
            'user_name',
            'User'
        )
    )


# ============================================================
# INGREDIENT ANALYZER
# ============================================================

@product_bp.route('/ingredients', methods=['GET', 'POST'])
@login_required
def ingredients():

    ingredient_data = None
    search_term = ''

    if request.method == 'POST':

        search_term = (
            request.form.get(
                'ingredient',
                ''
            )
            .strip()
        )

        if search_term:

            ingredient_data = get_ingredient_info(
                search_term
            )

            if not ingredient_data:

                flash(
                    f'No information found for "{search_term}".',
                    'warning'
                )

    all_ingredients = get_all_ingredients()

    return render_template(
        'ingredients.html',
        ingredient_data=ingredient_data,
        search_term=search_term,
        all_ingredients=all_ingredients,
        user_name=session.get(
            'user_name',
            'User'
        )
    )


# ============================================================
# PRODUCT DETAILS API
# ============================================================

@product_bp.route('/api/<int:product_id>')
@login_required
def api_product(product_id):

    product = query(
        '''
        SELECT *
        FROM products
        WHERE product_id=%s
        ''',
        (product_id,),
        fetchone=True
    )

    if not product:

        return jsonify({
            'error': 'Product not found'
        }), 404

    return jsonify(dict(product))


# ============================================================
# INGREDIENT API
# ============================================================

@product_bp.route('/api/ingredient/<name>')
@login_required
def api_ingredient(name):

    data = get_ingredient_info(name)

    if not data:

        return jsonify({
            'error': 'Not found'
        }), 404

    return jsonify(data)