from __future__ import annotations

import json

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.clients.models import Cliente

from .models import (
    Biomicroscopia,
    DiagnosticoMedico,
    FichaClinica,
    FondoOjo,
    Tratamiento,
)
from .services import BiomicroscopiaService, PacienteMedicoService, FichaClinicaService

service = BiomicroscopiaService()
paciente_service = PacienteMedicoService()
ficha_service = FichaClinicaService()

BIO_ROWS = [
    ("cornea_od", "C&oacute;rnea", "cornea_oi"),
    ("cristalino_od", "Cristalino", "cristalino_oi"),
    ("pupila_desc_od", "Pupila", "pupila_desc_oi"),
    ("iris_od", "Iris", "iris_oi"),
    ("pestanas_od", "Pesta&ntilde;as", "pestanas_oi"),
    ("conjuntiva_bulbar_od", "Conjuntiva bulbar", "conjuntiva_bulbar_oi"),
    ("conjuntiva_tarsal_od", "Conjuntiva tarsal", "conjuntiva_tarsal_oi"),
    ("orbita_od", "&Oacute;rbita", "orbita_oi"),
    ("pliegue_semilunar_od", "Pliegue semilunar", "pliegue_semilunar_oi"),
    ("caruncula_od", "Car&uacute;ncula", "caruncula_oi"),
    ("conductos_lagrimales_od", "Conductos lagrimales", "conductos_lagrimales_oi"),
    ("parpado_superior_od", "P&aacute;rpado superior", "parpado_superior_oi"),
    ("camara_anterior_od", "C&aacute;mara anterior", "camara_anterior_oi"),
    ("parpado_inferior_od", "P&aacute;rpado inferior", "parpado_inferior_oi"),
    ("parpados_od", "P&aacute;rpados (general)", "parpados_oi"),
    ("conjuntiva_od", "Conjuntiva (general)", "conjuntiva_oi"),
]

FONDO_ROWS = [
    ("disco_optico_od", "Disco &oacute;ptico", "disco_optico_oi"),
    ("macula_od", "M&aacute;cula", "macula_oi"),
    ("vasos_od", "Vasos", "vasos_oi"),
    ("retina_periferica_od", "Retina perif&eacute;rica", "retina_periferica_oi"),
    ("av_temp_sup_od", "A/V temporal sup", "av_temp_sup_oi"),
    ("av_temp_inf_od", "A/V temporal inf", "av_temp_inf_oi"),
    ("av_nasal_sup_od", "A/V nasal sup", "av_nasal_sup_oi"),
    ("av_nasal_inf_od", "A/V nasal inf", "av_nasal_inf_oi"),
    ("retina_od", "Retina", "retina_oi"),
    ("excavacion_od", "Excavaci&oacute;n", "excavacion_oi"),
    ("papila_detalle_od", "Papila", "papila_detalle_oi"),
    ("fijacion_od", "Fijaci&oacute;n", "fijacion_oi"),
    ("color_od", "Color", "color_oi"),
    ("borde_od", "Borde", "borde_oi"),
]

FOOTER_INFO = {
    "direccion": "CALLE GARCÍA AVILES 318 entre Av. 9 de OCTUBRE Y VELEZ",
    "telefonos": "Telf: 0980632277 / 0998436958 / 0985394814",
    "ciudad": "Guayaquil",
}


def _format_fecha_es(value: datetime | None) -> str:
    if not value:
        value = timezone.now()
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    return f"{value.day} de {meses[value.month - 1]} de {value.year}"


def _calcular_edad(nacimiento, referencia) -> int | None:
    if not nacimiento or not referencia:
        return None
    if isinstance(referencia, datetime):
        ref_date = referencia.date()
    else:
        ref_date = referencia
    edad = ref_date.year - nacimiento.year - (
        (ref_date.month, ref_date.day) < (nacimiento.month, nacimiento.day)
    )
    return max(edad, 0)


def _compactar_campos(instance, campos) -> str | None:
    partes = []
    for campo in campos:
        valor = getattr(instance, campo, "")
        if valor:
            partes.append(str(valor).strip())
    return ", ".join(partes) if partes else None


