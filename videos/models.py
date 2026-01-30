from django.db import models

class Video(models.Model):
    youtube_id = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=300)
    descripcion = models.TextField()
    url_thumbnail = models.URLField()
    canal_nombre = models.CharField(max_length=200)
    vistas = models.BigIntegerField(default=0)
    fecha_publicacion = models.DateTimeField()

    def get_embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}"

    def __str__(self):
        return self.titulo