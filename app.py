# app.py

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your-secret-key-here")

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
USER_CREDENTIALS = {
    os.environ.get("USER_NAME_1"): os.environ.get("PASSWORD_1"),
    os.environ.get("USER_NAME_2"): os.environ.get("PASSWORD_2")
}

def execute_sql_count(query):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Range": "0-99999"
    }
    rpc_endpoint = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql_count"
    payload = {"query": query}
    
    response = requests.post(rpc_endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

def execute_sql_amount(query):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Range": "0-99999"
    }
    rpc_endpoint = f"{SUPABASE_URL}/rest/v1/rpc/execute_sql_amount"
    payload = {"query": query}
    
    response = requests.post(rpc_endpoint, headers=headers, json=payload)
    
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'authenticated' not in session or not session['authenticated']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if USER_CREDENTIALS.get(username) == password:
            session['authenticated'] = True
            response = make_response(redirect(url_for('dashboard')))
            response.set_cookie('authenticated', 'true', max_age=86400)  # 24 hours
            return response
        else:
            return render_template('base.html', error="Invalid credentials")
    
    return render_template('base.html')

@app.route('/')
@login_required
def dashboard():
    try:
        # Using the exact queries from your original code
        count_query = """
        SELECT 
            COUNT(*)
        FROM 
            sfg_customers c
        """

        amount_query = """
        SELECT 
            SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid
        FROM 
            sfg_customers c
        JOIN 
            sfg_subscriber_transactions t
            ON c.customer_number = t.customer_number
        """

        liability_query = """
        SELECT 
            SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
        FROM 
            sfg_customers c
        JOIN 
            sfg_subscriber_transactions t
            ON c.customer_number = t.customer_number
        """

        # Execute queries using the correct functions
        total_customers = int(execute_sql_count(count_query)['count'].iloc[0]) if not execute_sql_count(count_query).empty else 0
        total_amount_paid = float(execute_sql_amount(amount_query)['amount'].iloc[0]) if not execute_sql_amount(amount_query).empty else 0
        total_gross_liability = float(execute_sql_amount(liability_query)['amount'].iloc[0]) if not execute_sql_amount(liability_query).empty else 0
        
        # Calculate derived stats
        average_amount = total_amount_paid/total_customers if total_customers > 0 else 0
        profit = total_amount_paid - total_gross_liability

        return render_template('dashboard.html',
                             total_customers=total_customers,
                             total_amount=total_amount_paid,
                             total_liability=total_gross_liability,
                             average_amount=average_amount,
                             profit=profit)
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return render_template('dashboard.html',
                             error="Error loading dashboard data")

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect(url_for('login')))
    response.set_cookie('authenticated', '', expires=0)
    return response

if __name__ == '__main__':
    app.run(debug=True)