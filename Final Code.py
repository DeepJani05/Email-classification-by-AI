Configure OpenAI API Key.
# Install the OpenAI Python package.
%pip install openai

# Code example of OpenAI communication

from openai import OpenAI

client = OpenAI(
    # In order to use provided API key, make sure that models you create point to this custom base URL.
    base_url='https://47v4us7kyypinfb5lcligtc3x40ygqbs.lambda-url.us-east-1.on.aws/v1/',
    # The temporary API key giving access to ChatGPT 4o model. Quotas apply: you have 500'000 input and 500'000 output tokens, use them wisely ;)
    api_key='a0BIj000001aF52MAE'
)

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "user", "content": "Hello!"}
  ]
)

print(completion.choices[0].message)


# Code example of reading input data

import pandas as pd
from IPython.display import display

def read_data_frame(document_id, sheet_name):
    export_link = f"https://docs.google.com/spreadsheets/d/{document_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    return  pd.read_csv(export_link)

document_id = '14fKHsblfqZfWj3iAaM2oA51TlYfQlFT4WKo52fVaQ9U'
products_df = read_data_frame(document_id, 'products')
emails_df = read_data_frame(document_id, 'emails')

# Display first 3 rows of each DataFrame
display(products_df.head(3))
display(emails_df.head(3))


Task 1. Classify emails

