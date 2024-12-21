# email-order-manager
"Automated workflow for email classification, order processing, and customer inquiry handling using OpenAI API."

This project automates email classification, order processing, and customer inquiry handling using the OpenAI API. It is designed to improve email management efficiency and streamline business workflows.

## Features
- **Email Classification**: Categorizes incoming emails as orders, inquiries, or general communication.
- **Order Processing**: Extracts order details and organizes them for seamless handling.
- **Customer Inquiry Management**: Identifies and prioritizes customer inquiries.
- **Integration with OpenAI API**: Leverages advanced AI capabilities for natural language processing.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/your-username/email-order-manager.git
   cd email-order-manager
   
2. Install Dependencies
Install all the required dependencies by running:
 ```
pip install -r requirements.txt
```
3. Set Up OpenAI API Key
Go to the OpenAI API platform and get your API key.
Create a .env file in the project directory and add the following line
 ```
OPENAI_API_KEY=your-api-key-here
```

4. Configure Email Settings
Edit the config.py file in the project directory.
Add your email provider's necessary SMTP settings (email address, password, and SMTP server).
5. Run the Application
Once the setup is complete, run the application by executing:
``` 
python app.py
```
6. Set Up Scheduled Email Checks (Optional)
If you want the application to run periodically, set up a cron job (Linux/macOS) or use Task Scheduler (Windows).

8. Customizing Email Classification and Order Processing (Optional)
To customize email classification, modify the classify_email function in email_classifier.py.
To adjust how orders are processed, edit the order_processing.py file accordingly.

10. Contribute or Report Issues
You can fork the repository, contribute to the project, or report any issues by opening a new issue on the GitHub repository.


