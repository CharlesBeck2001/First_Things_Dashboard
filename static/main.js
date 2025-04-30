// static/js/main.js

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Add loading indicator function
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '<div class="loading">Loading...</div>';
}

// Function to search customers
async function searchCustomers() {
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const resultsDiv = document.getElementById('searchResults');
    
    showLoading('searchResults');
    
    try {
        const response = await fetch(`/api/customers/search?first_name=${encodeURIComponent(firstName)}&last_name=${encodeURIComponent(lastName)}`);
        if (!response.ok) throw new Error('Search failed');
        
        const data = await response.json();
        resultsDiv.innerHTML = '';
        
        if (data.length === 0) {
            resultsDiv.innerHTML = '<p>No results found</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Address</th>
                    <th>Amount Paid</th>
                    <th>Gross Liability</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(customer => `
                    <tr>
                        <td>${customer.First_Name}</td>
                        <td>${customer.Last_Name}</td>
                        <td>${customer.primary_address}</td>
                        <td>${formatCurrency(customer.amount_paid)}</td>
                        <td>${formatCurrency(customer.gross_liability)}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        resultsDiv.appendChild(table);
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-message">Error: ${error.message}</p>`;
        console.error('Error searching customers:', error);
    }
}

// Function to get transactions
async function getTransactions() {
    const customerNumber = document.getElementById('customerNumber').value;
    
    if (!customerNumber) {
        alert('Please enter a customer number');
        return;
    }
    
    try {
        const response = await fetch(`/api/transactions/${customerNumber}`);
        const data = await response.json();
        
        const resultsDiv = document.getElementById('transactionResults');
        resultsDiv.innerHTML = '';
        
        if (data.length === 0) {
            resultsDiv.innerHTML = '<p>No transactions found</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${data.map(transaction => `
                    <tr>
                        <td>${transaction.transaction_date}</td>
                        <td>${formatCurrency(transaction.amount_paid)}</td>
                        <td>${transaction.status || 'N/A'}</td>
                    </tr>
                `).join('')}
            </tbody>
        `;
        
        resultsDiv.appendChild(table);
    } catch (error) {
        console.error('Error getting transactions:', error);
    }
}

// Add event listeners for enter key in search fields
document.getElementById('firstName').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchCustomers();
});

document.getElementById('lastName').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') searchCustomers();
});

document.getElementById('customerNumber').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') getTransactions();
});
