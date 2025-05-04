# Personal Financial Management System

## 1. Introduction

### a. What is your application?

This application is a web-based personal financial management system designed to help users track their income, expenses, planned future expenses, and savings. It allows users to input their financial data, view summaries and filtered reports, manage savings transfers/withdrawals, and receive AI-powered insights into their budget, planning, and investment potential. The system aims to provide a clear overview of personal finances and offer guidance for better financial health.

### b. How to run the program?

1.  **Prerequisites:** Python 3.x, pip.
2.  **Clone Repository:** Clone the project repository from GitHub:
    ```bash
    git clone [https://github.com/EdwinKeizik/Personal-Financial-Management-System.git](https://github.com/EdwinKeizik/Personal-Financial-Management-System.git)
    cd Personal-Financial-Management-System
    ```
3.  **Create Virtual Environment:**
    ```bash
    python -m venv .venv
    # Activate the environment:
    # Windows:
    .venv\Scripts\activate
    # Linux/macOS:
    source .venv/bin/activate
    ```
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Environment Variables Setup:**
    * Create a file named `.env` in the project root directory.
    * Add the following lines, replacing placeholders with your actual values:
      ```env
      SECRET_KEY=<Your_Generated_Flask_Secret_Key>
      HUGGINGFACE_API_KEY=<Your_Hugging_Face_API_Token_Accepted_By_TogetherAI>
      ```
    * Generate a `SECRET_KEY` using Python: `import secrets; print(secrets.token_hex(24))`
    * Ensure `.env` is listed in your `.gitignore` file.
6.  **Database Setup:**
    * Initialize the database. Open a Python shell within the activated virtual environment (`flask shell` or `python`) and run:
      ```python
      from website import db, create_app
      app = create_app()
      with app.app_context():
          db.create_all()
      exit()
      ```
7.  **Run Application:**
    ```bash
    flask run
    ```
8.  **Access:** Open your web browser and navigate to `http://127.0.0.1:5000/`.

### c. How to use the program?

1.  **Register:** Navigate to the `/register` page (usually linked from the login/home page if not logged in) and create a new user account with a unique username (min 4 characters) and password (min 8 characters, different from username).
2.  **Login:** Use your registered credentials via the `/login` page.
3.  **Dashboard/Index:** After login, the main view (`/`) displays forms for adding income, expenses, and planned expenses. It also shows filterable lists of existing entries.
4.  **Add Data:** Fill in the respective forms (Income, Expenses, Planning) with amount, name, date, and type (for Income/Expenses) and submit.
5.  **View/Filter Data:** Use the filter options (Amount, Name, Date, Type) above the lists on the main page to view specific records.
6.  **Delete Data:** Click the delete button next to an entry in the lists to remove it.
7.  **Report Page:** Navigate to the `/report` page. This displays overall financial totals (Income, Expenses, Planning, Savings, Balance, Coverage).
8.  **Savings Management (on Report Page):** Use the Transfer/Withdraw forms to move money into savings or take money out of savings.
9.  **AI Assistance Page:** Navigate to the `/ai` page.
    * Click buttons ("Generate budget analysis", "Generate budget plan", "Generate investment recommendations") to get AI insights based on your current financial data.
    * Use the custom request text box to ask specific finance-related questions.
    * Start a new chat session using the "New Chat" button to clear previous AI messages.

## 2. Body/Analysis

### a. Functional Requirements Coverage

The application implements core features for personal finance management:

* **User Authentication:** Secure user registration and login (`auth.py` using Flask-Login, Werkzeug for hashing).
* **Data Entry:** Forms for adding Income, Expenses, and Planned Expenses (`views.py`, `submit_finances.py`). Input validation is performed (`finance_management.py`).
* **Data Display & Filtering:** The main view displays lists of income, expenses, and planning records. Users can filter these lists based on amount, name, date, and type (`views.py`, `filters.py`).
* **Data Deletion:** Users can delete individual financial records (`views.py`, `delete_finances.py`).
* **Reporting:** A dedicated report page calculates and displays total income, expenses, planning, savings, current balance, and the amount needed to cover planned expenses (`report.py`, `report_calculations.py`).
* **Savings Management:** Functionality to transfer funds to savings and withdraw from savings, updating the savings total (`report.py`, `savings_handler.py`, `finance_collector.py`). Input validation specific to transfers/withdrawals (e.g., sufficient balance) is included.
* **AI Analysis:** An AI assistant page provides automated budget analysis, planning suggestions, and investment recommendations based on the user's data. It also supports custom finance-related queries (`ai.py`, `ai_functionality.py`, `user_finances.py`, `hug_client.py`).
* **Data Persistence:** Financial data and user information are stored persistently using a database, managed via Flask-SQLAlchemy (`models.py`, `db` object).

