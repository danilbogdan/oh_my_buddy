# from django.utils.translation import gettext_lazy as _
# from django.db import models
# from solo.models import SingletonModel


# class LLModel(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()

#     class Meta:
#         verbose_name = _("LLModel")
#         verbose_name_plural = _("LLModels")

#     def __str__(self):
#         return self.name


# class Assistant(models.Model):
#     instructions = models.TextField()
#     name = models.CharField(max_length=255)
#     tools = models.JSONField()
#     model = models.ForeignKey(LLModel, on_delete=models.CASCADE)

#     class Meta:
#         verbose_name = _("Assistant")
#         verbose_name_plural = _("Assistants")

#     def __str__(self):
#         return self.name


# class Thread(models.Model):
#     assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
#     metadata = models.JSONField()

#     class Meta:
#         verbose_name = _("Thread")
#         verbose_name_plural = _("Threads")

#     def __str__(self):
#         return f"Thread {self.id} for Assistant {self.assistant.name}"


# class Message(models.Model):
#     thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
#     role = models.CharField(max_length=50)
#     content = models.TextField()
#     metadata = models.JSONField()

#     class Meta:
#         verbose_name = _("Message")
#         verbose_name_plural = _("Messages")

#     def __str__(self):
#         return f"Message {self.id} in Thread {self.thread.id}"