def _resumen_biomicroscopia(ficha_id: int) -> str | None:
    bio = Biomicroscopia.objects.filter(ficha_id=ficha_id).first()
    if not bio:
        return None
    od = _compactar_campos(
        bio,
        [
            "parpados_od",
            "conjuntiva_od",
            "cornea_od",
            "camara_anterior_od",
            "iris_od",
            "cristalino_od",
        ],
    )
    oi = _compactar_campos(
        bio,
        [
            "parpados_oi",
            "conjuntiva_oi",
            "cornea_oi",
            "camara_anterior_oi",
            "iris_oi",
            "cristalino_oi",
        ],
    )
    obs = getattr(bio, "observaciones_generales", None)
    partes = []
    if od:
        partes.append(f"OD: {od}")
    if oi:
        partes.append(f"OI: {oi}")
    if obs:
        partes.append(obs.strip())
    return ". ".join(partes) if partes else None


def _resumen_fondo_ojo(ficha_id: int) -> str | None:
    fo = FondoOjo.objects.filter(ficha_id=ficha_id).first()
    if not fo:
        return None
    od = _compactar_campos(fo, ["disco_optico_od", "macula_od", "vasos_od", "retina_periferica_od"])
    oi = _compactar_campos(fo, ["disco_optico_oi", "macula_oi", "vasos_oi", "retina_periferica_oi"])
    obs = getattr(fo, "observaciones", None)
    partes = []
    if od:
        partes.append(f"OD: {od}")
    if oi:
        partes.append(f"OI: {oi}")
    if obs:
        partes.append(obs.strip())
    return ". ".join(partes) if partes else None


def _resumen_diagnostico(ficha_id: int) -> str | None:
    dx = DiagnosticoMedico.objects.filter(ficha_id=ficha_id).order_by("-fecha_diagnostico").first()
    if not dx:
        return None
    partes = []
    principal = (dx.diagnostico_principal or "").strip()
    if principal:
        cie = f" ({dx.cie_10_principal})" if dx.cie_10_principal else ""
        partes.append(f"{principal}{cie}")
    secundarios = []
    if dx.diagnosticos_secundarios:
        secundarios.append(dx.diagnosticos_secundarios.strip())
    if dx.cie_10_secundarios:
        secundarios.append(dx.cie_10_secundarios.strip())
    if secundarios:
        partes.append(", ".join(secundarios))
    return ", ".join(partes) if partes else None


def _tratamiento_items(ficha_id: int) -> list[str]:
    tx = Tratamiento.objects.filter(ficha_id=ficha_id).order_by("-fecha_tratamiento").first()
    if not tx:
        return []
    bloques = [
        getattr(tx, "medicamentos", None),
        getattr(tx, "tratamiento_no_farmacologico", None),
        getattr(tx, "recomendaciones", None),
        getattr(tx, "plan_seguimiento", None),
    ]
    items: list[str] = []
    for bloque in bloques:
        if not bloque:
            continue
        for linea in str(bloque).splitlines():
            limpio = linea.strip().lstrip("-•·").strip()
            if limpio:
                items.append(limpio)
    return items

def _render(request: HttpRequest, template: str, context: dict | None = None) -> HttpResponse:
    return render(request, template, context or {})


@login_required
def pacientes(request: HttpRequest) -> HttpResponse:
    return _render(request, "medical/pacientes_nuevo.html")


@login_required
def nuevo_paciente(request: HttpRequest) -> HttpResponse:
    return _render(request, "medical/nuevo_paciente_form.html")


@login_required
def ver_paciente(request: HttpRequest, paciente_id: int) -> HttpResponse:
    return _render(request, "medical/detalle_paciente.html", {"paciente_id": paciente_id})


@login_required
def editar_paciente(request: HttpRequest, paciente_id: int) -> HttpResponse:
    return _render(request, "medical/editar_paciente.html", {"paciente_id": paciente_id})


@login_required
def historial_paciente(request: HttpRequest, paciente_id: int) -> HttpResponse:
    return _render(request, "medical/historial_paciente.html", {"paciente_id": paciente_id})


@login_required
def consultas(request: HttpRequest) -> HttpResponse:
    return _render(request, "medical/consultas_nuevo.html")


@login_required
def nueva_consulta(request: HttpRequest) -> HttpResponse:
    return redirect("medical:ficha_clinica")


@login_required
def ver_consulta(request: HttpRequest, consulta_id: int) -> HttpResponse:
    return _render(request, "medical/detalle_consulta.html", {"consulta_id": consulta_id})


@login_required
def editar_consulta(request: HttpRequest, consulta_id: int) -> HttpResponse:
    return _render(request, "medical/editar_consulta.html", {"consulta_id": consulta_id})


@login_required
def dashboard_medico(request: HttpRequest) -> HttpResponse:
    return _render(request, "medical/dashboard_medico_final.html")


@login_required
def ficha_clinica_view(request: HttpRequest) -> HttpResponse:
    return _render(request, "medical/ficha_clinica_nuevo.html")


