from django.test import TestCase
from .models import Book, Post
from django.contrib.auth import get_user_model
from api.schema import schema
from api.testcase import MyTestCase

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

class PostTestCase(TestCase):

    def test_create(self):
        user = User.objects.create_user(username='test')
        user.save()
        post = Post(
            user=user,
            text='Lorem ipsum dolor sit amet, consectetur adipiscing elit. In sed porta odio, vitae pharetra urna. Integer libero nulla, pretium sed mi sit amet, molestie hendrerit sem. Donec nec nibh porta ex elementum elementum ut eget erat. Phasellus ipsum purus, consectetur sit amet pretium vitae, tempor sit amet lorem. In interdum venenatis eros ac ultrices. Phasellus interdum libero risus, non maximus ipsum venenatis ut. Fusce eget metus ac metus commodo mollis. Pellentesque nec lacus accumsan, blandit turpis eget, commodo turpis. Mauris in libero tempor, ultricies odio eu, posuere nulla. Curabitur interdum a lectus et pretium. Cras hendrerit diam felis, sed gravida justo elementum in. Nunc consequat quam ac sem tristique, eu tempor leo imperdiet. Suspendisse potenti. Nulla facilisi. Vivamus at est felis.'            
        )
        post.save()
        assert len(list(user.posts.all())) > 0

class PostGraphqlTestCase(MyTestCase):

    def setUp(self):
        user = User.objects.create_user(username='test')
