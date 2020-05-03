from . import Post, Comment

class Query(Post.Query):
    pass

class Mutation(
    Post.Mutation,
    Comment.Mutation,
):
    pass