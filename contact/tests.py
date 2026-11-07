import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from contact.models import Category, Contact


TEST_MEDIA_DIRECTORY = tempfile.TemporaryDirectory(dir=settings.BASE_DIR)
TEST_MEDIA_ROOT = Path(TEST_MEDIA_DIRECTORY.name)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ContactPrivacyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(
            username='owner',
            password='strong-test-password',
            first_name='Ana',
            last_name='Silva',
            email='ana@example.com',
        )
        cls.other_user = User.objects.create_user(
            username='other',
            password='strong-test-password',
        )
        cls.owner_category = Category.objects.create(
            name='Trabalho',
            owner=cls.owner,
        )
        cls.other_category = Category.objects.create(
            name='Privada',
            owner=cls.other_user,
        )
        cls.owner_contact = Contact.objects.create(
            first_name='Contato do proprietário',
            phone='111111111',
            owner=cls.owner,
        )
        cls.other_contact = Contact.objects.create(
            first_name='Contato privado',
            phone='222222222',
            owner=cls.other_user,
            picture=SimpleUploadedFile(
                'private.gif',
                (
                    b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00'
                    b'\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00'
                    b'\x02\x02D\x01\x00;'
                ),
                content_type='image/gif',
            ),
        )

    def test_anonymous_user_is_redirected_to_login(self):
        protected_urls = (
            reverse('contact:index'),
            reverse('contact:search') + '?q=Contato',
            reverse('contact:contact', args=(self.owner_contact.pk,)),
            reverse('contact:update', args=(self.owner_contact.pk,)),
            reverse('contact:delete', args=(self.owner_contact.pk,)),
            reverse('contact:contact_picture', args=(self.other_contact.pk,)),
        )

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse('contact:login'), response.url)

    def test_health_check_is_public(self):
        response = self.client.get(reverse('health'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})

    def test_index_only_lists_current_users_contacts(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('contact:index'))

        self.assertContains(response, self.owner_contact.first_name)
        self.assertNotContains(response, self.other_contact.first_name)

    def test_search_does_not_find_another_users_contact(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('contact:search'),
            {'q': self.other_contact.first_name},
        )

        self.assertEqual(response.context['page_obj'].paginator.count, 0)

    def test_contact_detail_from_another_user_returns_404(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('contact:contact', args=(self.other_contact.pk,))
        )

        self.assertEqual(response.status_code, 404)

    def test_contact_update_from_another_user_returns_404(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:update', args=(self.other_contact.pk,)),
            {
                'first_name': 'Alterado',
                'last_name': '',
                'phone': '999999999',
                'email': '',
                'description': '',
                'category': '',
            },
        )

        self.assertEqual(response.status_code, 404)
        self.other_contact.refresh_from_db()
        self.assertEqual(self.other_contact.first_name, 'Contato privado')

    def test_contact_delete_from_another_user_returns_404(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:delete', args=(self.other_contact.pk,)),
            {'confirmation': 'yes'},
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Contact.objects.filter(pk=self.other_contact.pk).exists())

    def test_contact_picture_from_another_user_returns_404(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('contact:contact_picture', args=(self.other_contact.pk,))
        )

        self.assertEqual(response.status_code, 404)

    def test_contact_picture_is_available_to_its_owner(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('contact:contact_picture', args=(self.other_contact.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/gif')
        response.close()

    def test_profile_form_is_filled_with_current_user_data(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('contact:user_update'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].instance, self.owner)
        self.assertContains(response, 'value="Ana"')
        self.assertContains(response, 'value="ana@example.com"')

    def test_password_update_keeps_user_logged_in(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:user_update'),
            {
                'first_name': 'Ana',
                'last_name': 'Silva',
                'email': 'ana@example.com',
                'username': 'owner',
                'password1': 'new-strong-test-password',
                'password2': 'new-strong-test-password',
            },
        )

        self.assertRedirects(response, reverse('contact:user_update'))
        self.owner.refresh_from_db()
        self.assertTrue(self.owner.check_password('new-strong-test-password'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_logout_rejects_get_and_accepts_post(self):
        self.client.force_login(self.owner)

        get_response = self.client.get(reverse('contact:logout'))

        self.assertEqual(get_response.status_code, 405)
        self.assertIn('_auth_user_id', self.client.session)

        post_response = self.client.post(reverse('contact:logout'))

        self.assertRedirects(post_response, reverse('contact:login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_delete_get_only_displays_confirmation(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('contact:delete', args=(self.owner_contact.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/delete_confirmation.html')
        self.assertTrue(Contact.objects.filter(pk=self.owner_contact.pk).exists())

    def test_delete_requires_explicit_confirmation(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:delete', args=(self.owner_contact.pk,))
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(pk=self.owner_contact.pk).exists())

    def test_owner_can_delete_contact_with_confirmation(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:delete', args=(self.owner_contact.pk,)),
            {'confirmation': 'yes'},
        )

        self.assertRedirects(response, reverse('contact:index'))
        self.assertFalse(Contact.objects.filter(pk=self.owner_contact.pk).exists())

    def test_contact_and_category_string_representations(self):
        self.assertEqual(str(self.owner_category), 'Trabalho')
        self.assertEqual(str(self.owner_contact), 'Contato do proprietário ')

    def test_contact_form_only_lists_current_users_categories(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('contact:create'))
        categories = response.context['form'].fields['category'].queryset

        self.assertIn(self.owner_category, categories)
        self.assertNotIn(self.other_category, categories)

    def test_create_rejects_another_users_category(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:create'),
            {
                'first_name': 'Contato',
                'last_name': 'Inválido',
                'phone': '555555555',
                'email': 'categoria-invalida@example.com',
                'description': '',
                'category': self.other_category.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors['category'])
        self.assertFalse(
            Contact.objects.filter(email='categoria-invalida@example.com').exists()
        )

    def test_deleting_user_cascades_to_private_contacts_and_categories(self):
        owner_id = self.owner.pk

        self.owner.delete()

        self.assertFalse(Contact.objects.filter(owner_id=owner_id).exists())
        self.assertFalse(Category.objects.filter(owner_id=owner_id).exists())

    def test_empty_search_redirects_to_index(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse('contact:search'), {'q': '   '})

        self.assertRedirects(response, reverse('contact:index'))

    def test_contact_without_picture_redirects_to_detail(self):
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('contact:contact_picture', args=(self.owner_contact.pk,))
        )

        self.assertRedirects(
            response,
            reverse('contact:contact', args=(self.owner_contact.pk,)),
        )

    def test_owner_can_create_contact(self):
        self.client.force_login(self.owner)

        get_response = self.client.get(reverse('contact:create'))
        self.assertEqual(get_response.status_code, 200)

        response = self.client.post(
            reverse('contact:create'),
            {
                'first_name': 'Novo',
                'last_name': 'Contato',
                'phone': '333333333',
                'email': 'novo@example.com',
                'description': '',
                'category': '',
            },
        )

        created = Contact.objects.get(email='novo@example.com')
        self.assertEqual(created.owner, self.owner)
        self.assertRedirects(
            response,
            reverse('contact:update', args=(created.pk,)),
        )

    def test_create_rejects_equal_first_and_last_names(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse('contact:create'),
            {
                'first_name': 'Mesmo',
                'last_name': 'Mesmo',
                'phone': '333333333',
                'email': '',
                'description': '',
                'category': '',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context['form'],
            'first_name',
            'Primeiro nome não pode ser igual ao segundo',
        )
        self.assertFalse(Contact.objects.filter(first_name='Mesmo').exists())

    def test_owner_can_update_contact(self):
        self.client.force_login(self.owner)
        url = reverse('contact:update', args=(self.owner_contact.pk,))

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)

        response = self.client.post(
            url,
            {
                'first_name': 'Nome atualizado',
                'last_name': 'Sobrenome',
                'phone': '444444444',
                'email': 'atualizado@example.com',
                'description': 'Atualizado pelos testes',
                'category': '',
            },
        )

        self.assertRedirects(response, url)
        self.owner_contact.refresh_from_db()
        self.assertEqual(self.owner_contact.first_name, 'Nome atualizado')
        self.assertEqual(self.owner_contact.phone, '444444444')

    def test_registration_creates_user_and_rejects_duplicate_email(self):
        registration_data = {
            'first_name': 'Nova',
            'last_name': 'Pessoa',
            'email': 'nova@example.com',
            'username': 'nova-pessoa',
            'password1': 'Strong-registration-password-9382',
            'password2': 'Strong-registration-password-9382',
        }

        response = self.client.post(reverse('contact:register'), registration_data)

        self.assertRedirects(response, reverse('contact:login'))
        self.assertTrue(User.objects.filter(username='nova-pessoa').exists())

        registration_data['username'] = 'outra-pessoa'
        duplicate_response = self.client.post(
            reverse('contact:register'),
            registration_data,
        )

        self.assertEqual(duplicate_response.status_code, 200)
        self.assertFormError(
            duplicate_response.context['form'],
            'email',
            'Já existe este e-mail',
        )

    def test_login_rejects_invalid_credentials_and_accepts_valid_ones(self):
        invalid_response = self.client.post(
            reverse('contact:login'),
            {'username': self.owner.username, 'password': 'senha-incorreta'},
        )
        self.assertEqual(invalid_response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        response = self.client.post(
            reverse('contact:login'),
            {
                'username': self.owner.username,
                'password': 'strong-test-password',
            },
        )

        self.assertRedirects(response, reverse('contact:index'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_profile_rejects_mismatched_and_weak_passwords(self):
        self.client.force_login(self.owner)
        base_data = {
            'first_name': 'Ana',
            'last_name': 'Silva',
            'email': 'ana@example.com',
            'username': 'owner',
        }

        mismatched_response = self.client.post(
            reverse('contact:user_update'),
            {
                **base_data,
                'password1': 'new-strong-test-password',
                'password2': 'different-password',
            },
        )
        self.assertFormError(
            mismatched_response.context['form'],
            'password2',
            'Senhas não batem',
        )

        weak_response = self.client.post(
            reverse('contact:user_update'),
            {**base_data, 'password1': '123', 'password2': '123'},
        )
        self.assertEqual(weak_response.status_code, 200)
        self.assertTrue(weak_response.context['form'].errors['password1'])
