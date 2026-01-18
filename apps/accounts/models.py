from django.db import models


class Role(models.Model):
    rol_id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column="fecha_creacion", blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'roles'
        managed = False
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self) -> str:
        return self.nombre


class LegacyUser(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    rol = models.ForeignKey(
        Role,
        on_delete=models.DO_NOTHING,
        db_column="rol_id",
        related_name="usuarios",
        null=True,
    )
    username = models.CharField(max_length=80, unique=True)
    password = models.CharField(max_length=255)
    nombre = models.CharField(max_length=100)
    ap_pat = models.CharField(max_length=100)
    ap_mat = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    fecha_creacion = models.DateTimeField(db_column="fecha_creacion", blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'usuarios'
        managed = False
        verbose_name = 'Usuario (legacy)'
        verbose_name_plural = 'Usuarios (legacy)'

    def __str__(self) -> str:
        return f"{self.nombre} {self.ap_pat}".strip()

    @property
    def full_name(self) -> str:
        parts = [self.nombre, self.ap_pat, self.ap_mat]
        return " ".join(filter(None, parts))