def classify_email(email_body):
    prompt = f"""
    Classify the following email as either a "product inquiry" or an "order request".
    The classification should accurately reflect the intent of the email.
    Respond with only "product inquiry" or "order request".

    Email:
    {email_body}

    Classification:
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

# Classify emails
email_classification_df = pd.DataFrame({
    'email ID': emails_df['email_id'],
    'category': emails_df['message'].apply(classify_email)
})

# Display the results
print(email_classification_df)

# Save to Google Sheets
def save_to_google_sheets(df, sheet_name):
    # This function is a placeholder. In a real implementation, you would use
    # the Google Sheets API to write the data back to the sheet.
    print(f"Saving data to sheet: {sheet_name}")
    print(df)

email_classification_df.to_csv('email_classifications.csv', index=False)


Task 2. Process order requests
import pandas as pd
import json
import re
from difflib import get_close_matches
from openai import OpenAI

def extract_order_details(email_body):
    prompt = f"""
    Extract the following information from the email:
    - Product ID
    - Quantity

    Email:
    {email_body}

    Examples:
    - "I would like to order 2 x PRD0011" -> {{"Product ID": "PRD0011", "Quantity": 2}}
    - "Please send me one BFT0543" -> {{"Product ID": "BFT0543", "Quantity": 1}}
    - "I want to order all the remaining LTH0976" -> {{"Product ID": "LTH0976", "Quantity": "all"}}
    - "I'd like to order one of your Versatile Scarves" -> {{"Product": "Versatile Scarf", "Quantity": 1}}
    - "Hi, my name is Marco and I need to buy a pair of slide sandals for men, in the Men's Shoes category, for the summer." -> {{"Product": "Slide Sandals", "Quantity": 1}}
    - "Please send me 1 Sleek Wallet. Thanks, Johny" -> {{"Product": "Sleek Wallet", "Quantity": 1}}
    - "Hey there, I would like to buy Chelsea Boots [CBT 89 01] from you guys! You're so awesome I'm so impressed with the quality of Fuzzy Slippers - FZZ1098 I've bought from you before. I hope the quality stays. I would like to order Retro sunglasses from you, but probably next time! Thanks" -> {{"Product": "CBT8901", "Quantity": 1}}

    Format the output as a JSON object with keys "Product ID" and "Quantity".
    If multiple products are ordered, return a list of objects.
    Respond ONLY with the JSON, no other text.
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = completion.choices[0].message.content.strip()
    print(f"GPT-4 Response: {response_text}")

    # Try to extract JSON from the response
    json_match = re.search(r'\{.*\}|\[.*\]', response_text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {json_match.group()}")

    # If JSON extraction fails, try to extract product ID and quantity using regex
    product_id_match = re.search(r'Product ID["\']\s*:\s*["\']?([A-Z0-9]+)["\']?', response_text)
    quantity_match = re.search(r'Quantity["\']\s*:\s*(\d+|all)', response_text)

    if product_id_match and quantity_match:
        return {
            "Product ID": product_id_match.group(1),
            "Quantity": quantity_match.group(1)
        }

    print(f"Failed to extract order details from: {response_text}")
    return None

from difflib import get_close_matches

def find_product(product_id_or_name, products_df):
    if product_id_or_name is None:
        return None

    # Check if it's a product ID
    product = products_df[products_df['product_id'] == product_id_or_name]
    if not product.empty:
        return product.iloc[0]

    # If not found by ID, try to find by name (case-insensitive)
    product = products_df[products_df['name'].str.lower() == product_id_or_name.lower()]
    if not product.empty:
        return product.iloc[0]

    # If still not found, try partial name match
    product = products_df[products_df['name'].str.lower().str.contains(product_id_or_name.lower())]
    if not product.empty:
        return product.iloc[0]

    return None

def process_order(order_details, products_df):
    if order_details is None:
        return []

    if isinstance(order_details, dict):
        order_details = [order_details]

    results = []
    for item in order_details:
        product_id_or_name = item.get('Product ID') or item.get('Product')
        quantity = item.get('Quantity')

        product = find_product(product_id_or_name, products_df)

        if product is None:
            results.append({
                'product_id': product_id_or_name,
                'product_name': 'Product not found',
                'quantity': 0,
                'status': 'product not found'
            })
            continue

        stock = int(product['stock'])

        if quantity == 'all':
            quantity = stock
        else:
            try:
                quantity = int(quantity)
            except ValueError:
                results.append({
                    'product_id': product['product_id'],
                    'product_name': product['name'],
                    'quantity': 0,
                    'status': 'invalid quantity'
                })
                continue

        if stock >= quantity:
            status = 'created'
            products_df.loc[products_df['product_id'] == product['product_id'], 'stock'] -= quantity
        else:
            status = 'out of stock'
            quantity = stock  # Set quantity to available stock

        results.append({
            'product_id': product['product_id'],
            'product_name': product['name'],
            'quantity': quantity,
            'status': status
        })

    return results

def generate_order_response(order_status, products_df):
    order_details = []
    out_of_stock = []
    for item in order_status:
        product = products_df[products_df['product_id'] == item['product_id']]
        if not product.empty:
            product = product.iloc[0]
            if item['status'] == 'created':
                order_details.append(f"{item['quantity']} x {product['name']} (${product['price']} each)")
            else:
                out_of_stock.append(f"{product['name']} (Requested: {item['quantity']}, Available: {product['stock']})")
        else:
            out_of_stock.append(f"Unknown product (ID: {item['product_id']})")

    if out_of_stock:
        prompt = f"""
        Generate a professional and production-ready email response for an order that cannot be fully fulfilled due to insufficient stock or unknown products.

        Order details:
        {', '.join(order_details)}

        Issues:
        {', '.join(out_of_stock)}

        Explain the situation, specify the out-of-stock or unknown items, and suggest alternatives or options (e.g., waiting for restock, similar products).
        """
    else:
        prompt = f"""
        Generate a professional and production-ready email response for a successful order.

        Order details:
        {', '.join(order_details)}

        Include order details and thank the customer for their order.
        """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content

# Process orders
order_status = []
order_responses = []

for _, email in emails_df.iterrows():
    if email_classification_df.loc[email_classification_df['email ID'] == email['email_id'], 'category'].iloc[0] == 'order request':
        print(f"\nProcessing email ID: {email['email_id']}")
        print(f"Email content: {email['message']}")

        order_details = extract_order_details(email['message'])
        print(f"Extracted order details: {order_details}")

        if order_details:
            status = process_order(order_details, products_df)
            print(f"Processed order status: {status}")

            for item in status:
                order_status.append({
                    'email ID': email['email_id'],
                    'product ID': item['product_id'],
                    'product_name': item['product_name'],
                    'quantity': item['quantity'],
                    'status': item['status']
                })
            response = generate_order_response(status, products_df)
            order_responses.append({
                'email ID': email['email_id'],
                'response': response
            })
        else:
            print("No valid order details extracted.")

# Create DataFrames
order_status_df = pd.DataFrame(order_status)
order_response_df = pd.DataFrame(order_responses)

# Display results
print("\nOrder Status:")
display(order_status_df)
order_status_df.to_csv('order_status.csv', index=False)

print("\nOrder Responses:")
display(order_response_df)
order_response_df.to_csv('order_response.csv', index=False)

print(f"\nTotal orders processed: {len(order_status)}")


Task 3. Handle product inquiry

import pandas as pd
import string
from openai import OpenAI
from difflib import get_close_matches

def extract_inquiry_details(email_body):
    prompt = f"""
    Extract key information from the customer's product inquiry:
    - Product category or type
    - Specific features or attributes mentioned
    - Any price considerations
    - Intended use or occasion

    Email:
    {email_body}

    Respond with a concise summary of the extracted information.
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

import re

def search_products(inquiry_details, products_df):
    # Convert inquiry details to lowercase for case-insensitive matching
    inquiry_lower = inquiry_details.lower()

    # Escape special regex characters
    inquiry_escaped = re.escape(inquiry_lower)

    # Filter products based on the inquiry details
    matching_products = products_df[
        products_df['category'].str.capitalize().str.contains(inquiry_escaped, regex=True, na=False) |
        products_df['description'].str.lower().str.contains(inquiry_escaped, regex=True, na=False) |
        products_df['name'].str.capitalize().str.contains(inquiry_escaped, regex=True, na=False)
    ]

    # If no matches found, try splitting the inquiry into words and search for each word
    if matching_products.empty:
        words = re.findall(r'\w+', inquiry_lower)
        for word in words:
            word_escaped = re.escape(word)
            matching_products = products_df[
                products_df['category'].str.capitalize().str.contains(word_escaped, regex=True, na=False) |
                products_df['description'].str.lower().str.contains(word_escaped, regex=True, na=False) |
                products_df['name'].str.capitalize().str.contains(word_escaped, regex=True, na=False)
            ]
            if not matching_products.empty:
                break

    return matching_products.head(5)  # Return top 5 matches

def generate_inquiry_response(inquiry_details, matching_products):
    prompt = f"""
    Generate a helpful response to a customer's product inquiry. Use the following information:

    Customer's inquiry details:
    {inquiry_details}

    Matching products (up to 5):
    {matching_products[['name', 'description', 'price']].to_string(index=False)}

    Craft a response that addresses the customer's specific questions and recommends suitable products.
    Include product names, relevant features, and prices.
    If no exact matches are found, suggest similar alternatives or ask for more information.
    Keep the response concise and friendly.
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

# Process inquiries
inquiry_responses = []

for _, email in emails_df.iterrows():
    if email_classification_df.loc[email_classification_df['email ID'] == email['email_id'], 'category'].iloc[0] == 'product inquiry':
        print(f"\nProcessing email ID: {email['email_id']}")
        print(f"Email content: {email['message']}")

        inquiry_details = extract_inquiry_details(email['message'])
        print(f"Extracted inquiry details: {inquiry_details}")

        matching_products = search_products(inquiry_details, products_df)

        if not matching_products.empty:
            response = generate_inquiry_response(inquiry_details, matching_products)
        else:
            response = "I apologize, but I couldn't find any products that match your specific inquiry. Could you please provide more details or clarify your requirements? We'd be happy to assist you further."

        inquiry_responses.append({
            'email ID': email['email_id'],
            'response': response
        })

# Create DataFrame
inquiry_response_df = pd.DataFrame(inquiry_responses)

# Display results
print("\nInquiry Responses:")
display(inquiry_response_df)

# Save to CSV
inquiry_response_df.to_csv('inquiry_responses.csv', index=False)
