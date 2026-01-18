from django.db import models

from apps.accounts.models import LegacyUser
from apps.clients.models import PacienteMedico


class FichaClinica(models.Model):
    ficha_id = models.AutoField(primary_key=True)
    paciente_medico = models.ForeignKey(
        PacienteMedico,
        on_delete=models.CASCADE,
        db_column="paciente_medico_id",
        related_name="fichas_clinicas",
    )
    usuario = models.ForeignKey(
        LegacyUser,
        on_delete=models.DO_NOTHING,
        db_column="usuario_id",
        related_name="fichas_clinicas",
    )
    numero_consulta = models.CharField(max_length=20, unique=True)
    fecha_consulta = models.DateTimeField()
    motivo_consulta = models.TextField(blank=True, null=True)
    historia_actual = models.TextField(blank=True, null=True)

    av_od_sc = models.CharField(max_length=20, blank=True, null=True)
    av_od_cc = models.CharField(max_length=20, blank=True, null=True)
    av_od_ph = models.CharField(max_length=20, blank=True, null=True)
    av_od_cerca = models.CharField(max_length=20, blank=True, null=True)

    av_oi_sc = models.CharField(max_length=20, blank=True, null=True)
    av_oi_cc = models.CharField(max_length=20, blank=True, null=True)
    av_oi_ph = models.CharField(max_length=20, blank=True, null=True)
    av_oi_cerca = models.CharField(max_length=20, blank=True, null=True)

    esfera_od = models.CharField(max_length=10, blank=True, null=True)
    cilindro_od = models.CharField(max_length=10, blank=True, null=True)
    eje_od = models.CharField(max_length=10, blank=True, null=True)
    adicion_od = models.CharField(max_length=10, blank=True, null=True)

    esfera_oi = models.CharField(max_length=10, blank=True, null=True)
    cilindro_oi = models.CharField(max_length=10, blank=True, null=True)
    eje_oi = models.CharField(max_length=10, blank=True, null=True)
    adicion_oi = models.CharField(max_length=10, blank=True, null=True)

    distancia_pupilar = models.CharField(max_length=10, blank=True, null=True)
    tipo_lente = models.CharField(max_length=50, blank=True, null=True)

    estado = models.CharField(max_length=20, default="en_proceso")
    fecha_creacion = models.DateTimeField(db_column="fecha_creacion", blank=True, null=True)

    class Meta:
        db_table = "fichas_clinicas"
        managed = False
        verbose_name = "Ficha clinica"
        verbose_name_plural = "Fichas clinicas"

    def __str__(self) -> str:
        return f"Ficha {self.numero_consulta}"


