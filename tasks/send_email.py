import requests


SENDGRID_API_KEY = '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'


def send_email():
    data = {
    "personalizations": [
        {
        "to": [
            {
            "email": "test@example.com"
            }
        ],
        "subject": "Sending with SendGrid is Fun"
        }
    ],
    "from": {
        "email": "test@example.com"
    },
    "content": [
        {
        "type": "text/plain",
        "value": "and easy to do anywhere, even with Python"
        }
    ]
    }
    res = requests.post(
        json=data, 
        url='https://api.sendgrid.com/v3/mail/send', 
        headers={'Authorization': f'Bearer {SENDGRID_API_KEY}'}
    )
    print(res.status_code, res.json())

if __name__ == '__main__':
    send_email()
    