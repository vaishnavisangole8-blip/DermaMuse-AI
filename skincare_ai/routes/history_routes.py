"""
History / Before-After Routes – Module 15
"""
from flask import Blueprint, render_template, session, redirect, url_for, flash
from modules.auth import login_required
from database.db import query

history_bp = Blueprint('history', __name__, url_prefix='/history')


@history_bp.route('/')
@login_required
def history():
    analyses = query(
        '''SELECT analysis_id, analysis_date, skin_type, skin_profile,
                  overall_score, oiliness_score, dryness_score,
                  concern_score, sensitivity_score, confidence, budget
           FROM skin_analyses
           WHERE user_id=%s
           ORDER BY analysis_date DESC
           LIMIT 20''',
        (session['user_id'],), fetchall=True
    )
    analyses = analyses or []

    # Build before/after data
    before_after = None
    if len(analyses) >= 2:
        latest = analyses[0]
        oldest = analyses[-1]
        change = latest['overall_score'] - oldest['overall_score']
        before_after = {
            'initial_date':  str(oldest['analysis_date']),
            'current_date':  str(latest['analysis_date']),
            'initial_score': oldest['overall_score'],
            'current_score': latest['overall_score'],
            'change':        change,
            'direction':     'improved' if change > 0 else ('declined' if change < 0 else 'unchanged'),
        }

    return render_template(
        'history.html',
        analyses=analyses,
        before_after=before_after,
        user_name=session.get('user_name', 'User'),
    )


@history_bp.route('/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id: int):
    # Also removes photo from disk
    import os
    from flask import current_app
    row = query(
        'SELECT image_filename FROM skin_analyses WHERE analysis_id=%s AND user_id=%s',
        (analysis_id, session['user_id']), fetchone=True
    )
    if row and row.get('image_filename'):
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], row['image_filename'])
        if os.path.exists(path):
            os.remove(path)

    query(
        'DELETE FROM skin_analyses WHERE analysis_id=%s AND user_id=%s',
        (analysis_id, session['user_id']), commit=True
    )
    flash('Analysis deleted.', 'info')
    return redirect(url_for('history.history'))
