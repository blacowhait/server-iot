from __future__ import print_function
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, Request
from settings import get_settings

templates = Jinja2Templates(directory="./templates")

settings = get_settings()
router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

async def send_verification_email(email : str, token : str):
    subject = "Verified your email"
    sender = {"name":"Sendinblue","email":"contact@sendinblue.com"}
    html_content = f"""<html>
    <body>
    <h1>Verified your email</h1>
    <a href="{settings.DOMAIN}/auth/activation/?token={token}&email={email}">Click Me!</a>
    </body>
    </html>"""
    to = [{"email":email,"name":"Jane Doe"}]
    # replyTo = {"name":"Sendinblue","email":"contact@sendinblue.com"}
    # params = {"parameter":"My param value","subject":"New Subject"}
    # send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=bcc, cc=cc, reply_to=reply_to, headers=headers, html_content=html_content, sender=sender, subject=subject)
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

async def send_forgot_password_email(email: str, new_password: str):
    subject = "Forgot Password"
    sender = {"name":"Sendinblue","email":"contact@sendinblue.com"}
    html_content = f"""<html>
    <body>
    <h1>Use this password for login your account</h1>
    <h2>{new_password}</h2>
    </body>
    </html>"""
    to = [{"email":email,"name":"Jane Doe"}]
    # replyTo = {"name":"Sendinblue","email":"contact@sendinblue.com"}
    # params = {"parameter":"My param value","subject":"New Subject"}
    # send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, bcc=bcc, cc=cc, reply_to=reply_to, headers=headers, html_content=html_content, sender=sender, subject=subject)
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)