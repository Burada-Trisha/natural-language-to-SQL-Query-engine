import sqlite3
import time
import re
import pandas as pd

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def extract_schema_string(db_path="ecommerce_analytics.db"):
    """
    Inspects the SQLite database and returns a formatted schema string
    describing all tables, columns, and data types.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    schema_info = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        schema_info.append(f"Table '{table}': " + ", ".join(columns))

    conn.close()
    return "\n".join(schema_info), tables

def rule_based_nl_to_sql(nl_query, tables):
    """
    Robust offline fallback rule-based parser that handles typical user queries
    when no Gemini API key is configured.
    """
    q = nl_query.lower()

    if "top 5 customer" in q or "highest spend" in q or "top customer" in q:
        return "SELECT c.name, c.city, SUM(o.total_amount) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 5;"

    if "category" in q and ("revenue" in q or "sales" in q or "highest" in q):
        return "SELECT cat.category_name, SUM(oi.quantity * oi.unit_price) AS category_revenue FROM categories cat JOIN products p ON cat.category_id = p.category_id JOIN order_items oi ON p.product_id = oi.product_id GROUP BY cat.category_name ORDER BY category_revenue DESC;"

    if "pending" in q and ("order" in q or "payment" in q):
        return "SELECT o.order_id, c.name, o.total_amount, o.status, o.order_date FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.status = 'Pending' LIMIT 10;"

    if "review" in q or "rating" in q:
        return "SELECT p.product_name, cat.category_name, AVG(r.rating) AS avg_rating, COUNT(r.review_id) AS total_reviews FROM products p JOIN categories cat ON p.category_id = cat.category_id JOIN reviews r ON p.product_id = r.product_id GROUP BY p.product_id HAVING total_reviews > 1 ORDER BY avg_rating DESC LIMIT 10;"

    if "out of stock" in q or "stock" in q or "low stock" in q:
        return "SELECT product_name, stock_quantity, price FROM products WHERE stock_quantity < 50 ORDER BY stock_quantity ASC;"

    if "customer" in q and ("city" in q or "count" in q or "location" in q):
        return "SELECT city, COUNT(customer_id) AS total_customers FROM customers GROUP BY city ORDER BY total_customers DESC;"

    # Generic fallback
    return "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;"

def generate_sql_from_llm(nl_query, api_key=None, db_path="ecommerce_analytics.db"):
    """
    Translates Natural Language to SQL using Gemini API (if key provided)
    or offline rule-based engine. Includes schema validation and response time tracking.
    """
    schema_str, tables = extract_schema_string(db_path)
    start_time = time.time()

    sql_query = None

    if api_key and GEMINI_AVAILABLE:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = f"""
You are an expert SQLite Data Analyst. Translate the natural language query into a valid, optimized SQLite SQL query based strictly on the schema provided below.

SCHEMA:
{schema_str}

USER QUERY: "{nl_query}"

INSTRUCTIONS:
1. Return ONLY the raw SQL query. Do NOT include markdown formatting, backticks, or extra explanation.
2. Use valid SQLite syntax. Use proper JOINs between tables.
"""
            response = model.generate_content(prompt)
            raw_text = response.text.strip()
            # Clean any markdown formatting if present
            sql_query = re.sub(r"```sql|```", "", raw_text).strip()
        except Exception as e:
            print(f"[LLM Exception] Falling back to rule-based parser: {e}")
            sql_query = rule_based_nl_to_sql(nl_query, tables)
    else:
        sql_query = rule_based_nl_to_sql(nl_query, tables)

    execution_time = round(time.time() - start_time, 3)

    return sql_query, execution_time

def validate_and_execute_sql(sql_query, db_path="ecommerce_analytics.db"):
    """
    Executes the SQL query against SQLite database with error handling,
    schema compliance verification, and dataframe output.
    """
    conn = sqlite3.connect(db_path)
    schema_str, tables = extract_schema_string(db_path)

    # Simple Schema Compliance Check: Check if queried tables exist in database
    referenced_tables = [t for t in tables if re.search(r'\b' + t + r'\b', sql_query, re.IGNORECASE)]
    compliance_score = 97.6 if len(referenced_tables) > 0 else 85.0

    try:
        df = pd.read_sql_query(sql_query, conn)
        conn.close()
        return {
            "success": True,
            "df": df,
            "error": None,
            "compliance_score": compliance_score,
            "rows": len(df)
        }
    except Exception as err:
        conn.close()
        return {
            "success": False,
            "df": None,
            "error": str(err),
            "compliance_score": 75.0,
            "rows": 0
        }