class Biomicroscopia(models.Model):
    biomicroscopia_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="biomicroscopias",
    )

    parpados_od = models.TextField(blank=True, null=True)
    conjuntiva_od = models.TextField(blank=True, null=True)
    cornea_od = models.TextField(blank=True, null=True)
    camara_anterior_od = models.TextField(blank=True, null=True)
    iris_od = models.TextField(blank=True, null=True)
    pupila_od_mm = models.CharField(max_length=10, blank=True, null=True)
    pupila_od_reaccion = models.CharField(max_length=20, blank=True, null=True)
    cristalino_od = models.TextField(blank=True, null=True)
    pupila_desc_od = models.TextField(blank=True, null=True)
    pestanas_od = models.TextField(blank=True, null=True)
    conjuntiva_bulbar_od = models.TextField(blank=True, null=True)
    conjuntiva_tarsal_od = models.TextField(blank=True, null=True)
    orbita_od = models.TextField(blank=True, null=True)
    pliegue_semilunar_od = models.TextField(blank=True, null=True)
    caruncula_od = models.TextField(blank=True, null=True)
    conductos_lagrimales_od = models.TextField(blank=True, null=True)
    parpado_superior_od = models.TextField(blank=True, null=True)
    parpado_inferior_od = models.TextField(blank=True, null=True)

    parpados_oi = models.TextField(blank=True, null=True)
    conjuntiva_oi = models.TextField(blank=True, null=True)
    cornea_oi = models.TextField(blank=True, null=True)
    camara_anterior_oi = models.TextField(blank=True, null=True)
    iris_oi = models.TextField(blank=True, null=True)
    pupila_oi_mm = models.CharField(max_length=10, blank=True, null=True)
    pupila_oi_reaccion = models.CharField(max_length=20, blank=True, null=True)
    cristalino_oi = models.TextField(blank=True, null=True)
    pupila_desc_oi = models.TextField(blank=True, null=True)
    pestanas_oi = models.TextField(blank=True, null=True)
    conjuntiva_bulbar_oi = models.TextField(blank=True, null=True)
    conjuntiva_tarsal_oi = models.TextField(blank=True, null=True)
    orbita_oi = models.TextField(blank=True, null=True)
    pliegue_semilunar_oi = models.TextField(blank=True, null=True)
    caruncula_oi = models.TextField(blank=True, null=True)
    conductos_lagrimales_oi = models.TextField(blank=True, null=True)
    parpado_superior_oi = models.TextField(blank=True, null=True)
    parpado_inferior_oi = models.TextField(blank=True, null=True)

    observaciones_generales = models.TextField(blank=True, null=True)
    otros_detalles = models.TextField(blank=True, null=True)
    fecha_examen = models.DateTimeField(db_column="fecha_examen", blank=True, null=True)

    class Meta:
        db_table = "biomicroscopia"
        managed = False
        verbose_name = "Biomicroscopia"
        verbose_name_plural = "Biomicroscopias"

    def __str__(self) -> str:
        return f"Biomicroscopia {self.biomicroscopia_id}"


class FondoOjo(models.Model):
    fondo_ojo_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="fondos_ojo",
    )

    disco_optico_od = models.TextField(blank=True, null=True)
    macula_od = models.TextField(blank=True, null=True)
    vasos_od = models.TextField(blank=True, null=True)
    retina_periferica_od = models.TextField(blank=True, null=True)
    av_temp_sup_od = models.TextField(blank=True, null=True)
    av_temp_inf_od = models.TextField(blank=True, null=True)
    av_nasal_sup_od = models.TextField(blank=True, null=True)
    av_nasal_inf_od = models.TextField(blank=True, null=True)
    retina_od = models.TextField(blank=True, null=True)
    excavacion_od = models.TextField(blank=True, null=True)
    papila_detalle_od = models.TextField(blank=True, null=True)
    fijacion_od = models.TextField(blank=True, null=True)
    color_od = models.TextField(blank=True, null=True)
    borde_od = models.TextField(blank=True, null=True)

    disco_optico_oi = models.TextField(blank=True, null=True)
    macula_oi = models.TextField(blank=True, null=True)
    vasos_oi = models.TextField(blank=True, null=True)
    retina_periferica_oi = models.TextField(blank=True, null=True)
    av_temp_sup_oi = models.TextField(blank=True, null=True)
    av_temp_inf_oi = models.TextField(blank=True, null=True)
    av_nasal_sup_oi = models.TextField(blank=True, null=True)
    av_nasal_inf_oi = models.TextField(blank=True, null=True)
    retina_oi = models.TextField(blank=True, null=True)
    excavacion_oi = models.TextField(blank=True, null=True)
    papila_detalle_oi = models.TextField(blank=True, null=True)
    fijacion_oi = models.TextField(blank=True, null=True)
    color_oi = models.TextField(blank=True, null=True)
    borde_oi = models.TextField(blank=True, null=True)

    observaciones = models.TextField(blank=True, null=True)
    otros_detalles = models.TextField(blank=True, null=True)
    fecha_examen = models.DateTimeField(db_column="fecha_examen", blank=True, null=True)

    class Meta:
        db_table = "fondo_ojo"
        managed = False
        verbose_name = "Fondo de ojo"
        verbose_name_plural = "Fondos de ojo"