@login_required
def biomicroscopia_nuevo(request: HttpRequest) -> HttpResponse:
    context = request.GET.dict()
    context.update({"bio_rows": BIO_ROWS, "fondo_rows": FONDO_ROWS})
    return _render(request, "medical/biomicroscopia_nuevo.html", context)


@login_required
def certificado_view(request: HttpRequest, consulta_id: int) -> HttpResponse:
    consulta = (
        FichaClinica.objects.select_related("paciente_medico__cliente", "usuario")
        .filter(ficha_id=consulta_id)
        .first()
    )
    if not consulta:
        raise Http404("Ficha clínica no encontrada")

    paciente = consulta.paciente_medico
    cliente = paciente.cliente if paciente else None
    fecha_consulta = consulta.fecha_consulta or timezone.now()
    edad = (
        _calcular_edad(getattr(cliente, "fecha_nacimiento", None), fecha_consulta.date())
        if cliente and cliente.fecha_nacimiento
        else None
    )

    context = {
        "consulta": consulta,
        "paciente": paciente,
        "cliente": cliente,
        "edad": edad,
        "fecha_consulta_str": _format_fecha_es(fecha_consulta),
        "biomicroscopia_texto": _resumen_biomicroscopia(consulta_id),
        "fondo_ojo_texto": _resumen_fondo_ojo(consulta_id),
        "diagnostico_texto": _resumen_diagnostico(consulta_id),
        "tratamiento_items": _tratamiento_items(consulta_id),
        "medico_nombre": f"{consulta.usuario.nombre} {consulta.usuario.ap_pat}".strip()
        if consulta.usuario
        else None,
        "footer_info": FOOTER_INFO,
    }
    context["consulta_id"] = consulta_id
    return _render(request, "medical/certificado.html", context)


@login_required
def examen_oftalmologico_view(request: HttpRequest, consulta_id: int) -> HttpResponse:
    return _render(
        request,
        "medical/examen_oftalmologico_nuevo.html",
        {"consulta_id": consulta_id},
    )


@login_required
def api_biomicroscopia_detail(request: HttpRequest, ficha_id: int) -> JsonResponse:
    data = service.obtener_examen(ficha_id)
    return JsonResponse({"success": True, "data": data})


@login_required
@require_http_methods(["POST"])
def api_biomicroscopia_save(request: HttpRequest) -> JsonResponse:
    body = request.body.decode("utf-8") or "{}"
    payload = json.loads(body)
    ficha_id = payload.get("ficha_id") or request.POST.get("ficha_id")
    if not ficha_id:
        return JsonResponse({"success": False, "message": "ficha_id requerido"}, status=400)
    result = service.guardar_examen(int(ficha_id), payload)
    return JsonResponse({"success": True, "data": result}, status=201)


