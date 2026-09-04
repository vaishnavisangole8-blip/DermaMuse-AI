"""
Analysis Routes – Modules 2, 3, 4, 5, 6
Handles: Questionnaire, Photo Upload, AI Analysis, Scoring, Results
"""

import os
import uuid
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, current_app, jsonify)
from werkzeug.utils import secure_filename
from modules.auth import login_required
from modules.skin_ai import analyze_skin
from modules.recommendation import get_routine, recommend_products, compute_budget
from database.db import query

analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')


def allowed_file(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


# ── Step 1: Questionnaire + Photo Upload ─────────────────────────────────────

@analysis_bp.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    if request.method == 'POST':
        # ── Validate photo (optional) ──
        filename = None
        upload_path = None

        if 'photo' in request.files and request.files['photo'].filename != '':
            photo = request.files['photo']
            if not allowed_file(photo.filename):
                flash('Invalid file type. Use JPG, PNG or WEBP.', 'danger')
                return render_template('questionnaire.html')
            ext = photo.filename.rsplit('.', 1)[-1].lower()
            filename = f"{session['user_id']}_{uuid.uuid4().hex[:8]}.{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo.save(upload_path)

        # ── Collect questionnaire ──
        def safe_int(val, default=5):
            try: return max(0, min(10, int(val)))
            except: return default

        questionnaire = {
            'skin_type':     request.form.get('skin_type', 'Normal'),
            'q_oiliness':    safe_int(request.form.get('q_oiliness', 5)),
            'q_dryness':     safe_int(request.form.get('q_dryness', 5)),
            'q_sensitivity': safe_int(request.form.get('q_sensitivity', 5)),
            'q_acne_concern':safe_int(request.form.get('q_acne_concern', 5)),
            'sun_exposure':  request.form.get('sun_exposure', 'Medium'),
            'budget':        int(request.form.get('budget', 1500)),
        }

        # ── Run AI Analysis ──
        try:
            if upload_path:
                scores = analyze_skin(questionnaire, upload_path)
            else:
                # No image — use questionnaire-only scoring
                scores = analyze_skin(questionnaire, None)
        except Exception as e:
            current_app.logger.error(f"Analysis error: {e}")
            flash('Analysis failed. Please try again.', 'danger')
            return render_template('questionnaire.html')

        # ── Save to DB ──
        analysis_id = query(
            '''INSERT INTO skin_analyses
               (user_id, skin_type, q_oiliness, q_dryness, q_sensitivity,
                q_acne_concern, sun_exposure, budget,
                oiliness_score, dryness_score, sensitivity_score, concern_score,
                redness_score, pigmentation_score, overall_score, confidence,
                skin_profile, image_filename)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            (
                session['user_id'],
                questionnaire['skin_type'],
                questionnaire['q_oiliness'],
                questionnaire['q_dryness'],
                questionnaire['q_sensitivity'],
                questionnaire['q_acne_concern'],
                questionnaire['sun_exposure'],
                questionnaire['budget'],
                scores['oiliness_score'],
                scores['dryness_score'],
                scores['sensitivity_score'],
                scores['concern_score'],
                scores['redness_score'],
                scores['pigmentation_score'],
                scores['overall_score'],
                scores['confidence'],
                scores['skin_profile'],
                filename,
            ),
            commit=True
        )

        return redirect(url_for('analysis.results', analysis_id=analysis_id))

    return render_template('questionnaire.html')


# ── Step 2: Results / Dashboard ───────────────────────────────────────────────

@analysis_bp.route('/results/<int:analysis_id>')
@login_required
def results(analysis_id: int):
    analysis = query(
        'SELECT * FROM skin_analyses WHERE analysis_id=%s AND user_id=%s',
        (analysis_id, session['user_id']), fetchone=True
    )
    if not analysis:
        flash('Analysis not found.', 'warning')
        return redirect(url_for('analysis.start'))

    # Routine
    routine = get_routine(analysis['skin_type'], analysis)

    # Products
    products = recommend_products(
        skin_type=analysis['skin_type'],
        scores=analysis,
        budget=analysis['budget'],
        top_n=5
    )

    # Budget breakdown
    budget_data = compute_budget(products, analysis['budget'])

    # Save recommendations
    for p in products:
        query(
            '''INSERT IGNORE INTO recommendations
               (user_id, analysis_id, product_id, skin_match, concern_match,
                budget_match, final_score, routine_slot)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (session['user_id'], analysis_id, p['product_id'],
             p['skin_match'], p['concern_match'], p['budget_match'],
             p['final_score'], 'Both'),
            commit=True
        )

    return render_template(
        'results.html',
        analysis=analysis,
        routine=routine,
        products=products,
        budget_data=budget_data,
        user_name=session.get('user_name', 'User'),
    )


# ── API: get latest analysis for dashboard ────────────────────────────────────

@analysis_bp.route('/api/latest')
@login_required
def api_latest():
    row = query(
        '''SELECT * FROM skin_analyses WHERE user_id=%s
           ORDER BY analysis_date DESC LIMIT 1''',
        (session['user_id'],), fetchone=True
    )
    if not row:
        return jsonify({'error': 'No analysis found'}), 404
    # Convert datetime to string for JSON
    row = dict(row)
    if row.get('analysis_date'):
        row['analysis_date'] = str(row['analysis_date'])
    return jsonify(row)
