from __future__ import annotations

import random
import re
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from django.db import transaction
from django.db.models import Q

from apps.clients.models import Cliente
from apps.shared.serializers import model_to_legacy_dict, sanitize_model_payload

from .models import (
    Biomicroscopia,
    FichaClinica,
    FondoOjo,
    PacienteMedico,
    ParametrosClinicos,
    ReflejosPupilares,
    Tratamiento,
    DiagnosticoMedico,
    PresionIntraocular,
)


class PacienteMedicoService:
    """
    Servicio para replicar el comportamiento del PacienteMedicoController original.
    """

    rut_regex = re.compile(r"\D+")

    # ---------------- Utilidades ----------------
    def _validar_identificacion_ec(self, valor: str) -> bool:
        if not valor:
            return False
        s = self.rut_regex.sub("", valor)
        if len(s) == 10:
            return self._validar_cedula_ec(s)
        if len(s) == 13 and s.endswith("001"):
            return self._validar_cedula_ec(s[:10])
        return False

    @staticmethod
    def _validar_cedula_ec(ci: str) -> bool:
        if not re.fullmatch(r"\d{10}", ci):
            return False
        provincia = int(ci[:2])
        if provincia < 1 or provincia > 24:
            return False
        coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        suma = 0
        for i in range(9):
            prod = int(ci[i]) * coef[i]
            if prod >= 10:
                prod -= 9
            suma += prod
        decena = ((suma + 9) // 10) * 10
        digito = (decena - suma) % 10
        return digito == int(ci[9])

    def _normalizar_rut(self, valor: str) -> str:
        return self.rut_regex.sub("", valor or "").strip()

    def _generar_numero_ficha(self) -> str:
        for _ in range(5):
            ahora = datetime.utcnow()
            pref = f"FM-{ahora.year}{str(ahora.month).zfill(2)}-{int(ahora.timestamp() * 1000)}-{random.randint(100,999)}"
            if not PacienteMedico.objects.filter(numero_ficha=pref).exists():
                return pref
        return f"FM-{int(datetime.utcnow().timestamp()*1000)}-{random.randint(1000,9999)}"

    def _cliente_to_dict(self, cliente: Optional[Cliente]) -> dict:
        if not cliente:
            return {}
        return {
            "cliente_id": cliente.cliente_id,
            "nombres": cliente.nombres,
            "ap_pat": cliente.ap_pat,
            "ap_mat": cliente.ap_mat,
            "rut": cliente.rut,
            "email": cliente.email,
            "telefono": cliente.telefono,
            "direccion": cliente.direccion,
            "fecha_nacimiento": cliente.fecha_nacimiento.isoformat() if cliente.fecha_nacimiento else None,
            "estado": cliente.estado,
        }

    def _paciente_to_dict(self, paciente: PacienteMedico, include_cliente: bool = True) -> dict:
        data = {
            "paciente_medico_id": paciente.paciente_medico_id,
            "cliente_id": paciente.cliente_id,
            "numero_ficha": paciente.numero_ficha,
            "antecedentes_medicos": paciente.antecedentes_medicos,
            "antecedentes_oculares": paciente.antecedentes_oculares,
            "alergias": paciente.alergias,
            "medicamentos_actuales": paciente.medicamentos_actuales,
            "contacto_emergencia": paciente.contacto_emergencia,
            "telefono_emergencia": paciente.telefono_emergencia,
            "fecha_registro": paciente.fecha_registro.isoformat() if paciente.fecha_registro else None,
            "estado": paciente.estado,
        }
        if include_cliente:
            data["cliente"] = self._cliente_to_dict(getattr(paciente, "cliente", None))
        return data

    # ---------------- Operaciones ----------------
    def list_pacientes(self) -> Iterable[dict]:
        pacientes = PacienteMedico.objects.select_related("cliente").order_by("-paciente_medico_id")
        return [self._paciente_to_dict(p) for p in pacientes]

    def search(self, query: str) -> Iterable[dict]:
        qs = PacienteMedico.objects.select_related("cliente")
        if query:
            like = Q(cliente__nombres__icontains=query) | Q(cliente__ap_pat__icontains=query) | Q(
                cliente__ap_mat__icontains=query
            ) | Q(cliente__rut__icontains=query)
            qs = qs.filter(like)
        pacientes = qs.order_by("-paciente_medico_id")
        return [self._paciente_to_dict(p) for p in pacientes]

    def get_by_id(self, paciente_id: int) -> Optional[dict]:
        paciente = (
            PacienteMedico.objects.select_related("cliente")
            .filter(paciente_medico_id=paciente_id)
            .first()
        )
        if not paciente:
            return None
        return self._paciente_to_dict(paciente)

    def get_personas(self, q: str = "", estado: Optional[str] = None, limit: int = 100, offset: int = 0):
        pacientes_qs = PacienteMedico.objects.select_related("cliente")
        if q:
            like = Q(cliente__nombres__icontains=q) | Q(cliente__ap_pat__icontains=q) | Q(
                cliente__ap_mat__icontains=q
            ) | Q(cliente__rut__icontains=q)
            pacientes_qs = pacientes_qs.filter(like)
        if estado in ("true", "false"):
            pacientes_qs = pacientes_qs.filter(estado=(estado == "true"))

        items = []
        cliente_ids = set()
        for paciente in pacientes_qs:
            items.append(
                {
                    "type": "paciente",
                    **self._paciente_to_dict(paciente),
                }
            )
            cliente_ids.add(paciente.cliente_id)

        clientes_qs = Cliente.objects.exclude(cliente_id__in=cliente_ids)
        if q:
            like = Q(nombres__icontains=q) | Q(ap_pat__icontains=q) | Q(ap_mat__icontains=q) | Q(rut__icontains=q)
            clientes_qs = clientes_qs.filter(like)
        if estado in ("true", "false"):
            clientes_qs = clientes_qs.filter(estado=(estado == "true"))

        clientes_qs = clientes_qs.order_by("nombres")[offset : offset + limit]
        for cliente in clientes_qs:
            items.append(
                {
                    "type": "cliente",
                    "cliente_id": cliente.cliente_id,
                    "estado": cliente.estado,
                    "cliente": self._cliente_to_dict(cliente),
                }
            )
        return items

    @transaction.atomic
    def create_paciente(self, payload: dict) -> dict:
        cli_in = payload.get("cliente") or {}
        pac_in = payload.get("paciente_medico") or {}

        rut_norm = self._normalizar_rut(cli_in.get("rut", ""))
        if not self._validar_identificacion_ec(rut_norm):
            raise ValueError("Cédula/RUC inválido para Ecuador.")

        nombres = (cli_in.get("nombres") or "").strip()
        ap_pat = (cli_in.get("ap_pat") or "").strip()
        if not nombres or not ap_pat:
            raise ValueError("Nombres y Apellido Paterno son obligatorios.")

        cliente, created = Cliente.objects.get_or_create(
            rut=rut_norm,
            defaults={
                "nombres": nombres,
                "ap_pat": ap_pat,
                "ap_mat": (cli_in.get("ap_mat") or "").strip() or None,
                "email": (cli_in.get("email") or "").strip() or None,
                "telefono": (cli_in.get("telefono") or "").strip() or None,
                "direccion": (cli_in.get("direccion") or "").strip() or None,
                "estado": True,
            },
        )
        if not created:
            # actualizar campos
            cliente.nombres = nombres or cliente.nombres
            cliente.ap_pat = ap_pat or cliente.ap_pat
            if cli_in.get("ap_mat") is not None:
                cliente.ap_mat = (cli_in.get("ap_mat") or "").strip() or None
            if cli_in.get("email") is not None:
                cliente.email = (cli_in.get("email") or "").strip() or None
            if cli_in.get("telefono") is not None:
                cliente.telefono = (cli_in.get("telefono") or "").strip() or None
            if cli_in.get("direccion") is not None:
                cliente.direccion = (cli_in.get("direccion") or "").strip() or None
            if cli_in.get("fecha_nacimiento"):
                try:
                    cliente.fecha_nacimiento = datetime.fromisoformat(cli_in["fecha_nacimiento"]).date()
                except Exception:
                    pass
            if cli_in.get("estado") is not None:
                cliente.estado = bool(cli_in.get("estado"))
            cliente.save()

        existente = PacienteMedico.objects.filter(cliente_id=cliente.cliente_id).first()
        if existente:
            return {
                "already_exists": True,
                "data": self._paciente_to_dict(existente),
            }

        numero_ficha = (pac_in.get("numero_ficha") or "").strip()
        if not numero_ficha or PacienteMedico.objects.filter(numero_ficha=numero_ficha).exists():
            numero_ficha = self._generar_numero_ficha()

        paciente = PacienteMedico.objects.create(
            cliente_id=cliente.cliente_id,
            numero_ficha=numero_ficha,
            antecedentes_medicos=(pac_in.get("antecedentes_medicos") or "").strip() or None,
            antecedentes_oculares=(pac_in.get("antecedentes_oculares") or "").strip() or None,
            alergias=(pac_in.get("alergias") or "").strip() or None,
            medicamentos_actuales=(pac_in.get("medicamentos_actuales") or "").strip() or None,
            contacto_emergencia=(pac_in.get("contacto_emergencia") or "").strip() or None,
            telefono_emergencia=(pac_in.get("telefono_emergencia") or "").strip() or None,
            estado=bool(pac_in.get("estado", True)),
        )
        paciente.refresh_from_db()
        return {
            "already_exists": False,
            "data": self._paciente_to_dict(paciente),
        }


class BiomicroscopiaService:
    """
    Replica del servicio de casos de uso del proyecto Flask pero usando Django ORM.
    """

    def obtener_examen(self, ficha_id: int) -> Dict[str, Any]:
        data = {
            "biomicroscopia": None,
            "reflejos": None,
            "fondo_ojo": None,
            "parametros": None,
            "diagnostico": None,
            "tratamiento": None,
        }

        bio = Biomicroscopia.objects.filter(ficha_id=ficha_id).first()
        if bio:
            data["biomicroscopia"] = model_to_legacy_dict(bio)

        reflejos = ReflejosPupilares.objects.filter(ficha_id=ficha_id).first()
        if reflejos:
            data["reflejos"] = model_to_legacy_dict(reflejos)

        fondo = FondoOjo.objects.filter(ficha_id=ficha_id).first()
        if fondo:
            data["fondo_ojo"] = model_to_legacy_dict(fondo)

        parametros = ParametrosClinicos.objects.filter(ficha_id=ficha_id).first()
        if parametros:
            data["parametros"] = model_to_legacy_dict(parametros)

        diag = (
            DiagnosticoMedico.objects.filter(ficha_id=ficha_id)
            .order_by("-fecha_diagnostico")
            .first()
        )
        if diag:
            data["diagnostico"] = model_to_legacy_dict(diag)

        tx = (
            Tratamiento.objects.filter(ficha_id=ficha_id)
            .order_by("-fecha_tratamiento")
            .first()
        )
        if tx:
            data["tratamiento"] = model_to_legacy_dict(tx)

        return data


    def guardar_examen(self, ficha_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        ficha = FichaClinica.objects.filter(ficha_id=ficha_id).first()
        if not ficha:
            raise ValueError("Ficha clínica no encontrada")

        seccion_bio = sanitize_model_payload(Biomicroscopia, payload.get("biomicroscopia") or {})
        seccion_reflejos = sanitize_model_payload(ReflejosPupilares, payload.get("reflejos") or {})
        seccion_fondo = sanitize_model_payload(FondoOjo, payload.get("fondo_ojo") or {})
        seccion_parametros = sanitize_model_payload(ParametrosClinicos, payload.get("parametros") or {})

        with transaction.atomic():
            bio, _ = Biomicroscopia.objects.update_or_create(
                ficha=ficha, defaults=seccion_bio
            )
            reflejos, _ = ReflejosPupilares.objects.update_or_create(
                ficha=ficha, defaults=seccion_reflejos
            )
            fondo, _ = FondoOjo.objects.update_or_create(
                ficha=ficha, defaults=seccion_fondo
            )
            parametros, _ = ParametrosClinicos.objects.update_or_create(
                ficha=ficha, defaults=seccion_parametros
            )

            diagnostico_result = None
            tratamiento_result = None

            diag_payload = payload.get("diagnostico")
            if diag_payload:
                if isinstance(diag_payload, dict):
                    diag_defaults = sanitize_model_payload(DiagnosticoMedico, diag_payload)
                else:
                    diag_defaults = {"diagnostico_principal": str(diag_payload)}

                diag = (
                    DiagnosticoMedico.objects.filter(ficha=ficha)
                    .order_by("-fecha_diagnostico")
                    .first()
                )
                if diag:
                    for key, value in diag_defaults.items():
                        setattr(diag, key, value)
                    diag.save()
                else:
                    diag = DiagnosticoMedico.objects.create(ficha=ficha, **diag_defaults)
                diagnostico_result = model_to_legacy_dict(diag)

            tratamiento_payload = payload.get("tratamiento")
            if tratamiento_payload:
                if isinstance(tratamiento_payload, dict):
                    tx_defaults = sanitize_model_payload(Tratamiento, tratamiento_payload)
                else:
                    tx_defaults = {"medicamentos": str(tratamiento_payload)}

                tx = (
                    Tratamiento.objects.filter(ficha=ficha)
                    .order_by("-fecha_tratamiento")
                    .first()
                )
                if tx:
                    for key, value in tx_defaults.items():
                        setattr(tx, key, value)
                    tx.save()
                else:
                    tx = Tratamiento.objects.create(ficha=ficha, **tx_defaults)
                tratamiento_result = model_to_legacy_dict(tx)

        return {
            "biomicroscopia": model_to_legacy_dict(bio),
            "reflejos": model_to_legacy_dict(reflejos),
            "fondo_ojo": model_to_legacy_dict(fondo),
            "parametros": model_to_legacy_dict(parametros),
            "diagnostico": diagnostico_result,
            "tratamiento": tratamiento_result,
        }

class FichaClinicaService:
    editable_fields = [
        "paciente_medico_id",
        "usuario_id",
        "numero_consulta",
        "fecha_consulta",
        "motivo_consulta",
        "historia_actual",
        "av_od_sc",
        "av_od_cc",
        "av_od_ph",
        "av_od_cerca",
        "av_oi_sc",
        "av_oi_cc",
        "av_oi_ph",
        "av_oi_cerca",
        "esfera_od",
        "cilindro_od",
        "eje_od",
        "adicion_od",
        "esfera_oi",
        "cilindro_oi",
        "eje_oi",
        "adicion_oi",
        "distancia_pupilar",
        "tipo_lente",
        "estado",
    ]

    def _serialize(self, ficha: FichaClinica) -> dict:
        data = {
            "ficha_id": ficha.ficha_id,
            "paciente_medico_id": ficha.paciente_medico_id,
            "usuario_id": ficha.usuario_id,
            "numero_consulta": ficha.numero_consulta,
            "fecha_consulta": ficha.fecha_consulta.isoformat() if ficha.fecha_consulta else None,
            "motivo_consulta": ficha.motivo_consulta,
            "historia_actual": ficha.historia_actual,
            "estado": ficha.estado,
            "fecha_creacion": ficha.fecha_creacion.isoformat() if ficha.fecha_creacion else None,
        }
        for field in [
            "av_od_sc",
            "av_od_cc",
            "av_od_ph",
            "av_od_cerca",
            "av_oi_sc",
            "av_oi_cc",
            "av_oi_ph",
            "av_oi_cerca",
            "esfera_od",
            "cilindro_od",
            "eje_od",
            "adicion_od",
            "esfera_oi",
            "cilindro_oi",
            "eje_oi",
            "adicion_oi",
            "distancia_pupilar",
            "tipo_lente",
        ]:
            data[field] = getattr(ficha, field)

        if ficha.paciente_medico:
            data["paciente_medico"] = {
                "paciente_medico_id": ficha.paciente_medico.paciente_medico_id,
                "numero_ficha": ficha.paciente_medico.numero_ficha,
            }
            cliente = getattr(ficha.paciente_medico, "cliente", None)
            if cliente:
                data["paciente_medico"]["cliente"] = {
                    "cliente_id": cliente.cliente_id,
                    "nombres": cliente.nombres,
                    "ap_pat": cliente.ap_pat,
                    "ap_mat": cliente.ap_mat,
                    "rut": cliente.rut,
                }

        if ficha.usuario:
            data["usuario"] = {
                "usuario_id": ficha.usuario.usuario_id,
                "nombre": ficha.usuario.nombre,
                "ap_pat": ficha.usuario.ap_pat,
            }
        return data

    def list_fichas(self) -> Iterable[dict]:
        fichas = (
            FichaClinica.objects.select_related("paciente_medico__cliente", "usuario")
            .order_by("-fecha_consulta")
            .all()
        )
        return [self._serialize(f) for f in fichas]

    def get_ficha(self, ficha_id: int) -> Optional[dict]:
        ficha = (
            FichaClinica.objects.select_related("paciente_medico__cliente", "usuario")
            .filter(ficha_id=ficha_id)
            .first()
        )
        if not ficha:
            return None
        return self._serialize(ficha)

    def create_ficha(self, payload: dict) -> dict:
        cleaned = self._clean_fields(payload)
        ficha = FichaClinica.objects.create(**cleaned)
        return self.get_ficha(ficha.ficha_id)

    def update_ficha(self, ficha_id: int, payload: dict) -> Optional[dict]:
        ficha = FichaClinica.objects.filter(ficha_id=ficha_id).first()
        if not ficha:
            return None
        cleaned = self._clean_fields(payload)
        for key, value in cleaned.items():
            setattr(ficha, key, value)
        ficha.save()
        return self.get_ficha(ficha_id)

    def resumen_examenes(self, ficha_id: int) -> dict:
        data = {"ficha_id": ficha_id, "fondo_ojo": None, "presion_intraocular": None}

        fondo = (
            FondoOjo.objects.filter(ficha_id=ficha_id)
            .order_by("-fecha_examen")
            .first()
        )
        if fondo:
            data["fondo_ojo"] = {
                "od": ", ".join(filter(None, [fondo.disco_optico_od, fondo.macula_od, fondo.vasos_od, fondo.retina_periferica_od])),
                "oi": ", ".join(filter(None, [fondo.disco_optico_oi, fondo.macula_oi, fondo.vasos_oi, fondo.retina_periferica_oi])),
                "observaciones": fondo.observaciones or fondo.otros_detalles,
                "fecha_examen": fondo.fecha_examen.isoformat() if fondo.fecha_examen else None,
            }

        pio = (
            PresionIntraocular.objects.filter(ficha_id=ficha_id)
            .order_by("-fecha_medicion")
            .first()
        )
        if pio:
            data["presion_intraocular"] = {
                "pio_od": pio.pio_od,
                "pio_oi": pio.pio_oi,
                "metodo": pio.metodo_medicion,
                "hora": pio.hora_medicion.isoformat() if pio.hora_medicion else None,
                "observaciones": pio.observaciones,
                "fecha_medicion": pio.fecha_medicion.isoformat() if pio.fecha_medicion else None,
            }

        return data

    def _clean_fields(self, payload: dict) -> dict:
        data = {}
        for field in self.editable_fields:
            if field in payload:
                data[field] = payload[field]
        fecha = data.get("fecha_consulta")
        if fecha:
            try:
                data["fecha_consulta"] = datetime.fromisoformat(fecha)
            except Exception:
                pass
        return data
