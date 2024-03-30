from django.db import models

class Camera(models.Model):
    rtsp_url = models.TextField()
    device_id = models.TextField()
    event_id = models.TextField()
    
    class Meta:
        app_label = 'event_manager'


class Server(models.Model):
    server_url = models.TextField()
    ip_address = models.GenericIPAddressField()  # For storing IP Address
    location = models.CharField(max_length=100)  # Example field for location
    port = models.IntegerField()  # For storing port number

    class Meta:
        app_label = 'event_manager'