@login_required
@require_http_methods(["GET", "POST"])
def api_fichas_clinicas(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        data = ficha_service.list_fichas()
        return JsonResponse({"success": True, "data": data})

    payload = json.loads(request.body or "{}")
    created = ficha_service.create_ficha(payload)
    return JsonResponse({"success": True, "data": created}, status=201)


@login_required
@require_http_methods(["GET", "PUT"])
def api_ficha_clinica_by_id(request: HttpRequest, ficha_id: int) -> JsonResponse:
    if request.method == "GET":
        ficha = ficha_service.get_ficha(ficha_id)
        if not ficha:
            return JsonResponse({"success": False, "message": "Ficha no encontrada"}, status=404)
        return JsonResponse({"success": True, "data": ficha})

    payload = json.loads(request.body or "{}")
    ficha = ficha_service.update_ficha(ficha_id, payload)
    if not ficha:
        return JsonResponse({"success": False, "message": "Ficha no encontrada"}, status=404)
    return JsonResponse({"success": True, "data": ficha})


@login_required
def api_examenes_por_ficha(request: HttpRequest, ficha_id: int) -> JsonResponse:
    data = ficha_service.resumen_examenes(ficha_id)
    return JsonResponse({"success": True, "data": data})


@login_required
def api_get_personas(request: HttpRequest) -> JsonResponse:
    q = (request.GET.get("q") or "").strip()
    estado = request.GET.get("estado")
    limit = int(request.GET.get("limit", 100))
    offset = int(request.GET.get("offset", 0))
    items = paciente_service.get_personas(q=q, estado=estado, limit=limit, offset=offset)
    return JsonResponse({"success": True, "data": items, "meta": {"count": len(items)}})


@login_required
def api_get_cliente(request: HttpRequest, cliente_id: int) -> JsonResponse:
    cliente = Cliente.objects.filter(cliente_id=cliente_id).first()
    if not cliente:
        return JsonResponse({"success": False, "message": "Cliente no encontrado"}, status=404)
    return JsonResponse({"success": True, "data": paciente_service._cliente_to_dict(cliente)})


@login_required
@require_http_methods(["GET", "POST"])
def api_pacientes_medicos(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        data = paciente_service.list_pacientes()
        return JsonResponse({"success": True, "data": data})

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}
    try:
        result = paciente_service.create_paciente(payload)
    except ValueError as exc:
        return JsonResponse({"success": False, "message": str(exc)}, status=400)

    status = 201 if not result["already_exists"] else 200
    message = "Paciente creado correctamente." if not result["already_exists"] else "El cliente ya es paciente."
    return JsonResponse({"success": True, "message": message, "data": result["data"]}, status=status)


@login_required
def api_get_paciente_medico(request: HttpRequest, paciente_id: int) -> JsonResponse:
    data = paciente_service.get_by_id(paciente_id)
    if not data:
        return JsonResponse({"success": False, "message": "Paciente no encontrado"}, status=404)
    return JsonResponse({"success": True, "data": data})


@login_required
def api_search_pacientes_medicos(request: HttpRequest) -> JsonResponse:
    q = (request.GET.get("q") or "").strip()
    data = paciente_service.search(q)
    return JsonResponse({"success": True, "data": data})


@login_required
def api_paciente_consultas(request: HttpRequest, paciente_id: int) -> JsonResponse:
    consultas = (
        FichaClinica.objects.select_related("usuario", "paciente_medico")
        .filter(paciente_medico_id=paciente_id)
        .order_by("-fecha_consulta")
    )
    data = []
    for ficha in consultas:
        item = {
            "ficha_id": ficha.ficha_id,
            "numero_consulta": ficha.numero_consulta,
            "fecha_consulta": ficha.fecha_consulta.isoformat() if ficha.fecha_consulta else None,
            "estado": ficha.estado,
            "motivo_consulta": ficha.motivo_consulta,
        }
        if ficha.paciente_medico:
            item["paciente_medico"] = {
                "paciente_medico_id": ficha.paciente_medico.paciente_medico_id,
                "numero_ficha": ficha.paciente_medico.numero_ficha,
            }
        if ficha.usuario:
            item["usuario"] = {
                "usuario_id": ficha.usuario.usuario_id,
                "nombre": ficha.usuario.nombre,
                "ap_pat": ficha.usuario.ap_pat,
            }
        data.append(item)
    return JsonResponse({"success": True, "data": data})


@login_required
def api_consultas(request: HttpRequest) -> JsonResponse:
    """
    Endpoint flexible para obtener consultas (fichas cl�nicas).
    Acepta varios alias de par�metros heredados del sistema Flask:
      - paciente_id, pacienteId, paciente_medico_id, pacienteMedicoId, pmid
    Si no se env�a filtro, devuelve todas las consultas.
    """
    # Normalizar posibles nombres de par�metro que llegan desde templates legacy
    paciente_id = (
        request.GET.get("paciente_id")
        or request.GET.get("pacienteId")
        or request.GET.get("paciente_medico_id")
        or request.GET.get("pacienteMedicoId")
        or request.GET.get("pmid")
    )

    qs = FichaClinica.objects.select_related("usuario", "paciente_medico").order_by("-fecha_consulta")
    if paciente_id:
        try:
            qs = qs.filter(paciente_medico_id=int(paciente_id))
        except ValueError:
            return JsonResponse({"success": False, "message": "paciente_id inv�lido"}, status=400)

    data = []
    for ficha in qs:
        item = {
            "ficha_id": ficha.ficha_id,
            "numero_consulta": ficha.numero_consulta,
            "fecha_consulta": ficha.fecha_consulta.isoformat() if ficha.fecha_consulta else None,
            "estado": ficha.estado,
            "motivo_consulta": ficha.motivo_consulta,
        }
        if ficha.paciente_medico:
            item["paciente_medico"] = {
                "paciente_medico_id": ficha.paciente_medico.paciente_medico_id,
                "numero_ficha": ficha.paciente_medico.numero_ficha,
            }
        if ficha.usuario:
            item["usuario"] = {
                "usuario_id": ficha.usuario.usuario_id,
                "nombre": ficha.usuario.nombre,
                "ap_pat": ficha.usuario.ap_pat,
            }
        data.append(item)

    return JsonResponse({"success": True, "data": data})