### b. OOP Pillars

The application utilizes the four pillars of Object-Oriented Programming:

1.  **Inheritance:** This is clearly demonstrated where specific financial record types inherit properties and potentially methods from a base concept.
    * `Expenses` and `Planning` inherit from `Income` in `finance_management.py`. This allows them to share the common `__init__` and `check_input` logic (though `Planning` overrides `check_date`).
    * `Transfer` and `Withdraw` inherit from `Savings` in `finance_collector.py`, reusing the basic amount validation logic (`super().check_input()`) before adding their specific balance checks.

    ```python
    # finance_management.py
    class Income:
        # ... common attributes and methods ...
        def check_input(self): # Base validation
            # ... implementation ...
        def check_date(self): # Base date check
            # ... implementation ...

    class Expenses(Income): # Inherits from Income
        pass # Uses Income's methods directly

    class Planning(Income): # Inherits from Income
        def check_date(self): # Overrides check_date
            # ... specific implementation for future dates ...
    ```

2.  **Abstraction:** Abstraction hides complex implementation details behind simpler interfaces.
    * The various handler functions (`process_form_submission`, `process_delete_request`, `handle_transfer`, `handle_withdraw`, `get_user_financial_context`) abstract the logic for specific actions. The Flask view functions call these handlers without needing to know the intricate details of form processing, database interaction, or validation.
    * The model classes (`User`, `Income`, `Savings`, etc.) abstract the underlying database tables and SQL operations. Code interacts with Python objects and methods (`.query`, `.filter_by`, `.all()`) instead of raw SQL.
    * The validation classes (`Income`, `Expenses`, `Planning`, `Savings`, `Transfer`, `Withdraw` in `finance_management.py` and `finance_collector.py`) provide a simple `check_input()` method that hides the specific validation rules within.

    ```python
    # views.py - Abstraction Example
    @views.route("/", methods=["GET", "POST"])
    @login_required
    def home():
        if request.method == "POST":
            # Complex submission logic hidden behind this function call
            process_form_submission(request, current_user)
            # Complex deletion logic hidden behind this function call
            process_delete_request(request, current_user)
        # ... filtering and rendering ...
        # Filter logic hidden behind this function call
        filtered_reports = filter_reports(...)
        # ...
    ```

3.  **Encapsulation:** This principle involves bundling data (attributes) and methods that operate on that data within a single unit (a class).
    * All the model classes (`User`, `Income`, `Expenses`, `Planning`, `Savings`, `ChatAI`) encapsulate financial or user data (like `amount`, `name`, `date`, `username`, `password`) along with database-related behavior provided by Flask-SQLAlchemy (`db.Model`).
    * The validation classes (`Income`, `Savings`, etc. in `finance_management.py` / `finance_collector.py`) encapsulate the data needed for validation (`amount`, `balance`, etc.) and the validation methods (`check_input`, `check_date`, `check_balance`).

    ```python
    # finance_collector.py - Encapsulation Example
    class Savings:
        def __init__(self, amount, user_id):
            # Data attributes
            self.amount = amount
            self.user_id = user_id

        def check_input(self): # Method operating on the data
            # ... validation logic using self.amount ...
            pass
    ```

4.  **Polymorphism:** Polymorphism allows objects of different classes to be treated as objects of a common superclass, often involving method overriding.
    * In `finance_management.py`, both `Income` and `Planning` have a `check_date` method. While `Expenses` uses the `Income` version via inheritance, `Planning` provides its own specific implementation (checking for past dates instead of future dates). An object could call `.check_date()` and get different behavior depending on whether it's an `Income`/`Expenses` instance or a `Planning` instance.
    * In `submit_finances.py`, the code uses generic variable names `ItemClass` and `ItemModel`. Based on the `submit` value, these variables are assigned different *specific* classes (`IncomeClass`/`IncomeModel`, `ExpensesClass`/`ExpensesModel`, etc.). The subsequent code (`item = ItemClass(...)`, `new_item = ItemModel(...)`, `item.check_input()`) works polymorphically with whichever specific class was assigned.

    ```python
    # submit_finances.py - Polymorphism Example
    # ... determine ItemClass based on submit value ...
    item = ItemClass(amount, name, date, item_type, current_user.id)
    # The check_input method called depends on which class ItemClass refers to
    if item.check_input():
        # ... determine ItemModel based on submit value ...
        new_item = ItemModel(...) # Creates instance of specific model
        db.session.add(new_item)
        # ...
    ```

### c. Design Pattern

The **Factory Method** pattern is utilized in the `get_huggingface_client` function within `hug_client.py`.

