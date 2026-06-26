from django.shortcuts import render
from eleicoes_pcd.db_client import get_collection


def dashboard(request):
    """
    Página principal do dashboard.
    Carrega listas de municípios e zonas para os filtros.
    Os dados dos gráficos são carregados via fetch pelo JS (endpoints /api/).
    
    Renomeia _id para nrZona/cdMunicipio pois Django template não acessa _id.
    """
    municipios_raw = list(
        get_collection("municipios").find(
            {}, {"_id": 1, "nmMunicipio": 1}
        ).sort("nmMunicipio", 1)
    )
    # Renomear _id para que o template Django consiga acessar
    municipios = [
        {"cdMunicipio": m["_id"], "nmMunicipio": m["nmMunicipio"]}
        for m in municipios_raw
    ]

    zonas_raw = list(
        get_collection("zonas").find(
            {}, {"_id": 1, "nmSede": 1}
        ).sort("_id", 1)
    )
    zonas = [
        {"nrZona": z["_id"], "nmSede": z.get("nmSede", "")}
        for z in zonas_raw
    ]

    return render(request, "dashboard/index.html", {
        "municipios": municipios,
        "zonas": zonas,
        "turno_ativo": int(request.GET.get("turno", 1)),
    })
