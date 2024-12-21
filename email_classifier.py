import openai
from config import OPENAI_API_KEY

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

def classify_email(email_subject, email_body):
    """
    Classifies the email into categories such as 'Order', 'Inquiry', or 'General'.
    """
    prompt = f"Classify the following email as either 'Order', 'Inquiry', or 'General'.\nSubject: {email_subject}\nBody: {email_body}\n\nCategory:"
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=10,
        temperature=0.3
    )
    
    category = response.choices[0].text.strip()
    return category
