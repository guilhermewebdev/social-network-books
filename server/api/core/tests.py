from django.test import TestCase
from .models import Book
from django.contrib.auth import get_user_model

User = get_user_model()

class BooksTestCase(TestCase):
    
    def test_create(self):
        user = User.objects.create_user(username='test')
        user.save()
        book = Book.objects.create(
            user=user,
            book='zyTCAlFPjgYC',
            bookshelf='TRE',
        )        
        book.save()
        assert len(list(user.books.all().iterator())) > 0
        assert book.bookshelf == 'TRE'
        assert book.favorite == False

    def test_delete(self):
        user = User.objects.create_user(username='test')
        user.save()
        book = Book.objects.create(
            user=user,
            book='zyTCAlFPjgYC',
            bookshelf='TRE',
        )        
        book.save()
        book.delete()
        assert len(list(user.books.all().iterator())) == 0