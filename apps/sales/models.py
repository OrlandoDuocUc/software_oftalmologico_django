from django.db import models

from apps.accounts.models import LegacyUser
from apps.clients.models import Cliente
from apps.inventory.models import Product


class Sale(models.Model):
    venta_id = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, db_column='cliente_id', blank=True, null=True, related_name='ventas')
    usuario = models.ForeignKey(LegacyUser, on_delete=models.SET_NULL, db_column='usuario_id', blank=True, null=True, related_name='ventas')
    fecha_venta = models.DateTimeField(db_column='fecha_venta', blank=True, null=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, blank=True, null=True)
    numero_factura = models.CharField(max_length=50, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    subtotal_general = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subtotal_tarifa_15 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subtotal_tarifa_5 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    subtotal_tarifa_0 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    iva_15 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    iva_5 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    abono = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'ventas'
        managed = False
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self) -> str:
        return f"Venta #{self.venta_id}"


class SaleDetail(models.Model):
    detalle_id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Sale, on_delete=models.CASCADE, db_column='venta_id', related_name='detalles')
    producto = models.ForeignKey(Product, on_delete=models.DO_NOTHING, db_column='producto_id', related_name='detalles')
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tarifa_iva = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    codigo_principal = models.CharField(max_length=100, blank=True, null=True)
    codigo_auxiliar = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'detalle_ventas'
        managed = False
        verbose_name = 'Detalle de venta'
        verbose_name_plural = 'Detalles de venta'

    def __str__(self) -> str:
        return f"Detalle {self.detalle_id} de venta {self.venta_id}"
