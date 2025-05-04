from flask import Blueprint, flash, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from . import db
from .models import ChatAI
from .ai_models.user_finances import get_user_financial_context
from .ai_models.ai_functionality import build_prompt, get_ai_response
from .ai_models.hug_client import get_huggingface_client

ai = Blueprint('ai', __name__)


def _save_chat_message(user_id, message, response):
    try:
        new_chat = ChatAI(user_id=user_id, message=message, response=response)
        db.session.add(new_chat)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        print(f"ERROR: Failed to save chat message for user {user_id}: {e}")
        return False, f"Database error saving chat: {e}"


@ai.route('/ai', methods=['GET', 'POST'])
@login_required
def home():
    user_id = current_user.id

    if request.method == 'POST':
        submit_action = request.form.get('submit')

        if submit_action == 'new_chat':
            try:
                ChatAI.query.filter_by(user_id=user_id).delete()
                db.session.commit()
                flash('New chat started! Previous messages cleared.', 'success')
            except Exception as e:
                db.session.rollback()
                print(f"ERROR: Failed deleting chat history for user {user_id}: {e}")
                flash('Error clearing chat history.', 'danger')
            return redirect(url_for('ai.home'))  # Redirect after POST

        financial_context = get_user_financial_context(user_id)
        if not financial_context:
            return redirect(url_for('ai.home'))

        prompt = None
        user_message_to_save = ""
        success_flash_message = ""

        if submit_action == 'budget_analysis':
            prompt = build_prompt(financial_context, 'budget_analysis')
            user_message_to_save = "Generate budget analysis"  # Represent user's click
            success_flash_message = "Budget analysis generated!"
        elif submit_action == 'planning_budget':
            prompt = build_prompt(financial_context, 'planning_budget')
            user_message_to_save = "Generate budget plan"  # Represent user's click
            success_flash_message = "Budget plan generated!"
        elif submit_action == 'investment_recommendation':
            prompt = build_prompt(financial_context, 'investment_recommendation')
            user_message_to_save = "Generate investment recommendations"  # Represent user's click
            success_flash_message = "Investment recommendations generated!"
        elif submit_action == 'custom':
            custom_text = request.form.get('customRequestText', '').strip()
            if not custom_text:
                flash('Please enter your custom request message.', 'warning')
                chats = ChatAI.query.filter_by(user_id=user_id).all()
                return render_template('ai.html', chats=chats, user=current_user)
            else:
                prompt = build_prompt(financial_context, 'custom', custom_message=custom_text)
                user_message_to_save = custom_text  # Save the actual user query
                success_flash_message = "Response to your custom request generated!"
        else:
            flash('Invalid action selected.', 'danger')
            chats = ChatAI.query.filter_by(user_id=user_id).all()
            return render_template('ai.html', chats=chats, user=current_user)

        if prompt:
            client = get_huggingface_client()
            if client:
                ai_response, error = get_ai_response(client, prompt)
                if error:
                    flash(f"AI Error: {error}", "danger")
                else:
                    saved, db_error = _save_chat_message(user_id, user_message_to_save, ai_response)
                    if saved:
                        flash(success_flash_message, 'success')
                    else:
                        flash(f"AI response received, but failed to save: {db_error}", 'danger')

        return redirect(url_for('ai.home'))

    chats = ChatAI.query.filter_by(user_id=user_id).all()
    return render_template('ai.html', chats=chats, user=current_user)