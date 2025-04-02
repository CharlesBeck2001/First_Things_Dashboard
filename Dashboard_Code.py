import streamlit as st
import pandas as pd
import requests
from streamlit_cookies_manager import Cookies

# Initialize cookies manager
cookies = Cookies()

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

# Check if the user is already authenticated through cookies
if cookies.get("authenticated"):
    st.session_state.authenticated = True

# Login form
if not st.session_state.authenticated:
    st.title("Login to Access Data")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.session_state.authenticated = True
            cookies.set("authenticated", "true")  # Set cookie to indicate logged-in state
            cookies.save()  # Save the cookie
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
    
    FT_Table_OG = FT_Table
    # Your app's main content here
    st.title("First Things Customer Data")
    # Input box for user to specify N (default is empty)

    st.subheader("Filter Data By Total Amount and Gross Liability")
    top_n = st.number_input("Show Top N Customers In Terms of Total Amount Paid (leave blank for all)", min_value=1, max_value=len(FT_Table), value=None, step=1, format="%d")

    # Input box for user to specify N (default is empty)
    top_n_2 = st.number_input("Show Top N Customers In Terms of Total Liability (leave blank for all)", min_value=1, max_value=len(FT_Table), value=None, step=1, format="%d")
    
    # Filter only if the user provides an N value
    if top_n and not top_n_2:
        FT_Table = FT_Table.nlargest(top_n, "Amount Paid")

    if top_n_2 and not top_n:
        FT_Table = FT_Table.nlargest(top_n_2, "Gross Liability")

    if top_n and top_n_2:
        FT_Table_1 = FT_Table.nlargest(top_n, "Amount Paid")
        FT_Table_2 = FT_Table.nlargest(top_n_2, "Gross Liability")
        FT_Table = pd.concat([FT_Table_1, FT_Table_2])
        FT_Table = FT_Table.drop_duplicates()
        FT_Table = FT_Table.sort_values(by=['Amount Paid', 'Gross Liability'], ascending=[False, False])

    st.subheader("Overall Table Based On Your Limiting Criteria")
    st.dataframe(FT_Table, use_container_width=True)

    st.subheader("Search By Name")
    # --- Customer Search Filtering ---
    first_name_filter = st.text_input("Filter by First Name", "")
    last_name_filter = st.text_input("Filter by Last Name", "")
    
    # Initialize filtered dataframe as None
    filtered_df = None

    # Perform the search only if both first name or last name are provided
    if first_name_filter or last_name_filter:
        # Apply filters to the entire database (FT_Table)
        filtered_df = FT_Table_OG
        
        if first_name_filter:
            filtered_df = filtered_df[filtered_df["First Name"].str.contains(first_name_filter, case=False, na=False)]
        
        if last_name_filter:
            filtered_df = filtered_df[filtered_df["Last Name"].str.contains(last_name_filter, case=False, na=False)]
        
        # Display the distinct filtered dataframe if results are found
        if filtered_df.empty:
            st.write("No results found for the given search criteria.")
        else:
            st.subheader("Filtered Customer Data Based on Your Search")
            st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Search By Address")
    adress_filter = st.text_input("Filter by Address", "")

    if adress_filter:
        # Apply filters to the entire database (FT_Table)
        filtered_df_2 = FT_Table_OG
        
        if adress_filter:
            filtered_df_2 = filtered_df_2[filtered_df_2["Primary Address"].str.contains(adress_filter, case=False, na=False)]
        
        # Display the distinct filtered dataframe if results are found
        if filtered_df_2.empty:
            st.write("No results found for the given search criteria.")
        else:
            st.subheader("Filtered Customer Data Based on Your Search")
            st.dataframe(filtered_df_2, use_container_width=True)

    
    # Display the top N table if no search is applied, or show the full database
    #if not filtered_df:
    
    # Display the filtered table
    #st.dataframe(FT_Table, use_container_width=True)
