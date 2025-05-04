LLM_PROVIDER = "together"
LLM_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
MAX_TOKENS = 512


def build_prompt(context, prompt_type, custom_message=None):
    financial_context = f"""
--- INCOME ---
{context['income_str']}

--- EXPENSES ---
{context['expense_str']}

--- PLANNED EXPENSES ---
{context['planning_str']}

--- SUMMARY ---
Total Income: €{context['total_income']}
Total Expenses: €{context['total_expenses']}
Total Planned Expenses: €{context['total_planning']}
Balance (Income - Expenses): €{context['balance']}
Savings: €{context['total_savings']}
Extra amount needed to cover planned expenses: €{context['amount_to_cover_planning']}
"""

    if prompt_type == 'budget_analysis':
        return f"""
You are a financial advisor. Analyze the user's budget based on the provided financial data. Give a clear budget analysis, suggestions for improving the budget, and basic financial health advice.
{financial_context}
--- INSTRUCTIONS ---
1. Analyze whether the user is managing their budget well.
2. Identify any issues or risks.
3. Suggest changes or savings opportunities.
4. Offer general advice for stability and future planning.
5. Keep the tone helpful and realistic.
6. Provide a summary of the analysis.
7. Ask at the end if user want your help with budget planning and tell that on the right there is a button "Help planning budget".
"""
    elif prompt_type == 'planning_budget':
        return f"""
You are a financial planner. Help the user create a clear and realistic budget plan using their income, expenses, and planned expenses.
{financial_context}
--- INSTRUCTIONS ---
1. Allocate the user’s income into appropriate categories (needs, savings, future planning).
2. Suggest how much they should save monthly to cover upcoming planned expenses.
3. Recommend a monthly spending limit.
4. Identify any risks or imbalances in their current setup.
5. Offer a budget strategy they can follow for the next 1–3 months.
6. End by asking if they want to receive investment recommendations and point them to the "Investment Advice" button on the right.
"""
    elif prompt_type == 'investment_recommendation':
        return f"""
You are a financial advisor. Based on the user's current income, expenses, savings, and upcoming planning expenses, suggest smart and safe investment strategies.
{financial_context}
--- INSTRUCTIONS ---
1. Evaluate if the user is in a stable position to start investing.
2. Recommend suitable low- and medium-risk investment options (like ETFs, bonds, savings accounts, or fractional investing).
3. Suggest what percentage or amount of savings could be used for investments.
4. Provide short- and long-term investment tips.
5. Keep the tone friendly, realistic, and easy to understand.
6. End with a reminder that this is not professional financial advice, just general guidance.
"""
    elif prompt_type == 'custom' and custom_message:
        return f"""
--- RULES ---
1. ONLY respond to messages that are directly related to personal finance.
2. If the user's question is NOT about personal finance, do NOT answer it. Instead, reply with: "I'm here to help with personal finance questions only." And nothing else.
Otherwise, if the question is related to finance, respond normally.
3. If the question is about finance but not clear, ask the user to clarify in a finance-related way.
You are a financial assistant chatbot that helps users with personal finance topics only. These include:
- Income and salary
- Expenses and budgeting
- Saving strategies
- Planning future expenses
- Debt management
- Investment recommendations
- Emergency funds
- Retirement planning
3. If the question is partially related to finance but unclear, ask the user to clarify in a finance-related way.
4. Your tone should be friendly, professional, and supportive — like a financial coach.
5. If the user uses inappropriate or offensive language, politely refuse and remind them of proper use.

--- USER MESSAGE ---
{custom_message}
{financial_context}
"""
    else:
        return None


def get_ai_response(client, prompt):
    if not client or not prompt:
        return None, "Missing AI client or prompt."
    try:
        completion = client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS,
        )
        if completion.choices:
            return completion.choices[0].message.content, None
        else:
            return None, "AI returned no response."
    except Exception as e:
        print(f"ERROR: Exception during AI completion request: {e}")
        return None, f"Failed to get response from AI: {e}"