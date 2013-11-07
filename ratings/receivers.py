from django.contrib.contenttypes.models import ContentType


def save_receiver(sender, **kwargs):
    ct = ContentType.objects.get_for_model(sender)
    second = sender.username if ct.model == 'user' else '_.-=.'
    print("SAVING class: {0}, {1}".format(ct, second))


def delete_receiver(sender, **kwargs):
    try:
        second = sender.username
    except AttributeError:
        second = 'pies'
    print("DELETING class: {0}, instance {1}".format(sender, second))
