from data_satrapy.models import Field, Post


def ordered_field_list():
    return Field.query.order_by(Field.subject).all()


def post_field_num(field):
    """

    :param field: str. field of post
    :return: int. number of posts on the field.
    """
    subject = Field.query.filter_by(subject=field).first_or_404()
    posts = Post.query.filter_by(field=subject).paginate()
    return posts.total
