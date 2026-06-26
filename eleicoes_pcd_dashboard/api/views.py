"""
API views — retornam JSON para os gráficos do dashboard.

Estrutura real das coleções (inspecionada):
  perfis:            nrZona, nrSecao, tipo ('PCD'|'NAO_PCD'), dsGenero,
                     dsFaixaEtaria, qtEletoresAptos (sempre 1)
  secoes:            _id={nrZona,nrSecao}, localVotacao.{nmLocalVotacao,dsSituAcessibilidade}
  municipios:        _id=cdMunicipio, nmMunicipio, zonas=[nrZona,...]
  zonas:             _id=nrZona, nmSede, municipios=[cdMunicipio,...]
  comparecimentoZona: _id={nrZona,nrTurno}, qtComparecimento, qtAbstencao,
                      qtComparecimentoDeficiencia, qtAbstencaoDeficiencia
"""

from django.http import JsonResponse
from eleicoes_pcd.db_client import get_collection


# ─── helpers ─────────────────────────────────────────────────────────────────

def _zonas_do_municipio(municipio: str) -> list | None:
    if not municipio:
        return None
    doc = get_collection("municipios").find_one({"nmMunicipio": municipio})
    if doc and doc.get("zonas"):
        return doc["zonas"]
    return []


def _lookup_zonas_nome():
    return {
        "from": "zonas",
        "localField": "_id",
        "foreignField": "_id",
        "as": "_zona",
    }


def _pct_abstencao_geral():
    total = {"$add": ["$_comp.qtAbstencao", "$_comp.qtComparecimento"]}
    return {"$cond": {
        "if": {"$gt": [total, 0]},
        "then": {"$round": [{"$multiply": [{"$divide": ["$_comp.qtAbstencao", total]}, 100]}, 2]},
        "else": None,
    }}


def _pct_abstencao_pcd():
    total = {"$add": ["$_comp.qtAbstencaoDeficiencia", "$_comp.qtComparecimentoDeficiencia"]}
    return {"$cond": {
        "if": {"$gt": [total, 0]},
        "then": {"$round": [{"$multiply": [{"$divide": ["$_comp.qtAbstencaoDeficiencia", total]}, 100]}, 2]},
        "else": None,
    }}


def _lookup_comparecimento(turno: int):
    return {
        "from": "comparecimentoZona",
        "localField": "_id",
        "foreignField": "_id.nrZona",
        "pipeline": [{"$match": {"_id.nrTurno": turno}}],
        "as": "_comp",
    }


# ─── P1 — Subnotificação por município ───────────────────────────────────────

