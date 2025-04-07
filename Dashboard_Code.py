import streamlit as st
import os
import pandas as pd
import requests
from streamlit_cookies_manager import EncryptedCookieManager
import plotly.graph_objects as go
from plotly.subplots import make_subplots


st.set_page_config(layout="wide")
# Initialize the cookie manager
# This should be on top of your script
cookies = EncryptedCookieManager(
    # This prefix will get added to all your cookie names.
    # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
    prefix="ktosiek/streamlit-cookies-manager/",
    # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
    password=os.environ.get("COOKIES_PASSWORD", st.secrets["credentials"]["cookies_password"]),
)
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

#if cookies["authenticated"] == "true":
#        st.session_state.authenticated = True
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

if "authenticated" not in cookies:
    cookies["authenticated"] = "false"

if cookies.get("authenticated") == "true":
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
            cookies["authenticated"] = "true"  # Set cookie to indicate logged-in state
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


    def execute_sql_count(query):
         headers = {
             "apikey": supabase_key,
             "Authorization": f"Bearer {supabase_key}",
             "Content-Type": "application/json",
             "Range": "0-99999"  # Request more rows explicitly
         }
         # Endpoint for the RPC function
         rpc_endpoint = f"{supabase_url}/rest/v1/rpc/execute_sql_count"
             
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


    def execute_sql_count(query):
         headers = {
             "apikey": supabase_key,
             "Authorization": f"Bearer {supabase_key}",
             "Content-Type": "application/json",
             "Range": "0-99999"  # Request more rows explicitly
         }
         # Endpoint for the RPC function
         rpc_endpoint = f"{supabase_url}/rest/v1/rpc/execute_sql_count"
             
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

    def execute_sql_amount(query):
         headers = {
             "apikey": supabase_key,
             "Authorization": f"Bearer {supabase_key}",
             "Content-Type": "application/json",
             "Range": "0-99999"  # Request more rows explicitly
         }
         # Endpoint for the RPC function
         rpc_endpoint = f"{supabase_url}/rest/v1/rpc/execute_sql_amount"
             
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

    
    def execute_sql_paginated(query, target_rows=2500, row_limit=1000):
        
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }
    
        # Endpoint for the RPC function
        rpc_endpoint = f"{supabase_url}/rest/v1/rpc/execute_sql_pagination"
    
        # Initialize list to store the results
        all_data = []
        start_row = 0
        fetched_rows = 0
    
        # Start the pagination loop
        while fetched_rows < target_rows:
            # Payload with the SQL query, including the current offset and row_limit
            payload = {
                "query": query,
                "page_offset": start_row,
                "row_limit": row_limit
            }
    
            # Make the API call to Supabase's execute_sql_pagination function
            response = requests.post(rpc_endpoint, headers=headers, json=payload)
    
            if response.status_code == 200:
                data = response.json()
                print(f"Fetched {len(data)} rows from offset {start_row}")  # Debugging line
    
                if not data:  # No more data left to fetch
                    print("No more data left to fetch.")
                    break
    
                # Add the current batch of data to the list
                all_data.extend(data)
                fetched_rows += len(data)
    
                # If we've reached the target number of rows, stop
                if fetched_rows >= target_rows:
                    break
    
                # Increment the starting row for the next page
                start_row += row_limit
            else:
                print(f"Error executing query: {response.status_code}")
                print(f"Response: {response.json()}")
                break
    
        # Convert the accumulated data to a DataFrame
        df = pd.DataFrame(all_data)
    
        # If we've collected more rows than requested, slice to target_rows
        df = df.head(target_rows)
    
        print(f"Fetched {fetched_rows} rows.")
        return df
    

    count_query = """
    SELECT 
        COUNT(*)
    FROM 
        ft_customers c
    """

    amount_query = """
    SELECT 
        SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid
    FROM 
        ft_customers c
    JOIN 
        ft_subscriber_transactions t
        ON c.customer_number = t.customer_number
    """

    liability_query = """
    SELECT 
        SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
    FROM 
        ft_customers c
    JOIN 
        ft_subscriber_transactions t
        ON c.customer_number = t.customer_number
    """
    
    # Define the SQL query to run
    
    # Your app's main content here
    st.title("First Things Customer Data")
    st.subheader("First Things Stats")

    # Create columns for the stat boxes
    col1, col2, col3 = st.columns(3)
    
    # Calculate the totals
    total_customers = int(execute_sql_count(count_query)['count'][0])
    total_amount_paid = float(execute_sql_amount(amount_query)['amount'][0])
    total_gross_liability = float(execute_sql_amount(liability_query)['amount'][0])
    
    # Add stat boxes in columns
    with col1:
        # Use a container to wrap the metric with custom CSS for box styling
        with st.container():
            st.markdown(
                f"""
                <div style="border: 2px solid white; padding: 20px; border-radius: 10px; background-color: black; color: white;">
                    <h3 style="font-size: 16px;">Total Customers</h3>
                    <h4 style="font-size: 24px;">{total_customers:,}</h4>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown(
                f"""
                <div style="border: 2px solid white; padding: 20px; border-radius: 10px; background-color: black; color: white;">
                    <h3 style="font-size: 16px;">Total Amount Paid</h3>
                    <h4 style="font-size: 24px;">${total_amount_paid:,.2f}</h4>
                </div>
                """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown(
                f"""
                <div style="border: 2px solid white; padding: 20px; border-radius: 10px; background-color: black; color: white;">
                    <h3 style="font-size: 16px;">Total Gross Liability</h3>
                    <h4 style="font-size: 24px;">${total_gross_liability:,.2f}</h4>
                </div>
                """, unsafe_allow_html=True)


    # Add margin below the metric boxes to create space between them and the next section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Input box for user to specify N (default is empty)
    st.subheader("Filter Data By Total Amount and Gross Liability")
    top_n = st.number_input("Show Top N Customers In Terms of Total Amount Paid (leave blank for all)", min_value=1, max_value=total_customers, value=None, step=1, format="%d")

    # Input box for user to specify N (default is empty)
    top_n_2 = st.number_input("Show Top N Customers In Terms of Total Liability (leave blank for all)", min_value=1, max_value=total_customers, value=None, step=1, format="%d")

    if not top_n and not top_n_2:

        sql_query = f"""
        SELECT 
            DISTINCT c.First_Name,
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
        LIMIT 1000;
        """

        FT_Table = execute_sql(sql_query)
        
        FT_Table.rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "primary_address": "Primary Address",
                    "amount_paid": "Amount Paid",
                    "gross_liability": "Gross Liability"
                }, inplace=True)

        FT_Table = FT_Table.drop_duplicates()
        
        FT_Table.index = FT_Table.index + 1

            # Create the new column: Amount Paid - Gross Liability
        FT_Table["Net Paid"] = FT_Table["Amount Paid"] - FT_Table["Gross Liability"]

        st.subheader("Table Containing The First 1000 Entries In Database (Representative Sample)")
        st.dataframe(FT_Table, use_container_width=True)
        
        # Create subplots layout: 1 row, 3 columns
        fig = make_subplots(rows=1, cols=3, subplot_titles=(
            "Distribution of Amount Paid",
            "Distribution of Gross Liability",
            "Distribution of Net Paid (Amount Paid - Gross Liability)"
        ))
        
        # Histogram 1: Amount Paid
        fig.add_trace(
            go.Histogram(x=FT_Table["Amount Paid"], name="Amount Paid"),
            row=1, col=1
        )
        
        # Histogram 2: Gross Liability
        fig.add_trace(
            go.Histogram(x=FT_Table["Gross Liability"], name="Gross Liability"),
            row=1, col=2
        )
        
        # Histogram 3: Net Paid
        fig.add_trace(
            go.Histogram(x=FT_Table["Net Paid"], name="Net Paid"),
            row=1, col=3
        )
        
        # Layout tweaks for aesthetics
        fig.update_layout(
            title_text="",
            height=400,
            width=1200,
            showlegend=False,
            template="plotly_white"
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Amount Paid", row=1, col=1)
        fig.update_xaxes(title_text="Gross Liability", row=1, col=2)
        fig.update_xaxes(title_text="Net Paid", row=1, col=3)
        
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=3)
        
        # Show the interactive plot
        st.subheader("Distribution of Information In Above Data")
        st.plotly_chart(fig, use_container_width=True)
        
        FT_Table_OG = FT_Table
    
    # Filter only if the user provides an N value
    if top_n and not top_n_2:
        
        sql_query = f"""
        SELECT 
            DISTINCT c.First_Name,
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
        ORDER BY 
            amount_paid DESC
        """
        
        FT_Table = execute_sql_paginated(sql_query, target_rows=top_n, row_limit=1000)
        
        FT_Table.rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "primary_address": "Primary Address",
                    "amount_paid": "Amount Paid",
                    "gross_liability": "Gross Liability"
                }, inplace=True)

        #st.write(len(FT_Table))
        
        #FT_Table = FT_Table.drop_duplicates()

        #st.write(len(FT_Table))
        
        FT_Table.index = FT_Table.index + 1
        
        FT_Table_OG = FT_Table
        st.subheader("Overall Table Based On Your Limiting Criteria")
        st.dataframe(FT_Table, use_container_width=True)
        
        #FT_Table = FT_Table.nlargest(top_n, "Amount Paid")

    if top_n_2 and not top_n:
        
        sql_query_2 = f"""
        SELECT 
            DISTINCT c.First_Name,
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
        ORDER BY 
            gross_liability DESC
        """
        
        FT_Table_2 = execute_sql_paginated(sql_query_2, target_rows=top_n_2, row_limit=1000)
        
        FT_Table_2.rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "primary_address": "Primary Address",
                    "amount_paid": "Amount Paid",
                    "gross_liability": "Gross Liability"
                }, inplace=True)
        
        #FT_Table_2 = FT_Table_2.drop_duplicates()
        
        FT_Table_2.index = FT_Table_2.index + 1

        FT_Table = FT_Table_2
        
        FT_Table_OG = FT_Table_2
        st.subheader("Overall Table Based On Your Limiting Criteria")
        st.dataframe(FT_Table, use_container_width=True)
        
        #FT_Table = FT_Table.nlargest(top_n_2, "Gross Liability")

    if top_n and top_n_2:

        top_v = max(top_n, top_n_2)
        
        sql_query_1 = f"""
        SELECT 
            DISTINCT c.First_Name,
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
        ORDER BY 
            amount_paid DESC, gross_liability DESC
        """
        
        FT_Table_1 = execute_sql_paginated(sql_query_1, target_rows=top_v, row_limit=1000)
        
        FT_Table_1.rename(columns={
                    "first_name": "First Name",
                    "last_name": "Last Name",
                    "primary_address": "Primary Address",
                    "amount_paid": "Amount Paid",
                    "gross_liability": "Gross Liability"
                }, inplace=True)
        
        FT_Table_1.index = FT_Table_1.index + 1

        FT_Table = FT_Table_1

        #FT_Table = FT_Table.sort_values(by=['Amount Paid', 'Gross Liability'], ascending=[False, False])

        #FT_Table = FT_Table.reset_index(drop=True)
        #FT_Table.index = FT_Table.index + 1
        FT_Table_OG = FT_Table
        #FT_Table_1 = FT_Table.nlargest(top_n, "Amount Paid")
        #FT_Table_2 = FT_Table.nlargest(top_n_2, "Gross Liability")
        #FT_Table = pd.concat([FT_Table_1, FT_Table_2])
        #FT_Table = FT_Table.drop_duplicates()
        #FT_Table = FT_Table.sort_values(by=['Amount Paid', 'Gross Liability'], ascending=[False, False])

        st.subheader("Overall Table Based On Your Limiting Criteria")
        st.dataframe(FT_Table, use_container_width=True)

    st.subheader("Search By Name")
    # --- Customer Search Filtering ---
    first_name_filter = st.text_input("Filter by First Name", "")
    last_name_filter = st.text_input("Filter by Last Name", "")
    
    # Initialize filtered dataframe as None
    filtered_df = None
    filtered_df_2 = None

    # Perform the search only if both first name or last name are provided
    if first_name_filter or last_name_filter:
        # Apply filters to the entire database (FT_Table)
        #filtered_df = FT_Table_OG

        
        if first_name_filter and last_name_filter:
            #filtered_df = filtered_df[filtered_df["First Name"].str.contains(first_name_filter, case=False, na=False)]

            name_query = f"""
            SELECT 
                DISTINCT c.First_Name,
                c.Last_Name,
                c.primary_address,
                SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid,
                SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
            FROM 
                ft_customers c
            JOIN 
                ft_subscriber_transactions t ON c.customer_number = t.customer_number
            WHERE
                c.First_Name = '{first_name_filter}' AND c.Last_Name = '{last_name_filter}'
            GROUP BY 
                c.customer_number, c.First_Name, c.Last_Name, c.primary_address
            """

            filtered_df = execute_sql(name_query)

        elif first_name_filter:

            name_query = f"""
            SELECT 
                DISTINCT c.First_Name,
                c.Last_Name,
                c.primary_address,
                SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid,
                SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
            FROM 
                ft_customers c
            JOIN 
                ft_subscriber_transactions t ON c.customer_number = t.customer_number
            WHERE
                c.First_Name = '{first_name_filter}'
            GROUP BY 
                c.customer_number, c.First_Name, c.Last_Name, c.primary_address
            """

            filtered_df = execute_sql_paginated(name_query, target_rows=5000, row_limit=1000)

        elif last_name_filter:

            name_query = f"""
            SELECT 
                DISTINCT c.First_Name,
                c.Last_Name,
                c.primary_address,
                SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid,
                SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
            FROM 
                ft_customers c
            JOIN 
                ft_subscriber_transactions t ON c.customer_number = t.customer_number
            WHERE
                c.Last_Name = '{last_name_filter}'
            GROUP BY 
                c.customer_number, c.First_Name, c.Last_Name, c.primary_address
            """

            filtered_df = execute_sql(name_query)
        #if last_name_filter:
        #   filtered_df = filtered_df[filtered_df["Last Name"].str.contains(last_name_filter, case=False, na=False)]
        
        # Display the distinct filtered dataframe if results are found
        if filtered_df.empty:
            st.write("No results found for the given search criteria.")
        else:
            filtered_df.index = filtered_df.index + 1
            st.subheader("Filtered Customer Data Based on Your Search")
            st.dataframe(filtered_df, use_container_width=True)

    st.subheader("Search By Address")
    adress_filter = st.text_input("Filter by Address", "")

    if adress_filter:
        # Apply filters to the entire database (FT_Table)
        #filtered_df_2 = FT_Table_OG
        
        if adress_filter:
            #filtered_df_2 = filtered_df_2[filtered_df_2["Primary Address"].str.contains(adress_filter, case=False, na=False)]

            address_query = f"""
            SELECT 
                DISTINCT c.First_Name,
                c.Last_Name,
                c.primary_address,
                SUM(CAST(t.gross_value AS NUMERIC)) AS amount_paid,
                SUM(CAST(t.gross_liability AS NUMERIC)) AS gross_liability
            FROM 
                ft_customers c
            JOIN 
                ft_subscriber_transactions t ON c.customer_number = t.customer_number
            WHERE
                c.primary_address = '{adress_filter}'
            GROUP BY 
                c.customer_number, c.First_Name, c.Last_Name, c.primary_address
            """

            filtered_df_2 = execute_sql(address_query)
        # Display the distinct filtered dataframe if results are found
        if filtered_df_2 is None:
            st.write("No results found for the given search criteria.")
        else:
            filtered_df_2.index = filtered_df_2.index + 1
            st.subheader("Filtered Customer Data Based on Your Search")
            st.dataframe(filtered_df_2, use_container_width=True)


    logout_button = st.button("Logout")
    if logout_button:
        # Clear authentication and delete the cookie
        st.session_state.authenticated = False
        cookies["authenticated"] = "false"  # Change the cookie
        cookies.save()  # Save the cookie changes
        st.success("You have logged out.")
        st.rerun()  # Refresh the page to apply the logout


            
    # Display the top N table if no search is applied, or show the full database
    #if not filtered_df:
    
    # Display the filtered table
    #st.dataframe(FT_Table, use_container_width=True)
# Add a Logout button at the bottom of the page
