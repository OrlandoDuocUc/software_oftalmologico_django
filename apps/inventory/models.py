from django.db import models


class Product(models.Model):
    producto_id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(blank=True, null=True)
    nombre = models.CharField(max_length=200)
    distribuidor = models.CharField(max_length=200, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    tipo_armazon = models.CharField(max_length=100, blank=True, null=True)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    diametro_1 = models.CharField(max_length=50, blank=True, null=True)
    diametro_2 = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    costo_venta_1 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    costo_venta_2 = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'productos'
        managed = False
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self) -> str:
        return self.nombre


class Proveedor(models.Model):
    proveedor_id = models.AutoField(primary_key=True)
    codigo_proveedor = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    nombre_comercial = models.CharField(max_length=255, blank=True, null=True)
    rut = models.CharField(max_length=12, unique=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.CharField(max_length=255, blank=True, null=True)
    categoria_productos = models.TextField(blank=True, null=True)
    condiciones_pago = models.CharField(max_length=50, default='Contado')
    plazo_pago_dias = models.IntegerField(default=0)
    descuento_volumen = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    representante_nombre = models.CharField(max_length=255, blank=True, null=True)
    representante_telefono = models.CharField(max_length=20, blank=True, null=True)
    representante_email = models.EmailField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(db_column='fecha_registro', blank=True, null=True)
    fecha_actualizacion = models.DateTimeField(db_column='fecha_actualizacion', blank=True, null=True)

    class Meta:
        db_table = 'proveedores'
        managed = False
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self) -> str:
        return self.razon_social


class Compra(models.Model):
    compra_id = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, db_column="proveedor_id", on_delete=models.DO_NOTHING)
    numero_factura = models.CharField(max_length=50, blank=True, null=True)
    ruc_ci = models.CharField(max_length=20, blank=True, null=True)
    fecha_pedido = models.DateField(blank=True, null=True)
    fecha_pago = models.DateField(blank=True, null=True)
    forma_pago = models.CharField(max_length=50, blank=True, null=True)
    plazo_pago = models.CharField(max_length=50, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)

    subtotal_general = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_tarifa_15 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_tarifa_5 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subtotal_tarifa_0 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva_15 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    iva_5 = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pagar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    abono = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    elaborado_codigo = models.CharField(max_length=50, blank=True, null=True)
    elaborado_nombre = models.CharField(max_length=150, blank=True, null=True)
    autorizado_codigo = models.CharField(max_length=50, blank=True, null=True)
    autorizado_nombre = models.CharField(max_length=150, blank=True, null=True)
    recibido_codigo = models.CharField(max_length=50, blank=True, null=True)
    recibido_nombre = models.CharField(max_length=150, blank=True, null=True)

    estado = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "compras"
        managed = False
        verbose_name = "Compra"
        verbose_name_plural = "Compras"

    def __str__(self) -> str:
        return f"Compra #{self.compra_id}"


class CompraDetalle(models.Model):
    detalle_id = models.AutoField(primary_key=True)
    compra = models.ForeignKey(Compra, db_column="compra_id", on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Product, db_column="producto_id", on_delete=models.DO_NOTHING)
    marca = models.CharField(max_length=100, blank=True, null=True)
    codigo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField(default=0)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tarifa_iva = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "compras_detalle"
        managed = False
        verbose_name = "Detalle de compra"
        verbose_name_plural = "Detalles de compra"

    def __str__(self) -> str:
        return f"Detalle #{self.detalle_id} de compra {self.compra_id}"
