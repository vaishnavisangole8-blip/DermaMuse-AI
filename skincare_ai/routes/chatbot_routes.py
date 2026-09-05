"""
Chatbot & Voice Assistant Routes – Modules 12, 13
"""
from flask import (Blueprint, render_template, request,
                   session, jsonify)
from modules.auth import login_required
from modules.chatbot import chatbot_respond
from database.db import query

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')


@chatbot_bp.route('/')
@login_required
def chat_page():
    # Load recent chat history
    history = query(
        '''SELECT role, message, created_at FROM chat_history
           WHERE user_id=%s ORDER BY created_at DESC LIMIT 20''',
        (session['user_id'],), fetchall=True
    )
    history = list(reversed(history)) if history else []
    return render_template('chatbot.html',
                           history=history,
                           user_name=session.get('user_name', 'User'))


@chatbot_bp.route('/message', methods=['POST'])
@login_required
def message():
    data = request.get_json(silent=True) or {}
    user_msg = (data.get('message') or '').strip()

    if not user_msg:
        return jsonify({'error': 'Empty message'}), 400

    # Save user message
    query(
        'INSERT INTO chat_history (user_id, role, message) VALUES (%s,%s,%s)',
        (session['user_id'], 'user', user_msg), commit=True
    )

    # Generate response
    bot_reply = chatbot_respond(user_msg, user_id=session['user_id'])

    # Save bot response
    query(
        'INSERT INTO chat_history (user_id, role, message) VALUES (%s,%s,%s)',
        (session['user_id'], 'bot', bot_reply), commit=True
    )

    return jsonify({'reply': bot_reply})


@chatbot_bp.route('/clear', methods=['POST'])
@login_required
def clear_history():
    query(
        'DELETE FROM chat_history WHERE user_id=%s',
        (session['user_id'],), commit=True
    )
    return jsonify({'status': 'cleared'})
