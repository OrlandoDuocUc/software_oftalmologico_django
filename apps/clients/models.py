from django.db import models


class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    ap_pat = models.CharField(max_length=100)
    ap_mat = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(db_column='fecha_creacion', blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'clientes'
        managed = False
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self) -> str:
        return f"{self.nombres} {self.ap_pat}".strip()


class PacienteMedico(models.Model):
    paciente_medico_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        'clients.Cliente',
        on_delete=models.SET_NULL,
        db_column='cliente_id',
        blank=True,
        null=True,
        related_name='pacientes_medicos'
    )
    numero_ficha = models.CharField(max_length=20, unique=True)
    antecedentes_medicos = models.TextField(blank=True, null=True)
    antecedentes_oculares = models.TextField(blank=True, null=True)
    alergias = models.TextField(blank=True, null=True)
    medicamentos_actuales = models.TextField(blank=True, null=True)
    contacto_emergencia = models.CharField(max_length=100, blank=True, null=True)
    telefono_emergencia = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'pacientes_medicos'
        managed = False
        verbose_name = 'Paciente medico'
        verbose_name_plural = 'Pacientes medicos'

    def __str__(self) -> str:
        return self.numero_ficha
