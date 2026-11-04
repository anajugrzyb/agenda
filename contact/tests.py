import tempfile
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from contact.models import Contact


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
