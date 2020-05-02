from django.test import TestCase
from .models import Book, Post, Comment, PostReaction, CommentReaction
from django.contrib.auth import get_user_model
from api.schema import schema
from api.testcase import MyTestCase
from django.core.exceptions import ValidationError

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

class CommentTestCase(TestCase):

    def setUp(self):
        self.userA = User.objects.create_user(username='userA')
        self.userB = User.objects.create_user(username='userB')

        self.post = Post(text='Lorem Ipsum', user=self.userA)
        self.post.save()

        self.comment = Comment(user=self.userB, text='Dolores', post=self.post)
        self.comment.save()

    def test_create(self):
        post_reaction = PostReaction(reaction='LI', user=self.userB, post=self.post)
        post_reaction.save()
       
        comment_reaction = CommentReaction(reaction='LI', user=self.userA, comment=self.comment)
        comment_reaction.save()
        
        assert len(self.post.reactions.all()) == 1
        assert len(self.comment.reactions.all()) == 1

    def test_undefined_reaction(self):
        undefined_reaction = PostReaction.objects.create(reaction='UN', user=self.userB, post=self.post)

        self.assertRaises(ValidationError, undefined_reaction.full_clean)

class PostGraphqlTestCase(MyTestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test')
        self.user2 = User.objects.create_user(username='test2')
        self.user3 = User.objects.create_user(username='test3')
        self.client.authenticate(self.user)
        self.user.following.add(self.user3)
        self.create_posts(self.user)
        self.create_posts(self.user2)
        self.create_posts(self.user3)

    def create_posts(self, user):
        posts = []
        privacy = ''
        for l in range(0, 10):
            if l%2 == 0: privacy = 'PUB'; # 5
            elif l%3 == 0: privacy = 'PRI'; # 2
            else: privacy  = 'FOL'; # 3
            posts.append(
                Post(
                    user=user,
                    text='Lorem ipsum dolor sit amet.',
                    privacy=privacy,
                )
            )
        Post.objects.bulk_create(posts)

    def test_list(self):        
        executed = self.client.execute('''
            query {
                posts {
                    edges {
                        node {
                            user {
                                username
                            }
                            privacy
                        }
                    }
                }
            }
        ''')
        assert 'data' in executed
        assert not 'errors' in executed
        assert len(executed['data']['posts']['edges']) == 15 + 2 + 3 + 3

    def test_not_authenticated_list(self):
        self.client.logout()
        executed = self.client.execute('''
            query {
                posts {
                    edges {
                        node {
                            user {
                                username
                            }
                            privacy
                        }
                    }
                }
            }
        ''')
        self.client.authenticate(self.user)
        assert 'data' in executed
        assert not 'errors' in executed
        assert len(executed['data']['posts']['edges']) == 15

    def test_get_one_post_pub(self):
        pub = Post.objects.filter(privacy='PUB').first()
        executed = self.client.execute('''
            query getPost($pk:ID!){
                post(pk:$pk){
                    privacy
                    user {
                        username
                    }
                }
            }
        ''', variables={ 'pk': pub.pk })
        assert executed == {
            'data': {
                'post': {
                    'privacy': 'PUB',
                    'user': {
                        'username': pub.user.username
                    }
                }
            }
        }

    def test_get_one_post_pri(self):
        pri = Post.objects.filter(privacy='PRI').first()
        executed = self.client.execute('''
            query getPost($pk:ID!){
                post(pk:$pk){
                    privacy
                    user {
                        username
                    }
                }
            }
        ''', variables={ 'pk': pri.pk })
        assert executed == {
            'data': {
                'post': {
                    'privacy': 'PRI',
                    'user': {
                        'username': self.user.username
                    }
                }
            }
        }

    def test_get_one_post_fol(self):
        fol = Post.objects.filter(privacy='FOL', user=self.user).first()
        executed = self.client.execute('''
            query getPost($pk:ID!){
                post(pk:$pk){
                    privacy
                    user {
                        username
                    }
                }
            }
        ''', variables={ 'pk': fol.pk })
        assert executed == {
            'data': {
                'post': {
                    'privacy': 'FOL',
                    'user': {
                        'username': self.user.username
                    }
                }
            }
        }

    def test_get_does_not_exist_post(self):
        executed = self.client.execute('''
            query getPost($pk:ID!){
                post(pk:$pk){
                    privacy
                    user {
                        username
                    }
                }
            }
        ''', variables={ 'pk': 99999 })
        assert executed == {
            'errors': [
                {
                    'message': 'Postagem não encontrada',
                    'locations': [
                        {
                            'line': 3, 
                            'column': 17
                        }
                    ],
                    'path': ['post']
                }
            ], 
            'data': {
                'post': None
            }
        }
    
    def test_create(self):
        executed = self.client.execute('''
            mutation createPost(
                $text: String!,
                $privacy: String!
            ){
                createPost(input: {
                    text: $text
                    privacy: $privacy
                }){
                    post{
                        user {
                            username
                        }
                        privacy
                    }
                }
            }
        ''', variables={
            'text': 'Lorem Ipsum',
            'privacy': 'PUB'
        })
        assert executed == {
            'data': {
                'createPost': {
                    'post': {
                        'user': {
                            'username': self.user.username
                        },
                        'privacy': 'PUB',
                    }
                }
            }
        }

    def test_update(self):
        post = Post.objects.filter(privacy='PUB', user=self.user).first()
        executed = self.client.execute('''
            mutation updatePost(
                $text: String,
                $privacy: String,
                $post: ID!
            ){
                updatePost(input: {
                    text: $text
                    privacy: $privacy
                    post: $post
                }){
                    post{
                        user {
                            username
                        }
                        privacy
                        text
                    }
                }
            }
        ''', variables={
            'text': 'Lorem Ipsum',
            'privacy': 'PRI',
            'post': post.pk
        })
        assert executed == {
            'data': {
                'updatePost': {
                    'post': {
                        'user': {
                            'username': self.user.username
                        },
                        'privacy': 'PRI',
                        'text': 'Lorem Ipsum'
                    }
                }
            }
        }

    def test_other_user_post_update(self):
        post = Post.objects.filter(privacy='PUB', user=self.user2).first()
        executed = self.client.execute('''
            mutation updatePost(
                $text: String,
                $privacy: String,
                $post: ID!
            ){
                updatePost(input: {
                    text: $text
                    privacy: $privacy
                    post: $post
                }){
                    post{
                        user {
                            username
                        }
                        privacy
                        text
                    }
                }
            }
        ''', variables={
            'text': 'Lorem Ipsum',
            'privacy': 'PRI',
            'post': post.pk
        })

        assert executed['errors'][0]['message'] == 'Postagem não encontrada'
        assert len(executed['errors']) == 1
        assert executed['data']['updatePost'] == None

    def test_deletion_post(self):
        post = Post.objects.filter(privacy='PUB', user=self.user).first()
        executed = self.client.execute('''
            mutation deletePost(
                $post: ID!
            ){
                deletePost(post: $post){
                    deleted
                }
            }
        ''', variables={ 'post': post.pk })
        assert executed == {
            'data': {
                'deletePost': {
                    'deleted': True
                }
            }
        }

    def test_deletion_other_user_post(self):
        post = Post.objects.filter(privacy='PRI', user=self.user2).first()
        executed = self.client.execute('''
            mutation deletePost(
                $post: ID!
            ){
                deletePost(post: $post){
                    deleted
                }
            }
        ''', variables={ 'post': post.pk })

        assert len(executed['errors']) == 1
        assert executed['errors'][0]['message'] == 'Postagem não encontrada'