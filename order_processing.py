def extract_order_details(email_body):
    """
    Extracts order details like item name, quantity, and shipping address from the email body.
    This is a simple example, you can make this more robust as needed.
    """
    order_details = {}
    
    # Simple example logic to extract order details
    lines = email_body.split("\n")
    for line in lines:
        if "item" in line.lower():
            order_details["item"] = line.split(":")[1].strip()
        elif "quantity" in line.lower():
            order_details["quantity"] = int(line.split(":")[1].strip())
        elif "address" in line.lower():
            order_details["address"] = line.split(":")[1].strip()

    return order_details