class PresionIntraocular(models.Model):
    pio_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="presiones_intraoculares",
    )
    pio_od = models.CharField(max_length=10, blank=True, null=True)
    pio_oi = models.CharField(max_length=10, blank=True, null=True)
    metodo_medicion = models.CharField(max_length=50, blank=True, null=True)
    hora_medicion = models.TimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_medicion = models.DateTimeField(db_column="fecha_medicion", blank=True, null=True)

    class Meta:
        db_table = "presion_intraocular"
        managed = False
        verbose_name = "Presion intraocular"
        verbose_name_plural = "Presiones intraoculares"


class CampoVisual(models.Model):
    campo_visual_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="campos_visuales",
    )
    tipo_campo = models.CharField(max_length=50, blank=True, null=True)
    resultado_od = models.TextField(blank=True, null=True)
    resultado_oi = models.TextField(blank=True, null=True)
    interpretacion = models.TextField(blank=True, null=True)
    fecha_examen = models.DateTimeField(db_column="fecha_examen", blank=True, null=True)

    class Meta:
        db_table = "campos_visuales"
        managed = False
        verbose_name = "Campo visual"
        verbose_name_plural = "Campos visuales"


class DiagnosticoMedico(models.Model):
    diagnostico_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="diagnosticos",
    )
    diagnostico_principal = models.TextField(blank=True, null=True)
    diagnosticos_secundarios = models.TextField(blank=True, null=True)
    cie_10_principal = models.CharField(max_length=10, blank=True, null=True)
    cie_10_secundarios = models.TextField(blank=True, null=True)
    severidad = models.CharField(max_length=20, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_diagnostico = models.DateTimeField(db_column="fecha_diagnostico", blank=True, null=True)

    class Meta:
        db_table = "diagnosticos"
        managed = False
        verbose_name = "Diagnostico medico"
        verbose_name_plural = "Diagnosticos medicos"


class Tratamiento(models.Model):
    tratamiento_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="tratamientos",
    )
    medicamentos = models.TextField(blank=True, null=True)
    tratamiento_no_farmacologico = models.TextField(blank=True, null=True)
    recomendaciones = models.TextField(blank=True, null=True)
    plan_seguimiento = models.TextField(blank=True, null=True)
    proxima_cita = models.DateField(db_column="proxima_cita", blank=True, null=True)
    urgencia_seguimiento = models.CharField(max_length=20, blank=True, null=True)
    fecha_tratamiento = models.DateTimeField(db_column="fecha_tratamiento", blank=True, null=True)

    class Meta:
        db_table = "tratamientos"
        managed = False
        verbose_name = "Tratamiento"
        verbose_name_plural = "Tratamientos"


class ReflejosPupilares(models.Model):
    reflejo_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="reflejos_pupilares",
    )
    acomodativo_uno = models.TextField(blank=True, null=True)
    fotomotor_uno = models.TextField(blank=True, null=True)
    consensual_uno = models.TextField(blank=True, null=True)
    acomodativo_dos = models.TextField(blank=True, null=True)
    fotomotor_dos = models.TextField(blank=True, null=True)
    consensual_dos = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(db_column="fecha_registro", blank=True, null=True)

    class Meta:
        db_table = "reflejos_pupilares"
        managed = False
        verbose_name = "Reflejos pupilares"
        verbose_name_plural = "Reflejos pupilares"


class ParametrosClinicos(models.Model):
    parametro_id = models.AutoField(primary_key=True)
    ficha = models.ForeignKey(
        FichaClinica,
        on_delete=models.CASCADE,
        db_column="ficha_id",
        related_name="parametros_clinicos",
    )
    presion_sistolica = models.CharField(max_length=10, blank=True, null=True)
    presion_diastolica = models.CharField(max_length=10, blank=True, null=True)
    saturacion_o2 = models.CharField(max_length=10, blank=True, null=True)
    glucosa = models.CharField(max_length=20, blank=True, null=True)
    trigliceridos = models.CharField(max_length=20, blank=True, null=True)
    ttp = models.CharField(max_length=20, blank=True, null=True)
    atp = models.CharField(max_length=20, blank=True, null=True)
    colesterol = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(db_column="fecha_registro", blank=True, null=True)

    class Meta:
        db_table = "parametros_clinicos"
        managed = False
        verbose_name = "Parametro clinico"
        verbose_name_plural = "Parametros clinicos"