* **What it is:** The Factory Method pattern defines an interface (in this case, simply the function signature `get_huggingface_client()`) for creating an object, but lets subclasses (or in this functional approach, the function itself) decide which class to instantiate. It decouples the client code (which needs an `InferenceClient`) from the concrete implementation details of creating that client.
* **How it works here:** The `get_huggingface_client()` function centralizes the logic for creating an `InferenceClient` instance. It handles fetching the API key **from the environment**, checking if it exists, selecting the provider (via `LLM_PROVIDER`), and encapsulating the `try-except` block for potential instantiation errors.
* **Why it's suitable:**
    * It centralizes the creation logic for the `InferenceClient`. If the way the client needs to be created changes (e.g., different provider options, different ways of getting API keys, additional configuration), the change only needs to happen inside this function, not everywhere a client is needed.
    * It abstracts the instantiation complexity (including error handling and API key retrieval logic) away from the code that *uses* the client (like the `ai.py` blueprint). The calling code simply asks for a client without worrying about *how* it's made.
    * Compared to **Singleton**, this function doesn't *enforce* that only one instance exists (though it could be modified to do so if desired). The primary goal here seems to be encapsulating creation logic, not guaranteeing singularity.
    * Compared to **Abstract Factory**, which creates families of related objects, Factory Method is simpler and sufficient here as we are only creating one type of product (the `InferenceClient`).

