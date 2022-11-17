from django.db import models
from django.contrib.auth.models import User

class Labels(models.Model):
    label_name = models.CharField(max_length=50, default='Normal')
    def __str__(self):
        return self.label_name

class Mail(models.Model):
    subject = models.CharField(max_length=100)
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    sent_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mail_from')
    sent_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mail_to')
    mail_read = models.BooleanField(default=False)
    mail_co2e = models.FloatField(default=4.00)
    labels = models.ForeignKey(Labels, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "%s %s" % (self.sent_from, self.subject)
