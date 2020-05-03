from . import Post, Comment, PostReactions

class Query(Post.Query):
    pass

class Mutation(
    Post.Mutation,
    Comment.Mutation,
    PostReactions.Mutation,
):
    pass