```python
# hug_client.py - Factory Method Example
import os
from huggingface_hub import InferenceClient
# from ..config import LLM_PROVIDER # Assuming provider defined elsewhere

def get_huggingface_client(): # The "Factory Method"
    api_key = os.getenv("HUGGINGFACE_API_KEY") # Configuration detail
    if not api_key:
        # ... error handling ...
        return None
    try:
        # Creates the specific product (InferenceClient)
        client = InferenceClient(
            # provider=LLM_PROVIDER, # Pass provider if needed
            token=api_key, # Use token parameter
        )
        return client # Returns the created product
    except Exception as e:
        # ... error handling ...
        return None
d. Composition / Aggregation
Composition is demonstrated through the database relationships defined in models.py. The User model uses db.relationship to establish a compositional link with other models like Income, Expenses, Planning, Savings, and ChatAI.

A User object essentially "has" or is "composed of" a collection of Income records, Expenses records, etc.
The lifecycle of these related records is typically managed alongside the User (e.g., if a User is deleted, associated records might also be deleted depending on cascade settings, though this isn't explicitly shown in the provided model definition).
This represents a strong "has-a" relationship where the parts (income, expenses) belong to the whole (user).
Python

# models.py - Composition Example
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    # User "has-a" collection of Income objects
    income = db.relationship("Income")
    # User "has-a" collection of Expenses objects
    expenses = db.relationship("Expenses")
    planning = db.relationship("Planning")
    savings = db.relationship("Savings")
    chat_ai = db.relationship("ChatAI")
Aggregation is a weaker "has-a" relationship where objects might refer to each other but don't necessarily own each other's lifecycle. While less distinct, one could argue that when get_report_data fetches various lists (income, expenses, etc.) and passes them to calculation functions, those functions temporarily aggregate the data without owning it. However, the SQLAlchemy relationships are a clearer example of composition.

e. Reading from / Writing to File
The application utilizes a database for persistent storage of user data and financial records, fulfilling this requirement's allowance for alternatives to flat files.

Flask-SQLAlchemy is used (implied by db.Model, db.Column, db.session).
The models.py file defines the structure of the data through classes inheriting from db.Model (User, Income, Expenses, Planning, Savings, ChatAI). These classes map to database tables.
Data is written to the database when new records are created (e.g., in submit_finances.py, savings_handler.py, auth.py, ai.py) using:
new_item = ItemModel(...) or new_user = User(...) etc.
db.session.add(new_item)
db.session.commit()
Data is read from the database when retrieving user information or financial records for display, reporting, or filtering (e.g., in get_financial_data, filter_reports, auth.py, ai.py) using methods like:
Model.query.filter_by(...).all()
Model.query.filter_by(...).first()
Python

# submit_finances.py - Writing Example
# ... determine ItemModel ...
new_item = ItemModel( # Create model instance
    amount=item.amount,
    # ... other attributes ...
    user_id=current_user.id,
)
db.session.add(new_item) # Add to session
db.session.commit() # Write to database

# report_calculations.py - Reading Example
def get_financial_data(user_id):
    # Read all matching records from database
    income = IncomeModel.query.filter_by(user_id=user_id).all()
    expenses = ExpensesModel.query.filter_by(user_id=user_id).all()
    # ... etc ...
    return income, expenses, planning, savings
f. Testing
Unit tests were created using Python's built-in unittest framework and the unittest.mock library to isolate components and verify their logic without relying on external services or a live database.

Coverage: Tests were written for various modules, including data validation classes (finance_collector.py, finance_management.py), data processing functions (delete_finances.py, submit_finances.py, savings_handler.py), report calculations (report_calculations.py), data fetching/formatting (get_report.py, user_finances.py), AI integration (ai_functionality.py, hug_client.py), database models (models.py), database filtering (filters.py), authentication (auth.py), and attempted for the main view blueprints (ai.py, report.py, views.py).
Mocking: Dependencies such as database models, external API clients (InferenceClient), Flask functions (flash, redirect, render_template, etc.), and helper functions were mocked using @patch to ensure tests focused on the logic of the unit under test.
Python

# Example from test_report_calculations.py
class TestReportCalculation(unittest.TestCase):

    @patch(PATCH_TARGET_SAVINGS)
    @patch(PATCH_TARGET_PLANNING)
    @patch(PATCH_TARGET_EXPENSES)
    @patch(PATCH_TARGET_INCOME)
    def test_get_financial_data(
        self, mock_income_model, mock_expenses_model,
        mock_planning_model, mock_savings_model
    ):
        user_id_to_test = 5
        # ... setup mock return values ...
        mock_income_model.query.filter_by.return_value.all.return_value = [...]
        # ...

        # Call function under test
        income, expenses, planning, savings = get_financial_data(user_id_to_test)

        # Assertions
        mock_income_model.query.filter_by.assert_called_once_with(user_id=user_id_to_test)
        # ... other assertions ...
        self.assertEqual(income, [...])
Challenges & Current Status: While aiming for comprehensive coverage, significant challenges were encountered when testing Flask view functions decorated with @login_required (ai.py, report.py, views.py). Standard mocking techniques involving creating Flask application/request contexts and patching the decorator led to persistent errors (AttributeError related to login_manager or TypeError related to mock arguments). As troubleshooting these proved difficult within the project timeline and pure unit testing approach, the corresponding test files (test_ai.py, test_report.py, test_views.py) currently contain failing tests related to these views and might have been temporarily renamed (e.g., not_ai.py) to exclude them from default test discovery. Additionally, other test files follow mixed naming conventions (*_test.py vs test_*.py), impacting default test discovery.
g. Code Style
The Python code was formatted to adhere to the PEP 8 style guidelines, ensuring consistency in indentation, spacing, line length, naming conventions, and overall structure. This was done iteratively using code formatting tools and manual review based on the PEP 8 standard.

3. Results and Summary
a. Results
The project successfully implements a multi-functional personal finance web application prototype.
Core functionalities including user management, CRUD operations for financial data, filtering, reporting, and savings tracking were developed.
Object-Oriented principles (Inheritance, Abstraction, Encapsulation, Polymorphism) and a design pattern (Factory Method) were incorporated.
Integration with an external AI service (via Together AI accessed with huggingface_hub library) for financial analysis and advice was added, using secure API key handling via environment variables.
Significant challenges were encountered in reliably unit testing Flask view functions protected by @login_required, leading to unresolved errors and incomplete test coverage for the main blueprints (ai, report, views).
b. Conclusions
This coursework resulted in a functional web application for personal finance management, demonstrating the integration of database persistence, user authentication, core financial tracking features, and AI-powered assistance. The project structure adheres to OOP principles and utilizes a Factory Method pattern for external service client creation.

The primary limitation is the difficulty encountered in unit testing the main Flask views due to interactions with the @login_required decorator and Flask's context management within a mocked environment. These tests remain incomplete or failing. Future work must prioritize resolving these testing issues, potentially by adopting Flask's test client approach, which simulates HTTP requests and handles context more naturally. Standardizing test file naming conventions (e.g., to test_*.py) is also recommended for reliable test discovery.

Future functional prospects include adding data visualization, budget goal tracking, more detailed reporting, user profile settings, and refining the AI interaction prompts and capabilities. Addressing the testing gaps is essential for stable future development.

4. Optional: Resources
Flask Documentation: https://flask.palletsprojects.com/
Flask-Login Documentation: https://flask-login.readthedocs.io/
Flask-SQLAlchemy Documentation: https://flask-sqlalchemy.palletsprojects.com/
SQLAlchemy Documentation: https://www.sqlalchemy.org/
Hugging Face Hub Client Library: https://huggingface.co/docs/huggingface_hub/index
Together AI Documentation: https://docs.together.ai/
Python unittest Documentation: https://docs.python.org/3/library/unittest.html
Python unittest.mock Documentation: https://docs.python.org/3/library/unittest.mock.html
PEP 8 Style Guide: https://peps.python.org/pep-0008/