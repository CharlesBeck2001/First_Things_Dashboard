import streamlit as st
import pandas as pd
import requests

# Accessing usernames and passwords from the secrets file
USER_CREDENTIALS = {
    st.secrets["credentials"]["user_name_1"]: st.secrets["credentials"]["password_1"],
    st.secrets["credentials"]["user_name_2"]: st.secrets["credentials"]["password_2"]
}

# Authentication function
def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Login form
if not st.session_state.authenticated:
    st.title("Login to Access Data")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

if st.session_state.authenticated:
    # Supabase URL and API Key (replace with your own details)
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    
    def execute_sql(query):
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
            "Range": "0-99999"  # Request more rows explicitly
        }
        # Endpoint for the RPC function
        rpc_endpoint = f"{supabase_url}/rest/v1/rpc/execute_sql"
            
        # Payload with the SQL query
        payload = {"query": query}
            
        # Make the POST request to the RPC function
        response = requests.post(rpc_endpoint, headers=headers, json=payload)
            
        # Handle response
        if response.status_code == 200:
            data = response.json()
                
            df = pd.DataFrame(data)
                
            print("Query executed successfully, returning DataFrame.")
            return(df)
        else:
            print("Error executing query:", response.status_code, response.json())
    
    
    # Define the SQL query to run
    sql_query = """
    SELECT 
        c.First_Name,
        c.Last_Name,
        c.primary_address,
        SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid,
        SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
    FROM 
        ft_customers c
    JOIN 
        ft_subscriber_transactions t
        ON c.customer_number = t.customer_number
    GROUP BY 
        c.customer_number, c.First_Name, c.Last_Name, c.primary_address
    LIMIT 100000
    """
    
    FT_Table = execute_sql(sql_query)
    
    FT_Table.rename(columns={
                "first_name": "First Name",
                "last_name": "Last Name",
                "primary_address": "Primary Address",
                "amount_paid": "Amount Paid",
                "gross_liability": "Gross Liability"
            }, inplace=True)
    
    FT_Table.index = FT_Table.index + 1
    
    
    # Your app's main content here
    st.title("First Things Customer Data")
    # Input box for user to specify N (default is empty)
    top_n = st.number_input("Show Top N Customers In Terms of Total Amount Paid (leave blank for all)", min_value=1, max_value=len(FT_Table), value=None, step=1, format="%d")
    
    # Filter only if the user provides an N value
    if top_n:
        FT_Table = FT_Table.nlargest(top_n, "Amount Paid")
    
    # Display the filtered table
    st.dataframe(FT_Table, use_container_width=True)
