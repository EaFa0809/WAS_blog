from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import Post


class BlogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(username="testuser", password="secretpass123")
        cls.other = get_user_model().objects.create_user(username="someoneelse", password="secretpass123")
        cls.post = Post.objects.create(title="A good title", body="Nice body content", author=cls.user)

    def test_post_model(self):
        self.assertEqual(str(self.post), "A good title")
        self.assertEqual(self.post.get_absolute_url(), reverse("post_detail", kwargs={"pk": self.post.pk}))

    def test_list_and_detail(self):
        self.assertContains(self.client.get(reverse("home")), "A good title")
        self.assertContains(self.client.get(self.post.get_absolute_url()), "Nice body content")
        self.assertEqual(self.client.get(reverse("post_detail", kwargs={"pk": 999999})).status_code, 404)

    def test_create_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("post_new"), {"title": "Another post", "body": "New body"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="Another post", author=self.user).exists())

    def test_update_post(self):
        self.client.force_login(self.user)
        self.client.post(reverse("post_edit", kwargs={"pk": self.post.pk}), {"title": "Updated", "body": "Edited"})
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated")

    def test_delete_post(self):
        self.client.force_login(self.user)
        self.client.post(reverse("post_delete", kwargs={"pk": self.post.pk}))
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_edit_requires_owner(self):
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(reverse("post_edit", kwargs={"pk": self.post.pk})).status_code, 404)

    def test_anonymous_redirect(self):
        self.assertEqual(self.client.get(reverse("post_new")).status_code, 302)

    def test_login_signup_and_logout(self):
        self.assertEqual(self.client.get(reverse("login")).status_code, 200)
        self.assertEqual(self.client.get(reverse("signup")).status_code, 200)
        self.assertContains(self.client.get(reverse("home")), "You are not logged in")
        self.client.force_login(self.user)
        self.assertContains(self.client.get(reverse("home")), "Hi testuser!")
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)
