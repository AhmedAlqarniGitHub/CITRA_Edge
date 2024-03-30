from django import forms
from .models import Camera
from .models import Server

class CameraForm(forms.ModelForm):
    class Meta:
        model = Camera
        fields = ['rtsp_url', 'device_id', 'event_id']


class ServerForm(forms.ModelForm):
    class Meta:
        model = Server
        fields = ['server_url', 'ip_address', 'location', 'port']