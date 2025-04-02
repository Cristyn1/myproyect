#from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Create your tests here.

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")  # Mode headless per GitHub Actions
        cls.selenium = webdriver.Chrome(options=opts)
        cls.selenium.implicitly_wait(5)

        # Crear superusuari per administrar el sistema
        superuser = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        superuser.is_superuser = True
        superuser.is_staff = True
        superuser.save()

        # Crear un usuari STAFF sense permisos de creació ni eliminació
        staff_user = User.objects.create_user("staffuser", "staff@isardvdi.com", "staffpassword")
        staff_user.is_staff = True  # És staff però no superusuari
        # Afegir només permisos de visualització d'usuaris
        user_content_type = ContentType.objects.get(app_label='auth', model='user')
        view_users_permission = Permission.objects.get(content_type=user_content_type, codename='view_user')

        staff_user.user_permissions.add(view_users_permission)
        staff_user.save()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_staff_user_can_view_but_not_create_or_delete_users(self):
        """ Comprovar que l'usuari STAFF pot veure usuaris però no crear-ne ni eliminar-los """

        self.selenium.get(f"{self.live_server_url}/admin/")
        # Login amb l'usuari STAFF
        username_input = self.selenium.find_element(By.NAME, "username")
        password_input = self.selenium.find_element(By.NAME, "password")
        username_input.send_keys("staffuser")
        password_input.send_keys("staffpassword")
        password_input.send_keys(Keys.RETURN)

        # Comprovar que pot veure la secció d'usuaris
        self.selenium.find_element(By.LINK_TEXT, "Users")  # Ha de trobar aquest enllaç

        # Comprovar que no pot veure botons de "Add user" ni "Delete"
        try:
            self.selenium.find_element(By.LINK_TEXT, "Add user")  # No hauria d'existir
            assert False, "L'usuari STAFF pot afegir usuaris, i no hauria de poder!"
        except:
            pass  # Si no el troba, és correcte

        try:
            self.selenium.find_element(By.LINK_TEXT, "Delete")  # No hauria de veure aquest enllaç
            assert False, "L'usuari STAFF pot esborrar usuaris, i no hauria de poder!"
        except:
            pass  # Si no el troba, és correcte
