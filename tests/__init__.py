from django.test import TestCase, Client
from authentic.conf import settings
from django.core import mail
from bs4 import BeautifulSoup


class AuthenticTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.context = {
            "username": "testcase",
            "email": "testcase@tescase.com",
            "password": "testando@123",
        }

    def test_create_account_whitout_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "testcase")

    def test_create_account_with_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = True
        self.context["re_password"] = "testando@123"
        response = self.client.post("/contas/criar/", data=self.context)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "testcase")

    def test_activation_account_email_template_without_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)

        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "testcase")

        context = {"uid": uid, "token": token}
        response = self.client.post("/contas/ativacao/", data=context)
        self.assertEqual(response.status_code, 204)

    def test_activation_account_email_template_whith_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = True
        self.context["re_password"] = "testando@123"
        response = self.client.post("/contas/criar/", data=self.context)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "testcase")

        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        context = {"uid": uid, "token": token}

        response = self.client.post("/contas/ativacao/", data=context)
        self.assertEqual(response.status_code, 204)

    def test_activation_account_email_resend(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)

        self.assertEqual(response.status_code, 201)

        email = {"email": self.context["email"]}

        response = self.client.post("/contas/ativacao/reenviar/", data=email)
        self.assertEqual(response.status_code, 204)

        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        context = {"uid": uid, "token": token}

        response = self.client.post("/contas/ativacao/", data=context)
        self.assertEqual(response.status_code, 204)

    def test_recover_password_whitout_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)

        email = {"email": self.context.get("email")}
        response = self.client.post("/contas/recuperar/senha/", data=email)
        self.assertEqual(response.status_code, 204)

        settings.CHANGE_PASSWORD_RETYPE = False
        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        context = {"uid": uid, "token": token, "new_password": "change_password123"}
        response = self.client.post("/contas/recuperar/senha/trocar/", data=context)
        self.assertEqual(response.status_code, 204)

    def test_recover_password_whit_retype(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)

        email = {"email": self.context.get("email")}
        response = self.client.post("/contas/recuperar/senha/", data=email)
        self.assertEqual(response.status_code, 204)

        settings.CHANGE_PASSWORD_RETYPE = True
        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        context = {
            "uid": uid,
            "token": token,
            "new_password": "change_password123",
            "re_new_password": "change_password123",
        }
        response = self.client.post("/contas/recuperar/senha/trocar/", data=context)
        self.assertEqual(response.status_code, 204)

    def test_authentication_login(self):
        settings.USER_CREATE_PASSWORD_RETYPE = False
        response = self.client.post("/contas/criar/", data=self.context)

        soup = BeautifulSoup(mail.outbox[0].body, "html.parser")
        link = soup.find("a").get("href")
        token, uid = link.split("/")[-1:-3:-1]
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["username"], "testcase")

        context = {"uid": uid, "token": token}
        response = self.client.post("/contas/ativacao/", data=context)
        self.assertEqual(response.status_code, 204)

        user_context = {
            "username": self.context.get("username"),
            "password": self.context.get("password"),
        }

        response = self.client.post("/entrar/", data=user_context)

        self.assertEqual(response.status_code, 200)