def subnotificacao(request):
    municipio = request.GET.get("municipio", "")
    limit     = min(int(request.GET.get("limit", 20)), 100)

    pipeline = [
        {"$group": {
            "_id": {"nrZona": "$nrZona", "tipo": "$tipo"},
            "count": {"$sum": "$qtEletoresAptos"},
        }},
        {"$lookup": {
            "from": "municipios",
            "localField": "_id.nrZona",
            "foreignField": "zonas",
            "as": "_mun",
        }},
        {"$unwind": {"path": "$_mun", "preserveNullAndEmptyArrays": False}},
        *([{"$match": {"_mun.nmMunicipio": municipio}}] if municipio else []),
        {"$group": {
            "_id": {"cdMunicipio": "$_mun._id", "tipo": "$_id.tipo"},
            "nmMunicipio": {"$first": "$_mun.nmMunicipio"},
            "count": {"$sum": "$count"},
        }},

        {"$group": {
            "_id": "$_id.cdMunicipio",
            "nmMunicipio": {"$first": "$nmMunicipio"},
            "totalPCD":   {"$sum": {"$cond": [{"$eq": ["$_id.tipo", "PCD"]}, "$count", 0]}},
            "totalAptos": {"$sum": "$count"},
        }},
        {"$match": {"totalAptos": {"$gt": 0}}},
        {"$project": {
            "_id": 0,
            "nmMunicipio": 1,
            "totalPCD": {"$multiply": ["$totalPCD", 2]},          # amostra × 2
            "pctPCD": {"$round": [
                {"$multiply": [{"$divide": ["$totalPCD", "$totalAptos"]}, 200]},
                2,
            ]},
        }},
        {"$sort": {"pctPCD": 1}},
        {"$limit": limit},
    ]

    dados = list(get_collection("perfis").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── P2 — Distribuição % PCD por zona ────────────────────────────────────────

def distribuicao_zona(request):
    municipio = request.GET.get("municipio", "")
    zona      = request.GET.get("zona", "")
    limit     = min(int(request.GET.get("limit", 30)), 100)

    match = {}
    if zona:
        try:
            match["nrZona"] = int(zona)
        except ValueError:
            pass

    if municipio:
        zonas_ids = _zonas_do_municipio(municipio)
        if zonas_ids is not None:
            match["nrZona"] = {"$in": zonas_ids}

    pipeline = [
        *([{"$match": match}] if match else []),
        {"$group": {
            "_id": {"nrZona": "$nrZona", "tipo": "$tipo"},
            "count": {"$sum": "$qtEletoresAptos"},
        }},
        {"$group": {
            "_id": "$_id.nrZona",
            "totalPCD":   {"$sum": {"$cond": [{"$eq": ["$_id.tipo", "PCD"]}, "$count", 0]}},
            "totalAptos": {"$sum": "$count"},
        }},
        {"$match": {"totalAptos": {"$gt": 0}}},
        {"$lookup": _lookup_zonas_nome()},
        {"$project": {
            "_id": 0,
            "nrZona": "$_id",
            "nmSede": {"$ifNull": [{"$first": "$_zona.nmSede"}, ""]},
            "pctPCD": {"$round": [
                {"$multiply": [{"$divide": ["$totalPCD", "$totalAptos"]}, 200]},
                2,
            ]},
        }},
        {"$sort": {"pctPCD": -1}},
        {"$limit": limit},
    ]

    dados = list(get_collection("perfis").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── P3 — Abstenção × concentração PCD (scatter) ─────────────────────────────

def abstencao_vs_pcd(request):
    turno     = int(request.GET.get("turno", 1))
    municipio = request.GET.get("municipio", "")
    zona      = request.GET.get("zona", "")

    match = {}
    if zona:
        try:
            match["nrZona"] = int(zona)
        except ValueError:
            pass
    if municipio:
        zonas_ids = _zonas_do_municipio(municipio)
        if zonas_ids is not None:
            match["nrZona"] = {"$in": zonas_ids}

    pipeline = [
        *([{"$match": match}] if match else []),
        {"$group": {
            "_id": {"nrZona": "$nrZona", "tipo": "$tipo"},
            "count": {"$sum": "$qtEletoresAptos"},
        }},
        {"$group": {
            "_id": "$_id.nrZona",
            "totalPCD":   {"$sum": {"$cond": [{"$eq": ["$_id.tipo", "PCD"]}, "$count", 0]}},
            "totalAptos": {"$sum": "$count"},
        }},
        {"$match": {"totalAptos": {"$gt": 0}}},
        {"$lookup": _lookup_comparecimento(turno)},
        {"$lookup": _lookup_zonas_nome()},
        {"$unwind": {"path": "$_comp", "preserveNullAndEmptyArrays": True}},
        {"$project": {
            "_id": 0,
            "nrZona": "$_id",
            "nmSede": {"$ifNull": [{"$first": "$_zona.nmSede"}, ""]},
            "pctPCD": {"$round": [
                {"$multiply": [{"$divide": ["$totalPCD", "$totalAptos"]}, 200]},
                2,
            ]},
            "pctAbstencao":    _pct_abstencao_geral(),
            "pctAbstencaoPCD": _pct_abstencao_pcd(),
        }},
        {"$sort": {"nrZona": 1}},
    ]

    dados = list(get_collection("perfis").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── P4 — Abstenção PCD vs geral por zona ────────────────────────────────────

def pcd_obrigatorio(request):
    turno     = int(request.GET.get("turno", 1))
    municipio = request.GET.get("municipio", "")
    zona      = request.GET.get("zona", "")

    match = {"_id.nrTurno": turno}
    if zona:
        try:
            match["_id.nrZona"] = int(zona)
        except ValueError:
            pass

    pipeline = [
        {"$match": match},
        *([
            {"$lookup": {
                "from": "municipios",
                "localField": "_id.nrZona",
                "foreignField": "zonas",
                "as": "_mun",
            }},
            {"$unwind": {"path": "$_mun", "preserveNullAndEmptyArrays": False}},
            {"$match": {"_mun.nmMunicipio": municipio}},
        ] if municipio else []),
        {"$lookup": {
            "from": "zonas",
            "localField": "_id.nrZona",
            "foreignField": "_id",
            "as": "_zona",
        }},
        {"$project": {
            "_id": 0,
            "nrZona": "$_id.nrZona",
            "nmSede": {"$ifNull": [{"$first": "$_zona.nmSede"}, ""]},
            "pctAbstencaoGeral": {"$round": [
                {"$multiply": [
                    {"$divide": [
                        "$qtAbstencao",
                        {"$add": ["$qtAbstencao", "$qtComparecimento"]},
                    ]},
                    100,
                ]}, 2,
            ]},
            "pctAbstencaoPCD": {"$cond": {
                "if": {"$gt": [
                    {"$add": [
                        {"$ifNull": ["$qtAbstencaoDeficiencia", 0]},
                        {"$ifNull": ["$qtComparecimentoDeficiencia", 0]},
                    ]},
                    0,
                ]},
                "then": {"$round": [
                    {"$multiply": [
                        {"$divide": [
                            "$qtAbstencaoDeficiencia",
                            {"$add": ["$qtAbstencaoDeficiencia", "$qtComparecimentoDeficiencia"]},
                        ]},
                        100,
                    ]}, 2,
                ]},
                "else": 0,
            }},
        }},
        {"$sort": {"nrZona": 1}},
    ]

    dados = list(get_collection("comparecimentoZona").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── P5 — Perfil demográfico: faixa etária × gênero ─────────────────────────

def perfil_demografico(request):
    municipio = request.GET.get("municipio", "")
    zona      = request.GET.get("zona", "")

    match = {"tipo": "PCD"}
    if zona:
        try:
            match["nrZona"] = int(zona)
        except ValueError:
            pass
    if municipio:
        zonas_ids = _zonas_do_municipio(municipio)
        if zonas_ids is not None:
            match["nrZona"] = {"$in": zonas_ids}

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": {
                "faixaEtaria": "$dsFaixaEtaria",
                "genero":      "$dsGenero",
            },
            "totalPCD": {"$sum": {"$multiply": ["$qtEletoresAptos", 2]}},
        }},
        {"$match": {
            "_id.faixaEtaria": {"$ne": None},
            "_id.genero":      {"$ne": None},
        }},
        {"$project": {
            "_id": 0,
            "faixaEtaria": "$_id.faixaEtaria",
            "genero":      "$_id.genero",
            "totalPCD":    1,
        }},
        {"$sort": {"faixaEtaria": 1, "genero": 1}},
    ]

    dados = list(get_collection("perfis").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── P6 — Locais de votação com mais PCD (tabela) ────────────────────────────

def locais_votacao(request):
    municipio      = request.GET.get("municipio", "")
    zona           = request.GET.get("zona", "")
    acessibilidade = request.GET.get("acessibilidade", "")
    limit          = min(int(request.GET.get("limit", 50)), 200)

    match = {"tipo": "PCD"}
    if zona:
        try:
            match["nrZona"] = int(zona)
        except ValueError:
            pass
    if municipio:
        zonas_ids = _zonas_do_municipio(municipio)
        if zonas_ids is not None:
            match["nrZona"] = {"$in": zonas_ids}

    buffer = limit * 4 if acessibilidade else limit

    grupos = list(get_collection("perfis").aggregate([
        {"$match": match},
        {"$group": {
            "_id": {"nrZona": "$nrZona", "nrSecao": "$nrSecao"},
            "totalPCD": {"$sum": {"$multiply": ["$qtEletoresAptos", 2]}},
        }},
        {"$sort": {"totalPCD": -1}},
        {"$limit": buffer},
    ]))

    if not grupos:
        return JsonResponse({"dados": []})

    secao_ids = [{"nrZona": g["_id"]["nrZona"], "nrSecao": g["_id"]["nrSecao"]} for g in grupos]
    secoes_map = {
        (s["_id"]["nrZona"], s["_id"]["nrSecao"]): s.get("localVotacao", {})
        for s in get_collection("secoes").find({"_id": {"$in": secao_ids}})
    }

    zonas_nos_resultados = list({g["_id"]["nrZona"] for g in grupos})
    municipio_por_zona = {}
    for m in get_collection("municipios").find(
        {"zonas": {"$elemMatch": {"$in": zonas_nos_resultados}}},
        {"nmMunicipio": 1, "zonas": 1},
    ):
        for z in m.get("zonas", []):
            if z in zonas_nos_resultados:
                municipio_por_zona[z] = m["nmMunicipio"]

    dados = []
    for g in grupos:
        nrZona  = g["_id"]["nrZona"]
        nrSecao = g["_id"]["nrSecao"]
        lv = secoes_map.get((nrZona, nrSecao), {})
        ds = lv.get("dsSituAcessibilidade", "") or ""

        if acessibilidade == "sim" and ds.lower().startswith("sem"):
            continue
        if acessibilidade == "nao" and not ds.lower().startswith("sem"):
            continue

        dados.append({
            "nrZona":               nrZona,
            "nrSecao":              nrSecao,
            "nmMunicipio":          municipio_por_zona.get(nrZona, ""),
            "nmLocalVotacao":       lv.get("nmLocalVotacao", ""),
            "totalPCD":             g["totalPCD"],
            "dsSituAcessibilidade": ds,
        })

        if len(dados) >= limit:
            break

    return JsonResponse({"dados": dados})


# ─── P7 — Abstenção PCD por porte de município ───────────────────────────────

def porte_municipio(request):
    turno = int(request.GET.get("turno", 1))

    pipeline = [
        {"$project": {"_id": 1, "nmMunicipio": 1, "zonas": 1}},
        {"$unwind": "$zonas"},
        {"$lookup": {
            "from": "comparecimentoZona",
            "let": {"zona": "$zonas"},
            "pipeline": [{"$match": {"$expr": {
                "$and": [
                    {"$eq": ["$_id.nrZona",   "$$zona"]},
                    {"$eq": ["$_id.nrTurno",  turno]},
                ],
            }}}],
            "as": "_comp",
        }},
        {"$unwind": {"path": "$_comp", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": "$_id",
            "qtAptos": {"$sum": {"$add": [
                {"$ifNull": ["$_comp.qtAbstencao",      0]},
                {"$ifNull": ["$_comp.qtComparecimento", 0]},
            ]}},
            "qtAbstencaoPCD":      {"$sum": {"$ifNull": ["$_comp.qtAbstencaoDeficiencia",       0]}},
            "qtComparecimentoPCD": {"$sum": {"$ifNull": ["$_comp.qtComparecimentoDeficiencia",  0]}},
        }},
        {"$addFields": {
            "porte": {"$cond": {
                "if": {"$gte": ["$qtAptos", 50000]},
                "then": "grande",
                "else": "pequeno",
            }},
        }},
        {"$group": {
            "_id":              "$porte",
            "qtMunicipios":     {"$addToSet": "$_id"},
            "qtAbstencaoPCD":   {"$sum": "$qtAbstencaoPCD"},
            "qtTotalPCD": {"$sum": {"$add": ["$qtAbstencaoPCD", "$qtComparecimentoPCD"]}},
        }},
        {"$project": {
            "_id": 0,
            "porte":          "$_id",
            "qtMunicipios":   {"$size": "$qtMunicipios"},
            "qtAbstencaoPCD": 1,
            "pctAbstencaoPCD": {"$cond": {
                "if": {"$gt": ["$qtTotalPCD", 0]},
                "then": {"$round": [
                    {"$multiply": [{"$divide": ["$qtAbstencaoPCD", "$qtTotalPCD"]}, 100]},
                    2,
                ]},
                "else": 0,
            }},
        }},
        {"$sort": {"porte": -1}},
    ]

    dados = list(get_collection("municipios").aggregate(pipeline))
    return JsonResponse({"dados": dados})


# ─── Auxiliar — Zonas por município ─────────────────────────────────────────

def zonas_por_municipio(request):
    municipio = request.GET.get("municipio", "")
    if not municipio:
        return JsonResponse({"dados": []})

    mun = get_collection("municipios").find_one({"nmMunicipio": municipio})
    if not mun or not mun.get("zonas"):
        return JsonResponse({"dados": []})

    zonas = list(
        get_collection("zonas")
        .find({"_id": {"$in": mun["zonas"]}}, {"_id": 1, "nmSede": 1})
        .sort("_id", 1)
    )

    dados = [{"nrZona": z["_id"], "nmSede": z.get("nmSede", "")} for z in zonas]
    return JsonResponse({"dados": dados})