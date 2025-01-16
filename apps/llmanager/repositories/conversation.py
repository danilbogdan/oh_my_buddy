from apps.llmanager.models import Conversation


class ConversationRepository:
    """Basic operations with django orm for Conversation model"""

    @classmethod
    def create(cls, user, title=None, metadata=None):
        return Conversation.objects.create(user_id=user, title=title, metadata=metadata)

    @classmethod
    def update_title(cls, id, title):
        return Conversation.objects.filter(id=id).update(title=title)

    @classmethod
    def get(cls, id):
        return Conversation.objects.get(id=id)

    @classmethod
    def get_user_conversations(cls, user_id):
        return Conversation.objects.filter(user=user_id)

    @classmethod
    def filter(cls, **kwargs):
        return Conversation.objects.filter(**kwargs)

    @classmethod
    def update(cls, id, **kwargs):
        return Conversation.objects.filter(id=id).update(**kwargs)

    @classmethod
    def delete(cls, id):
        return Conversation.objects.get(id=id).delete()
