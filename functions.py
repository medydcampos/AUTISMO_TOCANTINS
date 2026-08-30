from __future__ import annotations

import os
import sys
import webbrowser
from pathlib import Path
from typing import Literal

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DADOS_BREAKDOWN = BASE_DIR / "dados_quant" / "dados_limpos_breakdown.csv"
# Visao_Monocular nao existe no CENSO 2021–2022; permanece NA nesses anos.
COLUNA_SEM_DADO_PRE_2023 = "Visao_Monocular"
OUTPUT_DIR = BASE_DIR / "OUTPUT"
MPLCONFIGDIR = BASE_DIR / ".matplotlib_cache"
OUTPUT_DIR.mkdir(exist_ok=True)
MPLCONFIGDIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPLCONFIGDIR))

if "ipykernel" not in sys.modules:
    os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib.pyplot as plt


PlotTipo = Literal[
    "visualizar_deficiencia",
    "compara_anos",
    "compara_deficiencias",
]
SaidaTipo = Literal["console", "grafico"]
LogicaCategoriasTipo = Literal["coluna_simples", "hierarquia", "subdominio_detalhado"]


# Funcao: carregar dados de breakdown
def carregar_dados_breakdown(caminho_dados: str | Path = DADOS_BREAKDOWN) -> pd.DataFrame:
    df = pd.read_csv(caminho_dados, sep=";")
    df.columns = df.columns.str.strip()

    for coluna in ["Municipio", "Zona_Breakdown", "Dependencia_Administrativa"]:
        df[coluna] = df[coluna].astype(str).str.strip()

    for coluna in selecionar_colunas_deficiencia(df):
        valores = pd.to_numeric(df[coluna], errors="coerce")
        if coluna != COLUNA_SEM_DADO_PRE_2023:
            valores = valores.fillna(0)
        df[coluna] = valores

    return df


# Funcao: selecionar colunas de deficiencia
def selecionar_colunas_deficiencia(df: pd.DataFrame) -> list[str]:
    return list(df.columns[4:])


# Funcao auxiliar: resolver valor informado pelo usuario
def _resolver_valor(valor: str, opcoes: list[str], nome: str) -> str:
    mapa = {str(opcao).strip().lower(): opcao for opcao in opcoes}
    chave = str(valor).strip().lower()

    if chave not in mapa:
        raise ValueError(f"{nome} invalido: {valor}. Opcoes: {opcoes}")

    return mapa[chave]


# Funcao auxiliar: resolver uma ou mais deficiencias
def _resolver_deficiencias(
    df: pd.DataFrame,
    deficiencia: str | list[str] | tuple[str, ...],
) -> list[str]:
    opcoes = selecionar_colunas_deficiencia(df)

    if isinstance(deficiencia, str):
        deficiencias = [deficiencia]
    else:
        deficiencias = list(deficiencia)

    return [_resolver_valor(item, opcoes, "Deficiencia") for item in deficiencias]


# Funcao auxiliar: resolver tipo de plotagem
def _resolver_plot(
    plot: PlotTipo,
    compara_anos: bool,
    compara_deficiencias: bool,
) -> PlotTipo:
    modos = []

    if compara_anos:
        modos.append("compara_anos")

    if compara_deficiencias:
        modos.append("compara_deficiencias")

    if len(modos) > 1:
        raise ValueError("Escolha apenas uma opcao: compara_anos ou compara_deficiencias.")

    if modos:
        if plot != "visualizar_deficiencia" and plot != modos[0]:
            raise ValueError(f"Conflito entre plot={plot} e {modos[0]}=True.")
        return modos[0]

    return plot


# Funcao auxiliar: filtrar base por ano, zona e dependencia
def _filtrar_base(
    df: pd.DataFrame,
    ano: int,
    zona_breakdown: str,
    dependencia_administrativa_breakdown: str,
) -> pd.DataFrame:
    zona = _resolver_valor(
        zona_breakdown,
        sorted(df["Zona_Breakdown"].dropna().unique()),
        "Zona_Breakdown",
    )
    dependencia = _resolver_valor(
        dependencia_administrativa_breakdown,
        sorted(df["Dependencia_Administrativa"].dropna().unique()),
        "Dependencia_Administrativa",
    )

    filtro = (
        (df["Ano"] == ano)
        & (df["Zona_Breakdown"] == zona)
        & (df["Dependencia_Administrativa"] == dependencia)
    )

    filtrado = df.loc[filtro].copy()

    if filtrado.empty:
        raise ValueError(
            "Nenhuma linha encontrada para "
            f"ano={ano}, zona={zona}, dependencia={dependencia}."
        )

    return filtrado


# Funcao auxiliar: resolver lista de dependencias administrativas
def _resolver_dependencias(
    df: pd.DataFrame,
    dependencia_administrativa_breakdown: str | list[str] | tuple[str, ...],
) -> list[str]:
    opcoes = sorted(df["Dependencia_Administrativa"].dropna().unique())

    if isinstance(dependencia_administrativa_breakdown, str):
        dependencias = [
            dependencia.strip()
            for dependencia in dependencia_administrativa_breakdown.split(",")
            if dependencia.strip()
        ]
    else:
        dependencias = list(dependencia_administrativa_breakdown)

    dependencias_resolvidas = [
        _resolver_valor(dependencia, opcoes, "Dependencia_Administrativa")
        for dependencia in dependencias
    ]

    if len(dependencias_resolvidas) > 1 and "Total" in dependencias_resolvidas:
        raise ValueError(
            "Nao combine 'Total' com outras dependencias administrativas, "
            "pois isso duplicaria a contagem."
        )

    return dependencias_resolvidas


# Funcao auxiliar: filtrar/agregar base para estatisticas descritivas
def _filtrar_base_estatisticas(
    df: pd.DataFrame,
    ano: int,
    zona_breakdown: str,
    dependencia_administrativa_breakdown: str | list[str] | tuple[str, ...],
    colunas_valores: list[str],
) -> pd.DataFrame:
    zona = _resolver_valor(
        zona_breakdown,
        sorted(df["Zona_Breakdown"].dropna().unique()),
        "Zona_Breakdown",
    )
    dependencias = _resolver_dependencias(df, dependencia_administrativa_breakdown)

    filtro = (
        (df["Ano"] == ano)
        & (df["Zona_Breakdown"] == zona)
        & (df["Dependencia_Administrativa"].isin(dependencias))
    )

    filtrado = df.loc[filtro, ["Municipio", *colunas_valores]].copy()

    if filtrado.empty:
        raise ValueError(
            "Nenhuma linha encontrada para "
            f"ano={ano}, zona={zona}, dependencia={dependencias}."
        )

    if len(dependencias) > 1:
        filtrado = (
            filtrado.groupby("Municipio", as_index=False)[colunas_valores]
            .sum(min_count=1)
            .sort_values("Municipio")
        )

    return filtrado


# Funcao auxiliar: calcular estatisticas descritivas
def _calcular_estatisticas(serie: pd.Series) -> pd.Series:
    serie_num = pd.to_numeric(serie, errors="coerce")
    n_municipios = int(serie_num.size)

    if serie_num.isna().all():
        vazio = float("nan")
        return pd.Series(
            {
                "Municipios": n_municipios,
                "Total": vazio,
                "Media": vazio,
                "Desvio padrao": vazio,
                "Minimo": vazio,
                "P25": vazio,
                "Mediana": vazio,
                "P75": vazio,
                "Maximo": vazio,
                "Assimetria": vazio,
                "Curtose": vazio,
                "Municipios com zero": vazio,
                "Municipios com valor": vazio,
            }
        )

    serie = serie_num.dropna()

    return pd.Series(
        {
            "Municipios": serie.count(),
            "Total": serie.sum(),
            "Media": serie.mean(),
            "Desvio padrao": serie.std(),
            "Minimo": serie.min(),
            "P25": serie.quantile(0.25),
            "Mediana": serie.median(),
            "P75": serie.quantile(0.75),
            "Maximo": serie.max(),
            "Assimetria": serie.skew(),
            "Curtose": serie.kurt(),
            "Municipios com zero": (serie == 0).sum(),
            "Municipios com valor": (serie > 0).sum(),
        }
    )


# Funcao auxiliar: formatar numeros em padrao brasileiro
def _formatar_numero(valor: float) -> str:
    if pd.isna(valor):
        return ""

    if float(valor).is_integer():
        return f"{int(valor):,}".replace(",", ".")

    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Funcao auxiliar: formatar tabela
def _formatar_tabela(tabela: pd.DataFrame) -> pd.DataFrame:
    return tabela.map(_formatar_numero)


# Funcao auxiliar: formatar parametros para texto
def _formatar_parametro_texto(valor: str | list[str] | tuple[str, ...]) -> str:
    if isinstance(valor, str):
        return valor

    return ", ".join(str(item) for item in valor)


# Funcao auxiliar: plotar tabela como figura
def _plotar_tabela(tabela: pd.DataFrame, titulo: str, ax) -> None:
    ax.axis("off")
    ax.set_title(titulo, fontsize=12, fontweight="bold", pad=12)

    tabela_formatada = _formatar_tabela(tabela)
    table = ax.table(
        cellText=tabela_formatada.values,
        rowLabels=tabela_formatada.index,
        colLabels=tabela_formatada.columns,
        loc="center",
        cellLoc="center",
        rowLoc="left",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.25)


# Funcao auxiliar: verificar disponibilidade de display interativo
def _display_disponivel() -> bool:
    return "ipykernel" in sys.modules


# Funcao auxiliar: interpretar valor de assimetria
def _interpretar_assimetria(valor: float) -> str:
    if pd.isna(valor):
        return "nao foi possivel calcular a assimetria."

    intensidade = "baixa"
    if abs(valor) >= 1:
        intensidade = "forte"
    elif abs(valor) >= 0.5:
        intensidade = "moderada"

    if abs(valor) < 0.5:
        return "aproximadamente simetrica."

    if valor > 0:
        return (
            f"positiva {intensidade}; distribuicao assimetrica a direita, "
            "com cauda alongada para valores mais altos."
        )

    return (
        f"negativa {intensidade}; distribuicao assimetrica a esquerda, "
        "com cauda alongada para valores mais baixos."
    )


# Funcao auxiliar: interpretar valor de curtose
def _interpretar_curtose(valor: float) -> str:
    if pd.isna(valor):
        return "nao foi possivel calcular a curtose."

    if abs(valor) < 0.5:
        return (
            "proxima de zero; formato semelhante ao de uma distribuicao normal "
            "em termos de peso das caudas."
        )

    if valor > 0:
        intensidade = "elevada" if valor >= 3 else "positiva"
        return (
            f"{intensidade}; distribuicao leptocurtica, com caudas mais pesadas "
            "que a normal e maior presenca de valores extremos."
        )

    return (
        "negativa; distribuicao platicurtica, com caudas mais leves que a normal "
        "e menor presenca de valores extremos."
    )


# Funcao auxiliar: criar nota interpretativa de assimetria e curtose
def _criar_nota_interpretativa(tabela: pd.DataFrame) -> list[str]:
    if "Assimetria" not in tabela.index or "Curtose" not in tabela.index:
        return []

    notas = []
    for coluna in tabela.columns:
        assimetria = tabela.loc["Assimetria", coluna]
        curtose = tabela.loc["Curtose", coluna]
        notas.append(
            f"{coluna}: Assimetria = {_formatar_numero(assimetria)} "
            f"({_interpretar_assimetria(assimetria)}) "
            f"Curtose/kurtosis = {_formatar_numero(curtose)} "
            f"({_interpretar_curtose(curtose)})"
        )

    return notas


# Funcao auxiliar: mostrar tabela no console ou notebook
def _mostrar_tabela_console(
    titulo: str,
    tabela: pd.DataFrame,
    nota_interpretativa: bool = True,
) -> None:
    tabela_formatada = _formatar_tabela(tabela)
    notas = _criar_nota_interpretativa(tabela) if nota_interpretativa else []

    if _display_disponivel():
        from IPython.display import Markdown, display

        display(Markdown(f"### {titulo}"))
        display(tabela_formatada)
        if notas:
            linhas = "\n".join(f"- {nota}" for nota in notas)
            display(
                Markdown(
                    "**Nota interpretativa:** a curtose/kurtosis reportada e o "
                    "excesso de curtose calculado pelo pandas; uma distribuicao "
                    f"normal tem valor proximo de 0.\n\n{linhas}"
                )
            )
        return

    print(f"\n{titulo}")
    print(tabela_formatada.to_string())
    if notas:
        print("\nNota interpretativa:")
        print(
            "A curtose/kurtosis reportada e o excesso de curtose calculado pelo "
            "pandas; uma distribuicao normal tem valor proximo de 0."
        )
        for nota in notas:
            print(f"- {nota}")


# Funcao auxiliar: mostrar conjunto de tabelas
def _mostrar_resultado_console(
    tabelas_tituladas: list[tuple[str, pd.DataFrame]],
    nota_interpretativa: bool = True,
) -> None:
    for titulo, tabela in tabelas_tituladas:
        _mostrar_tabela_console(titulo, tabela, nota_interpretativa)


# Funcao auxiliar: criar nome do arquivo HTML
def _nome_arquivo_html(modo: str, deficiencias: list[str], anos: list[int]) -> str:
    partes = [modo, *deficiencias, *[str(ano) for ano in anos]]
    nome = "_".join(partes).lower()
    nome = "".join(caractere if caractere.isalnum() else "_" for caractere in nome)
    nome = "_".join(parte for parte in nome.split("_") if parte)
    return f"tabela_abnt_{nome}.html"


# Funcao auxiliar: converter tabela para HTML
def _tabela_para_html(tabela: pd.DataFrame) -> str:
    tabela_formatada = _formatar_tabela(tabela).reset_index()
    tabela_formatada = tabela_formatada.rename(columns={"index": "Estatistica"})

    return tabela_formatada.to_html(
        index=False,
        border=0,
        classes="abnt-table",
        escape=False,
    )


# Funcao auxiliar: converter nota interpretativa para HTML
def _nota_interpretativa_para_html(tabela: pd.DataFrame) -> str:
    notas = _criar_nota_interpretativa(tabela)

    if not notas:
        return ""

    itens = "".join(f"<li>{nota}</li>" for nota in notas)
    return f"""
    <div class="note">
        <p><strong>Nota interpretativa:</strong> a curtose/kurtosis reportada e o
        excesso de curtose calculado pelo pandas; uma distribuicao normal tem
        valor proximo de 0.</p>
        <ul>{itens}</ul>
    </div>
    """


# Funcao auxiliar: gerar HTML em estilo ABNT
def _gerar_html_abnt(
    tabelas_tituladas: list[tuple[str, pd.DataFrame]],
    caminho_html: str | Path | None,
    modo: str,
    deficiencias: list[str],
    anos: list[int],
    zona_breakdown: str,
    dependencia_administrativa_breakdown: str,
    nota_interpretativa: bool = True,
) -> Path:
    if caminho_html is None:
        caminho_html = OUTPUT_DIR / _nome_arquivo_html(modo, deficiencias, anos)
    else:
        caminho_html = Path(caminho_html)

    tabelas_html = []
    for indice, (titulo, tabela) in enumerate(tabelas_tituladas, start=1):
        tabelas_html.append(
            f"""
            <section class="table-block">
                <p class="table-title">Tabela {indice} - {titulo}</p>
                {_tabela_para_html(tabela)}
                {_nota_interpretativa_para_html(tabela) if nota_interpretativa else ""}
                <p class="source">Fonte: Elaboracao propria a partir de dados educacionais.</p>
            </section>
            """
        )

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Tabelas ABNT</title>
    <style>
        body {{
            background: #f5f5f5;
            color: #111;
            font-family: Arial, Helvetica, sans-serif;
            margin: 0;
            padding: 32px;
        }}
        main {{
            background: white;
            margin: 0 auto;
            max-width: 900px;
            padding: 48px;
        }}
        h1 {{
            font-size: 16px;
            margin: 0 0 24px;
            text-align: center;
            text-transform: uppercase;
        }}
        .meta {{
            font-size: 12px;
            margin-bottom: 28px;
        }}
        .table-block {{
            margin-bottom: 32px;
        }}
        .table-title {{
            font-size: 12px;
            margin: 0 0 8px;
            text-align: left;
        }}
        table.abnt-table {{
            border-collapse: collapse;
            border-top: 1px solid #111;
            border-bottom: 1px solid #111;
            font-size: 12px;
            margin: 0;
            width: 100%;
        }}
        table.abnt-table thead tr {{
            border-bottom: 1px solid #111;
        }}
        table.abnt-table th,
        table.abnt-table td {{
            padding: 6px 8px;
            text-align: right;
            vertical-align: middle;
        }}
        table.abnt-table th:first-child,
        table.abnt-table td:first-child {{
            text-align: left;
        }}
        .source {{
            font-size: 11px;
            margin: 6px 0 0;
        }}
        .note {{
            font-size: 11px;
            margin: 8px 0 0;
        }}
        .note p {{
            margin: 0 0 4px;
        }}
        .note ul {{
            margin: 0;
            padding-left: 18px;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            main {{
                box-shadow: none;
                max-width: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <main>
        <h1>Tabelas de estatisticas descritivas</h1>
        <p class="meta">
            Zona: {zona_breakdown} | Dependencia administrativa: {dependencia_administrativa_breakdown}
        </p>
        {"".join(tabelas_html)}
    </main>
</body>
</html>
"""

    caminho_html.parent.mkdir(parents=True, exist_ok=True)
    caminho_html.write_text(html, encoding="utf-8")
    return caminho_html


############# Funcao: plotar estatisticas descritivas ###############

def plotar_estatisticas_descritivas(
    deficiencia: str | list[str] | tuple[str, ...],
    ano: int = 2023,
    anos: list[int] | tuple[int, ...] | None = None,
    plot: PlotTipo = "visualizar_deficiencia",
    compara_anos: bool = False,
    compara_deficiencias: bool = False,
    zona_breakdown: str = "Total",
    dependencia_administrativa_breakdown: str | list[str] | tuple[str, ...] = "Total",
    caminho_dados: str | Path = DADOS_BREAKDOWN,
    mostrar: bool = True,
    saida: SaidaTipo = "console",
    extracao: bool = False,
    caminho_html: str | Path | None = None,
    abrir_html: bool = True,
    nota_interpretativa: bool = True,
):
    df = carregar_dados_breakdown(caminho_dados)
    modo = _resolver_plot(plot, compara_anos, compara_deficiencias)
    deficiencias = _resolver_deficiencias(df, deficiencia)
    tabelas_tituladas = []
    fig = None

    if modo == "visualizar_deficiencia":
        if len(deficiencias) != 1:
            raise ValueError("Use apenas uma deficiencia em visualizar_deficiencia.")

        base = _filtrar_base_estatisticas(
            df, ano, zona_breakdown, dependencia_administrativa_breakdown, deficiencias
        )
        tabela = _calcular_estatisticas(base[deficiencias[0]]).to_frame(deficiencias[0])
        tabelas_tituladas.append((f"{deficiencias[0]} - {ano}", tabela))
        anos_analise = [ano]

    elif modo == "compara_anos":
        if len(deficiencias) != 1:
            raise ValueError("Use apenas uma deficiencia em compara_anos.")

        anos = list(anos) if anos is not None else [2023, 2024, 2025]

        if len(anos) < 2:
            raise ValueError("compara_anos requer pelo menos dois anos.")

        estatisticas_por_ano = {}
        for ano_item in anos:
            base = _filtrar_base_estatisticas(
                df,
                ano_item,
                zona_breakdown,
                dependencia_administrativa_breakdown,
                deficiencias,
            )
            estatisticas_por_ano[str(ano_item)] = _calcular_estatisticas(
                base[deficiencias[0]]
            )

        tabela = pd.concat(estatisticas_por_ano, axis=1)
        tabelas_tituladas = [(f"{deficiencias[0]} - comparacao entre anos", tabela)]
        anos_analise = [int(ano_item) for ano_item in anos]

    elif modo == "compara_deficiencias":
        if len(deficiencias) < 2:
            raise ValueError("Use duas ou mais deficiencias em compara_deficiencias.")

        base = _filtrar_base_estatisticas(
            df, ano, zona_breakdown, dependencia_administrativa_breakdown, deficiencias
        )

        tabela = pd.concat(
            {coluna: _calcular_estatisticas(base[coluna]) for coluna in deficiencias},
            axis=1,
        )
        tabelas_tituladas.append((f"Comparacao de deficiencias - {ano}", tabela))
        anos_analise = [ano]

    else:
        raise ValueError(f"Plot invalido: {modo}")

    if saida == "console":
        if mostrar:
            _mostrar_resultado_console(tabelas_tituladas, nota_interpretativa)
    elif saida == "grafico":
        n_colunas = tabelas_tituladas[0][1].shape[1]
        largura = max(6, 1.6 * n_colunas + 3.5)
        if modo == "compara_anos":
            fig, axes = plt.subplots(
                1, len(tabelas_tituladas), figsize=(largura * len(tabelas_tituladas), 4.8)
            )
            axes = [axes] if len(tabelas_tituladas) == 1 else axes

            for ax, (titulo, tabela_plot) in zip(axes, tabelas_tituladas):
                _plotar_tabela(tabela_plot, titulo, ax)
        else:
            if modo == "compara_deficiencias":
                largura = 2.4 * len(deficiencias) + 4

            fig, ax = plt.subplots(figsize=(largura, 4.8))
            _plotar_tabela(tabelas_tituladas[0][1], tabelas_tituladas[0][0], ax)

        fig.tight_layout()

        if mostrar:
            plt.show()
    else:
        raise ValueError("saida deve ser 'console' ou 'grafico'.")

    if extracao:
        caminho_html_gerado = _gerar_html_abnt(
            tabelas_tituladas=tabelas_tituladas,
            caminho_html=caminho_html,
            modo=modo,
            deficiencias=deficiencias,
            anos=anos_analise,
            zona_breakdown=zona_breakdown,
            dependencia_administrativa_breakdown=_formatar_parametro_texto(
                dependencia_administrativa_breakdown
            ),
            nota_interpretativa=nota_interpretativa,
        )

        if abrir_html:
            webbrowser.open(caminho_html_gerado.resolve().as_uri())

        if mostrar:
            print(f"\nTabela ABNT salva em: {caminho_html_gerado}")

    return tabela, fig


################# Funcao: plotar histograma de matriculas por municipio #################

def plotar_histograma_matriculas(
    deficiencia: str,
    ano: int,
    zona_breakdown: str = "Total",
    dependencia_administrativa_breakdown: str = "Total",
    caminho_dados: str | Path = DADOS_BREAKDOWN,
    bins: int | str = "auto",
    bin_width: int | float | None = None,
    titulo: str | None = None,
    densidade: bool = False,
    plot_densidades: bool = False,
    anos: list[int] | tuple[int, ...] | None = None,
    xlim_max: int | float | None = None,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    df = carregar_dados_breakdown(caminho_dados)
    deficiencias = _resolver_deficiencias(df, deficiencia)

    if len(deficiencias) != 1:
        raise ValueError("Use apenas uma deficiencia para criar o histograma.")

    deficiencia = deficiencias[0]

    if plot_densidades:
        if anos is None:
            raise ValueError("Quando plot_densidades=True, informe anos=[...].")

        anos_plotagem = list(anos)

        if not 1 <= len(anos_plotagem) <= 3:
            raise ValueError("plot_densidades permite comparar de 1 ate 3 anos.")

        densidade = True
    else:
        if anos is not None:
            raise ValueError("Use anos=[...] apenas quando plot_densidades=True.")

        anos_plotagem = [ano]

    dados_por_ano = []
    for ano_item in anos_plotagem:
        base = _filtrar_base(
            df,
            ano=ano_item,
            zona_breakdown=zona_breakdown,
            dependencia_administrativa_breakdown=dependencia_administrativa_breakdown,
        )

        dados_ano = (
            base[["Municipio", deficiencia]]
            .rename(columns={deficiencia: "Matriculas"})
            .sort_values("Municipio")
            .reset_index(drop=True)
        )
        dados_ano["Ano"] = ano_item
        dados_por_ano.append(dados_ano)

    dados_histograma = pd.concat(dados_por_ano, ignore_index=True)

    if not plot_densidades:
        dados_histograma = dados_histograma.drop(columns="Ano")

    valores = dados_histograma["Matriculas"]
    if titulo is None and not plot_densidades:
        titulo = f"Distribuicao municipal das matriculas - {deficiencia} ({anos_plotagem[0]})"
    elif titulo is None:
        anos_titulo = ", ".join(str(ano_item) for ano_item in anos_plotagem)
        titulo = f"Densidade municipal das matriculas - {deficiencia} ({anos_titulo})"

    if bin_width is not None:
        if bin_width <= 0:
            raise ValueError("bin_width deve ser maior que zero.")

        limite_inferior = 0
        limite_superior = ((valores.max() // bin_width) + 1) * bin_width

        if limite_inferior == limite_superior:
            limite_superior = limite_inferior + bin_width

        bins = []
        limite_atual = limite_inferior
        while limite_atual <= limite_superior:
            bins.append(limite_atual)
            limite_atual += bin_width

    try:
        import seaborn as sns

        sns.set_theme(
            context="paper",
            style="ticks",
            font="Times New Roman",
            palette="deep",
        )
    except ImportError:
        sns = None

    if densidade and sns is None:
        raise ImportError("densidade=True requer a biblioteca seaborn.")

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    if plot_densidades:
        estilos_linha = ["-", "--", ":", "-."]

        for indice, ano_item in enumerate(anos_plotagem):
            valores_ano = dados_histograma.loc[
                dados_histograma["Ano"] == ano_item, "Matriculas"
            ]
            sns.kdeplot(
                valores_ano,
                cut=0,
                clip=(0, None),
                color="#C76E6E",
                linewidth=1.6,
                linestyle=estilos_linha[indice % len(estilos_linha)],
                label=str(ano_item),
                ax=ax,
            )
    elif sns is not None:
        sns.histplot(
            valores,
            bins=bins,
            stat="density" if densidade else "count",
            kde=densidade,
            kde_kws={"cut": 0, "clip": (0, None)},
            line_kws={"color": "#C76E6E", "linewidth": 1.6},
            color="#91a8b8",
            edgecolor="white",
            linewidth=0.8,
            alpha=0.88,
            ax=ax,
        )
    else:
        ax.hist(
            valores,
            bins=bins,
            density=densidade,
            color="#91a8b8",
            edgecolor="white",
            linewidth=0.8,
            alpha=0.88,
        )

    if densidade:
        for linha in ax.lines:
            linha.set_color("#C76E6E")
            linha.set_linewidth(1.6)

    ax.set_title(
        titulo,
        fontfamily="Times New Roman",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Matriculas por municipio", fontfamily="Times New Roman")
    rotulo_y = "Densidade" if densidade else "Quantidade de municipios"
    ax.set_ylabel(rotulo_y, fontfamily="Times New Roman")
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.margins(x=0)
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#222222")
    ax.spines["bottom"].set_color("#222222")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", colors="#222222", width=0.8)

    nota_zoom = None
    if xlim_max is not None:
        if xlim_max <= 0:
            raise ValueError("xlim_max deve ser maior que zero.")

        # Zoom so no eixo: densidades/contagens seguem com todos os municipios.
        fora = valores.loc[valores > xlim_max]
        ax.set_xlim(0, xlim_max)
        if len(fora) > 0:
            valores_fora = ", ".join(
                _formatar_numero(v) for v in sorted(fora.tolist(), reverse=True)
            )
            nota_zoom = (
                f"Recorte visual: 0–{_formatar_numero(xlim_max)} matriculas. "
                f"{len(fora)} municipio(s) acima desse limite "
                f"({valores_fora}) permanecem na amostra e no calculo da densidade."
            )
            ax.text(
                0.98,
                0.96,
                f"{len(fora)} municipio(s) > {_formatar_numero(xlim_max)} "
                f"(max. {_formatar_numero(fora.max())})",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=8.5,
                fontfamily="Times New Roman",
                color="#444444",
                bbox={
                    "boxstyle": "round,pad=0.25",
                    "facecolor": "white",
                    "edgecolor": "#D0D0D0",
                    "linewidth": 0.6,
                },
            )

    if plot_densidades:
        legenda = ax.legend(title="Ano", frameon=False)
        legenda.get_title().set_fontfamily("Times New Roman")
        for texto in legenda.get_texts():
            texto.set_fontfamily("Times New Roman")

    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")

    if nota_zoom:
        fig.tight_layout(rect=(0, 0.08, 1, 1))
        fig.text(
            0.01,
            0.01,
            nota_zoom,
            ha="left",
            va="bottom",
            fontsize=8,
            fontfamily="Times New Roman",
            color="#444444",
        )
    else:
        fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)

        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")

        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path

        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")

        if mostrar:
            print(f"Imagem salva em: {save_path}")
            if nota_zoom:
                print(nota_zoom)

    if mostrar:
        plt.show()

    return dados_histograma, fig


################# Funcao: plotar tendencia temporal das matriculas #################

def plotar_tendencia(
    deficiencia: str,
    anos: list[int] | tuple[int, ...] | None = None,
    zona_breakdown: str = "Total",
    dependencia_administrativa_breakdown: str | list[str] | tuple[str, ...] = "Estadual",
    caminho_dados: str | Path = DADOS_BREAKDOWN,
    titulo: str | None = None,
    rotulos_pontos: bool = True,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    df = carregar_dados_breakdown(caminho_dados)
    deficiencias = _resolver_deficiencias(df, deficiencia)

    if len(deficiencias) != 1:
        raise ValueError("Use apenas uma deficiencia para criar o grafico de tendencia.")

    deficiencia = deficiencias[0]
    zona = _resolver_valor(
        zona_breakdown,
        sorted(df["Zona_Breakdown"].dropna().unique()),
        "Zona_Breakdown",
    )
    dependencias = _resolver_dependencias(df, dependencia_administrativa_breakdown)
    anos_disponiveis = sorted(int(ano) for ano in df["Ano"].dropna().unique())
    anos_plotagem = list(anos) if anos is not None else anos_disponiveis

    if len(anos_plotagem) < 2:
        raise ValueError("Informe pelo menos dois anos para o grafico de tendencia.")

    pontos = []
    for ano_item in anos_plotagem:
        base = df.loc[
            (df["Ano"] == ano_item)
            & (df["Zona_Breakdown"] == zona)
            & (df["Dependencia_Administrativa"].isin(dependencias))
        ].copy()

        if base.empty:
            raise ValueError(
                "Nenhuma linha encontrada para "
                f"ano={ano_item}, zona={zona}, dependencia={dependencias}."
            )

        serie = pd.to_numeric(base[deficiencia], errors="coerce")
        pontos.append(
            {
                "Ano": int(ano_item),
                "Matriculas": serie.sum(min_count=1),
                "Municipios": int(base["Municipio"].nunique()),
            }
        )

    dados_tendencia = pd.DataFrame(pontos)

    try:
        import seaborn as sns

        sns.set_theme(
            context="paper",
            style="ticks",
            font="Times New Roman",
            palette="deep",
        )
    except ImportError:
        pass

    dependencia_rotulo = _formatar_parametro_texto(dependencia_administrativa_breakdown)
    if titulo is None:
        titulo = (
            f"Evolucao das matriculas - {deficiencia} "
            f"(zona {zona}, {dependencia_rotulo})"
        )

    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y = dados_tendencia["Matriculas"]
    ax.plot(
        dados_tendencia["Ano"],
        y,
        color="#0B3C5D",
        linewidth=2.2,
        marker="o",
        markersize=7.5,
        markerfacecolor="#0B3C5D",
        markeredgecolor="white",
        markeredgewidth=1.1,
        zorder=3,
    )

    if rotulos_pontos:
        deslocamento = (y.max() - y.min()) * 0.04 if y.notna().any() else 0
        for ano_item, valor in zip(dados_tendencia["Ano"], y):
            if pd.isna(valor):
                continue
            ax.annotate(
                _formatar_numero(valor),
                xy=(ano_item, valor),
                xytext=(0, 8 if deslocamento >= 0 else -12),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontfamily="Times New Roman",
                color="#0B3C5D",
            )

    ax.set_title(
        titulo,
        loc="left",
        fontfamily="Times New Roman",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlabel("Ano", fontfamily="Times New Roman")
    ax.set_ylabel("Matriculas", fontfamily="Times New Roman")
    ax.set_xticks(list(dados_tendencia["Ano"]))
    ax.set_xticklabels([str(ano_item) for ano_item in dados_tendencia["Ano"]])
    ymax = y.max(skipna=True)
    if pd.notna(ymax):
        ax.set_ylim(bottom=0, top=ymax * 1.18)
    ax.yaxis.grid(True, color="#E6E6E6", linewidth=0.7)
    ax.xaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#222222")
    ax.spines["bottom"].set_color("#222222")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", colors="#222222", width=0.8)

    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")

    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)

        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")

        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path

        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")

        if mostrar:
            print(f"Imagem salva em: {save_path}")

    if mostrar:
        plt.show()

    return dados_tendencia, fig


################# Funcao: crescimento acumulado simples entre deficiencias #################

_ROTULOS_DEFICIENCIA = {
    "Surdez": "Surdez",
    "Surdocegueira": "Surdocegueira",
    "Deficiencia_Auditiva": "Def. auditiva",
    "Visao_Monocular": "Visão monocular",
    "Baixa_Visao": "Baixa visão",
    "Cegueira": "Cegueira",
    "Deficiencia_Fisica": "Def. física",
    "Deficiencia_Intelectual": "Def. intelectual",
    "Deficiencia_Multipla": "Def. múltipla",
    "TEA_Autismo": "TEA/Autismo",
    "Altas_Habilidades_Superdotacao": "Altas habilidades",
}


def plotar_crescimento_deficiencias(
    deficiencia_destaque: str = "TEA_Autismo",
    ano_inicial: int = 2021,
    ano_final: int = 2025,
    zona_breakdown: str = "Total",
    dependencia_administrativa_breakdown: str | list[str] | tuple[str, ...] = "Estadual",
    excluir: list[str] | tuple[str, ...] | None = ("Visao_Monocular",),
    caminho_dados: str | Path = DADOS_BREAKDOWN,
    titulo: str | None = None,
    rotulos_barras: bool = True,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    """Compara o crescimento acumulado simples (Xf-Xi)/Xi entre deficiencias.

    A linha de referencia e a cesta das demais: crescimento da soma das
    matriculas das deficiencias que nao sao o destaque (media ponderada
    pelo estoque do ano inicial).
    """
    df = carregar_dados_breakdown(caminho_dados)
    destaque = _resolver_deficiencias(df, deficiencia_destaque)[0]
    colunas = selecionar_colunas_deficiencia(df)
    excluidas = set(excluir or [])
    deficiencias = [c for c in colunas if c not in excluidas]

    if destaque not in deficiencias:
        raise ValueError(
            f"Deficiencia de destaque {destaque} esta ausente ou foi excluida."
        )

    zona = _resolver_valor(
        zona_breakdown,
        sorted(df["Zona_Breakdown"].dropna().unique()),
        "Zona_Breakdown",
    )
    dependencias = _resolver_dependencias(df, dependencia_administrativa_breakdown)

    totais = {}
    for ano_item in (ano_inicial, ano_final):
        base = df.loc[
            (df["Ano"] == ano_item)
            & (df["Zona_Breakdown"] == zona)
            & (df["Dependencia_Administrativa"].isin(dependencias))
        ]
        if base.empty:
            raise ValueError(
                "Nenhuma linha encontrada para "
                f"ano={ano_item}, zona={zona}, dependencia={dependencias}."
            )
        totais[ano_item] = base[deficiencias].sum(min_count=1)

    linhas = []
    for coluna in deficiencias:
        xi = totais[ano_inicial][coluna]
        xf = totais[ano_final][coluna]
        if pd.isna(xi) or pd.isna(xf) or xi == 0:
            crescimento = float("nan")
        else:
            crescimento = (xf - xi) / xi * 100

        linhas.append(
            {
                "Deficiencia": coluna,
                "Rotulo": _ROTULOS_DEFICIENCIA.get(coluna, coluna),
                f"Matriculas_{ano_inicial}": xi,
                f"Matriculas_{ano_final}": xf,
                "Crescimento_pct": crescimento,
                "Destaque": coluna == destaque,
            }
        )

    dados = pd.DataFrame(linhas)
    demais = dados.loc[~dados["Destaque"]].copy()
    soma_i = demais[f"Matriculas_{ano_inicial}"].sum(min_count=1)
    soma_f = demais[f"Matriculas_{ano_final}"].sum(min_count=1)
    if pd.isna(soma_i) or soma_i == 0 or pd.isna(soma_f):
        raise ValueError("Nao foi possivel calcular a cesta das demais deficiencias.")

    crescimento_cesta = (soma_f - soma_i) / soma_i * 100
    crescimento_destaque = float(
        dados.loc[dados["Destaque"], "Crescimento_pct"].iloc[0]
    )

    dados_plot = dados.dropna(subset=["Crescimento_pct"]).sort_values(
        "Crescimento_pct", ascending=True
    )

    try:
        import seaborn as sns

        sns.set_theme(
            context="paper",
            style="ticks",
            font="Times New Roman",
            palette="deep",
        )
    except ImportError:
        pass

    if titulo is None:
        titulo = (
            f"Crescimento acumulado das matriculas 2021-2025"
        )

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    cores = [
        "#0B3C5D" if destaque_flag else "#9BB4C4"
        for destaque_flag in dados_plot["Destaque"]
    ]
    posicoes = list(range(len(dados_plot)))
    barras = ax.barh(
        posicoes,
        dados_plot["Crescimento_pct"],
        color=cores,
        edgecolor="white",
        linewidth=0.8,
        height=0.72,
    )
    ax.set_yticks(posicoes)
    ax.set_yticklabels(dados_plot["Rotulo"].tolist())

    ax.axvline(0, color="#222222", linewidth=0.9, zorder=2)
    ax.axvline(
        crescimento_cesta,
        color="#C76E6E",
        linewidth=1.5,
        linestyle="--",
        zorder=3,
        label=(
            f"Cesta demais deficiências: {_formatar_numero(crescimento_cesta)}%"
        ),
    )

    if rotulos_barras:
        for barra, valor in zip(barras, dados_plot["Crescimento_pct"]):
            deslocamento = 1.2 if valor >= 0 else -1.2
            ax.annotate(
                f"{_formatar_numero(valor)}%",
                xy=(valor, barra.get_y() + barra.get_height() / 2),
                xytext=(deslocamento, 0),
                textcoords="offset points",
                ha="left" if valor >= 0 else "right",
                va="center",
                fontsize=8.5,
                fontfamily="Times New Roman",
                color="#222222",
            )

    ax.set_title(
        titulo,
        loc="left",
        fontfamily="Times New Roman",
        fontsize=12,
        fontweight="bold",
        pad=18,
    )
    ax.set_xlabel(
        f"Crescimento acumulado simples, 2021-2025",
        fontfamily="Times New Roman",
    )
    ax.xaxis.grid(True, color="#E6E6E6", linewidth=0.7)
    ax.yaxis.grid(False)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#222222")
    ax.spines["bottom"].set_color("#222222")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", colors="#222222", width=0.8)

    legenda = ax.legend(frameon=False, loc="lower right")
    for texto in legenda.get_texts():
        texto.set_fontfamily("Times New Roman")

    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")

    nota = (
        f"{_ROTULOS_DEFICIENCIA.get(destaque, destaque)}: "
        f"{_formatar_numero(crescimento_destaque)}% | "
        f"Cesta demais: {_formatar_numero(crescimento_cesta)}% "
        f"(Diferença: {_formatar_numero(crescimento_destaque - crescimento_cesta)} p.p.). "
        f"Rede {dependencia_administrativa_breakdown if isinstance(dependencia_administrativa_breakdown, str) else _formatar_parametro_texto(dependencia_administrativa_breakdown)}, "
        f"Zona {zona}."
    )
    if excluidas:
        nota += " Exclui " + ", ".join(sorted(excluidas)).replace("_", " ") + "."

    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.text(
        0.01,
        0.01,
        nota,
        ha="left",
        va="bottom",
        fontsize=8,
        fontfamily="Times New Roman",
        color="#444444",
    )

    if save_path is not None:
        save_path = Path(save_path)

        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")

        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path

        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")

        if mostrar:
            print(f"Imagem salva em: {save_path}")
            print(nota)

    if mostrar:
        plt.show()

    resumo = {
        "crescimento_destaque_pct": crescimento_destaque,
        "crescimento_cesta_pct": crescimento_cesta,
        "diferenca_pp": crescimento_destaque - crescimento_cesta,
        "matriculas_cesta_inicial": float(soma_i),
        "matriculas_cesta_final": float(soma_f),
    }
    return dados, resumo, fig


################# Funcao auxiliar: quebrar rotulos longos em duas linhas #################


def _quebrar_rotulo_categoria(texto: str, largura: int = 22) -> str:
    texto = str(texto).strip()

    if not texto:
        return texto

    if len(texto) <= largura:
        return texto

    palavras = texto.split()

    if len(palavras) == 1:
        meio = len(texto) // 2
        return texto[:meio] + "\n" + texto[meio:]

    metade = len(texto) / 2
    linha1: list[str] = []
    linha2: list[str] = []
    acumulado = 0

    for indice, palavra in enumerate(palavras):
        tamanho_palavra = len(palavra) + (1 if linha1 else 0)

        if not linha2 and (acumulado + tamanho_palavra <= metade or not linha1):
            linha1.append(palavra)
            acumulado += tamanho_palavra
        else:
            linha2.extend(palavras[indice:])
            break

    if not linha2:
        linha2 = [linha1.pop()]

    return " ".join(linha1) + "\n" + " ".join(linha2)


################# Funcao auxiliar: exibir tabela de categorias #################


def _mostrar_tabela_categorias(tabela: pd.DataFrame, titulo: str) -> None:
    if _display_disponivel():
        from IPython.display import Markdown, display

        display(Markdown(f"### {titulo}"))
        display(tabela.reset_index(drop=True))
        return

    print(f"\n{titulo}")
    print(tabela.to_string(index=False))


def _filtrar_caminho_codificacao(
    data: pd.DataFrame,
    dominio: str,
    subdominio: str,
) -> pd.DataFrame:
    for coluna in ["Domínio", "Sub-domínio", "Sub-domínio detalhado", "id_passagem"]:
        if coluna not in data.columns:
            raise ValueError(f"data deve conter a coluna '{coluna}'.")

    dominio = str(dominio).strip()
    subdominio = str(subdominio).strip()

    if not dominio or not subdominio:
        raise ValueError("Informe dominio e subdominio.")

    opcoes_dominio = sorted(data["Domínio"].dropna().astype(str).unique())
    if dominio not in opcoes_dominio:
        raise ValueError(
            f"dominio '{dominio}' nao encontrado. Opcoes disponiveis: {opcoes_dominio}"
        )

    filtrado = data.loc[data["Domínio"].astype(str) == dominio].copy()
    opcoes_subdominio = sorted(filtrado["Sub-domínio"].dropna().astype(str).unique())
    if subdominio not in opcoes_subdominio:
        raise ValueError(
            f"subdominio '{subdominio}' nao encontrado em '{dominio}'. "
            f"Opcoes disponiveis: {opcoes_subdominio}"
        )

    return filtrado.loc[filtrado["Sub-domínio"].astype(str) == subdominio].copy()


def _resolver_logica_categorias(logica: str) -> LogicaCategoriasTipo:
    mapa = {
        "coluna_simples": "coluna_simples",
        "hierarquia": "hierarquia",
        "subdominio_detalhado": "subdominio_detalhado",
        "subdomínio_detalhado": "subdominio_detalhado",
    }
    chave = str(logica).strip().lower()

    if chave not in mapa:
        raise ValueError(
            "logica deve ser 'coluna_simples', 'hierarquia' ou 'subdominio_detalhado'."
        )

    return mapa[chave]


def _contar_categorias(
    data: pd.DataFrame,
    logica: LogicaCategoriasTipo,
    coluna: str,
    dominio: str | None,
    subdominio: str | None = None,
) -> tuple[pd.Series, str, str]:
    if "id_passagem" not in data.columns:
        raise ValueError("data deve conter a coluna 'id_passagem'.")

    if logica == "coluna_simples":
        if coluna not in data.columns:
            raise ValueError(f"Coluna '{coluna}' nao encontrada em data.")

        contagem = (
            data.groupby(coluna, dropna=False)["id_passagem"]
            .nunique()
            .sort_values(ascending=True)
        )
        nome_coluna_tabela = "domínio" if coluna == "Domínio" else coluna.lower()
        return contagem, nome_coluna_tabela, coluna

    if logica == "subdominio_detalhado":
        if dominio is None or not str(dominio).strip():
            raise ValueError("Informe dominio quando logica='subdominio_detalhado'.")
        if subdominio is None or not str(subdominio).strip():
            raise ValueError("Informe subdominio quando logica='subdominio_detalhado'.")

        filtrado = _filtrar_caminho_codificacao(data, dominio, subdominio)
        detalhado = filtrado.loc[filtrado["Sub-domínio detalhado"].notna()].copy()
        detalhado["Sub-domínio detalhado"] = (
            detalhado["Sub-domínio detalhado"].astype(str).str.strip()
        )
        detalhado = detalhado.loc[detalhado["Sub-domínio detalhado"] != ""]

        contagem = (
            detalhado.groupby("Sub-domínio detalhado", dropna=False)["id_passagem"]
            .nunique()
            .sort_values(ascending=True)
        )

        if contagem.empty:
            raise ValueError(
                f"Nao ha sub-dominios detalhados preenchidos em "
                f"'{dominio}' > '{subdominio}'."
            )

        if len(contagem) < 2:
            raise ValueError(
                f"logica='subdominio_detalhado' exige ao menos 2 categorias detalhadas em "
                f"'{dominio}' > '{subdominio}'. Encontradas: {len(contagem)}."
            )

        return contagem, "sub-domínio detalhado", "Sub-domínio detalhado"

    if dominio is None or not str(dominio).strip():
        raise ValueError("Informe dominio quando logica='hierarquia'.")

    for coluna_obrigatoria in ["Domínio", "Sub-domínio"]:
        if coluna_obrigatoria not in data.columns:
            raise ValueError(
                f"logica='hierarquia' requer a coluna '{coluna_obrigatoria}'."
            )

    dominio = str(dominio).strip()
    opcoes = sorted(data["Domínio"].dropna().astype(str).unique())

    if dominio not in opcoes:
        raise ValueError(
            f"dominio '{dominio}' nao encontrado. Opcoes disponiveis: {opcoes}"
        )

    filtrado = data.loc[data["Domínio"].astype(str) == dominio].copy()
    filtrado = filtrado.loc[filtrado["Sub-domínio"].notna()].copy()

    contagem = (
        filtrado.groupby("Sub-domínio", dropna=False)["id_passagem"]
        .nunique()
        .sort_values(ascending=True)
    )

    if len(contagem) < 2:
        raise ValueError(
            f"logica='hierarquia' exige ao menos 2 sub-dominios em '{dominio}'. "
            f"Encontrados: {len(contagem)}."
        )

    return contagem, "sub-domínio", "Sub-domínio"


def _preparar_subdominios_hierarquia(
    contagem: pd.Series,
    top_n: int = 3,
    agregacao_outros: bool = False,
) -> pd.Series:
    ordenado = contagem.sort_values(ascending=False)

    if agregacao_outros and len(ordenado) > top_n:
        top = ordenado.head(top_n).sort_values(ascending=True)
        outros = pd.Series({"Outros": int(ordenado.iloc[top_n:].sum())})
        # Outros na base do grafico (ultima barra na leitura de cima para baixo)
        resultado = pd.concat([outros, top])
    else:
        resultado = ordenado.head(top_n).sort_values(ascending=True)

    resultado.index.name = contagem.index.name or "Sub-domínio"
    return resultado


def _cores_barras_categorias(
    contagem: pd.Series,
    logica: LogicaCategoriasTipo,
    cor_destaque: str,
    cor_cinza: str,
) -> list[str]:
    if logica == "hierarquia":
        return [
            cor_cinza if str(categoria) == "Outros" else cor_destaque
            for categoria in contagem.index
        ]

    n_categorias = len(contagem)
    return [
        cor_destaque if indice >= n_categorias - 3 else cor_cinza
        for indice in range(n_categorias)
    ]


################# Funcao: descricao geral do dataset codificado #################


def _contar_valores_validos(serie: pd.Series) -> int:
    return (
        serie.dropna()
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )


def _formatar_valor_descritivo(valor: float | int, tipo: str) -> str:
    if tipo == "inteiro":
        return f"{int(valor):,}".replace(",", ".")

    if tipo == "percentual":
        texto = f"{float(valor):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{texto}%"

    texto = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return texto


def _gerar_html_descritivos_dataset(
    tabela: pd.DataFrame,
    titulo: str,
    caminho_html: str | Path | None = None,
) -> Path:
    if caminho_html is None:
        caminho_html = OUTPUT_DIR / "descritivos_dataset.html"
    else:
        caminho_html = Path(caminho_html)

    if not caminho_html.is_absolute():
        caminho_html = OUTPUT_DIR / caminho_html

    tabela_html = tabela.copy()
    tabela_html["Definição"] = (
        tabela_html["Definição"].astype(str).str.replace("`", "", regex=False)
    )

    linhas = []
    for _, linha in tabela_html.iterrows():
        linhas.append(
            "<tr>"
            f"<td>{linha['Indicadores']}</td>"
            f"<td>{linha['Definição']}</td>"
            f"<td style=\"text-align: right; white-space: nowrap;\">{linha['Valor']}</td>"
            "</tr>"
        )

    corpo_tabela = "\n".join(linhas)
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>{titulo}</title>
    <style>
        body {{
            background: #f5f5f5;
            color: #111;
            font-family: "Times New Roman", Times, serif;
            margin: 0;
            padding: 32px;
        }}
        main {{
            background: white;
            margin: 0 auto;
            max-width: 960px;
            padding: 40px 48px;
        }}
        h1 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 0 0 8px;
        }}
        .instrucao {{
            color: #444;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10pt;
            margin: 0 0 24px;
        }}
        table {{
            border-collapse: collapse;
            font-size: 11pt;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #111;
            padding: 8px 10px;
            text-align: left;
            vertical-align: top;
        }}
        th:last-child, td:last-child {{
            text-align: right;
        }}
        thead th {{
            background: #f0f0f0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <main>
        <h1>{titulo}</h1>
        <p class="instrucao">
            Selecione a tabela abaixo e copie (Ctrl/Cmd+C) para colar no Google Docs.
        </p>
        <table>
            <thead>
                <tr>
                    <th>Indicadores</th>
                    <th>Definição</th>
                    <th>Valor</th>
                </tr>
            </thead>
            <tbody>
                {corpo_tabela}
            </tbody>
        </table>
    </main>
</body>
</html>
"""

    caminho_html.parent.mkdir(parents=True, exist_ok=True)
    caminho_html.write_text(html, encoding="utf-8")
    return caminho_html


def descreve_dataset(
    data: pd.DataFrame,
    mostrar: bool = True,
    abrir_html: bool = False,
    caminho_html: str | Path | None = None,
) -> pd.DataFrame:
    colunas_obrigatorias = [
        "id_passagem",
        "document",
        "Domínio",
        "Sub-domínio",
        "Sub-domínio detalhado",
    ]
    faltantes = [coluna for coluna in colunas_obrigatorias if coluna not in data.columns]
    if faltantes:
        raise ValueError(
            "data deve conter as colunas: "
            + ", ".join(faltantes)
        )

    n_passagens = data["id_passagem"].nunique()
    n_dominios = data["Domínio"].nunique()
    n_subdominios = data["Sub-domínio"].nunique()
    n_subdominios_detalhados = _contar_valores_validos(data["Sub-domínio detalhado"])
    n_alocacoes = len(data)
    n_documentos = _contar_valores_validos(data["document"])
    media_codificacoes_por_passagem = (
        float(n_alocacoes / n_passagens) if n_passagens else 0.0
    )

    contagem_por_dominio = data.groupby("Domínio")["id_passagem"].nunique()
    media_por_dominio = float(contagem_por_dominio.mean()) if len(contagem_por_dominio) else 0.0

    indicadores = [
        (
            "Passagens",
            "Trechos citados das entrevistas analisados (unidade de análise).",
            n_passagens,
            "inteiro",
        ),
        (
            "Transcrições",
            "Entrevistas distintas de onde as passagens foram extraídas.",
            n_documentos,
            "inteiro",
        ),
        (
            "Domínios",
            "Categorias de primeiro nível presentes no corpus.",
            n_dominios,
            "inteiro",
        ),
        (
            "Subdomínios",
            "Categorias de segundo nível presentes no corpus.",
            n_subdominios,
            "inteiro",
        ),
        (
            "Subdomínios detalhados",
            "Categorias de terceiro nível preenchidas no corpus.",
            n_subdominios_detalhados,
            "inteiro",
        ),
        (
            "Total de codificações",
            "Atribuições Domínio + Sub-domínio realizadas. "
            "Uma passagem pode receber mais de uma codificação.",
            n_alocacoes,
            "inteiro",
        ),
        (
            "Média de codificações por passagem",
            "Total de codificações ÷ número de passagens.",
            media_codificacoes_por_passagem,
            "decimal",
        ),
        (
            "Média de passagens por domínio",
            "Em média, quantas passagens distintas cada domínio reúne.",
            media_por_dominio,
            "decimal",
        ),
    ]

    tabela = pd.DataFrame(
        {
            "Indicadores": [item[0] for item in indicadores],
            "Definição": [item[1] for item in indicadores],
            "Valor": [
                _formatar_valor_descritivo(valor, tipo)
                for _, _, valor, tipo in indicadores
            ],
        }
    )

    titulo = "Descritivos do dataset codificado"

    if mostrar:
        _mostrar_tabela_categorias(tabela, titulo)

    if abrir_html:
        caminho_gerado = _gerar_html_descritivos_dataset(
            tabela=tabela,
            titulo=titulo,
            caminho_html=caminho_html,
        )
        webbrowser.open(caminho_gerado.resolve().as_uri())
        if mostrar:
            print(f"\nTabela HTML salva em: {caminho_gerado}")

    return tabela


################# Funcao: diagrama descritivo da estrutura de codificacao #################


def _pct_br(parte: int, total: int) -> str:
    if total == 0:
        return "0,0%"
    return f"{100 * parte / total:.1f}".replace(".", ",") + "%"


def _tem_subdominio_detalhado(serie: pd.Series) -> pd.Series:
    texto = serie.astype(str).str.strip()
    return serie.notna() & ~texto.isin(["", "nan", "None", "NaN", "<NA>"])


def _caixa_diagrama(
    ax,
    x: float,
    y: float,
    texto: str,
    *,
    largura: float,
    altura: float,
    facecolor: str = "#E8F0F4",
    edgecolor: str = "#4A6D7C",
    textcolor: str = "#1F2A30",
    fontsize: int = 10,
    fontweight: str = "normal",
) -> dict[str, float]:
    from matplotlib.patches import FancyBboxPatch

    caixa = FancyBboxPatch(
        (x - largura / 2, y - altura / 2),
        largura,
        altura,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        linewidth=1.15,
        edgecolor=edgecolor,
        facecolor=facecolor,
        clip_on=False,
        zorder=2,
    )
    ax.add_patch(caixa)
    ax.text(
        x,
        y,
        texto,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontfamily="Times New Roman",
        fontweight=fontweight,
        color=textcolor,
        linespacing=1.25,
        clip_on=False,
        zorder=3,
    )
    return {"x": x, "y": y, "w": largura, "h": altura}


def _ligar_diagrama(ax, origem: dict[str, float], destino: dict[str, float], cor: str = "#4A6D7C"):
    x0, y0 = origem["x"], origem["y"] - origem["h"] / 2
    x1, y1 = destino["x"], destino["y"] + destino["h"] / 2
    ax.annotate(
        "",
        xy=(x1, y1),
        xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle="-|>",
            color=cor,
            lw=1.1,
            shrinkA=1,
            shrinkB=1,
        ),
        clip_on=False,
        zorder=1,
    )


def diagrama_descritivo(
    data: pd.DataFrame,
    titulo: str = "Estrutura das codificações no corpus",
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    """Desenha o diagrama da estrutura de codificacao (layout vertical A4).

    Bloco superior: multialocacao (1 vs >1 codificacao; entre dominios vs
    no mesmo dominio). Bloco inferior: uso do subdominio detalhado (opcional).
    """
    colunas_obrigatorias = ["id_passagem", "Domínio", "Sub-domínio detalhado"]
    faltantes = [coluna for coluna in colunas_obrigatorias if coluna not in data.columns]
    if faltantes:
        raise ValueError(
            "data deve conter as colunas: " + ", ".join(faltantes)
        )

    resumo = data.groupby("id_passagem", as_index=False).agg(
        n_codificacoes=("Domínio", "size"),
        n_dominios=("Domínio", "nunique"),
    )
    tem_detalhado = (
        data.assign(_det=_tem_subdominio_detalhado(data["Sub-domínio detalhado"]))
        .groupby("id_passagem")["_det"]
        .any()
    )
    resumo = resumo.merge(
        tem_detalhado.rename("tem_detalhado").reset_index(),
        on="id_passagem",
        how="left",
    )
    resumo["tem_detalhado"] = resumo["tem_detalhado"].fillna(False)

    n_passagens = int(len(resumo))
    n_multi = int((resumo["n_codificacoes"] > 1).sum())
    n_unica = int((resumo["n_codificacoes"] == 1).sum())
    n_multi_dominio = int(
        ((resumo["n_codificacoes"] > 1) & (resumo["n_dominios"] > 1)).sum()
    )
    n_mesmo_dominio = int(
        ((resumo["n_codificacoes"] > 1) & (resumo["n_dominios"] == 1)).sum()
    )
    n_com_detalhado = int(resumo["tem_detalhado"].sum())
    n_sem_detalhado = int((~resumo["tem_detalhado"]).sum())

    if n_multi + n_unica != n_passagens:
        raise ValueError("Partição 1 vs >1 codificação inconsistente.")
    if n_multi_dominio + n_mesmo_dominio != n_multi:
        raise ValueError("Partição multi-domínio vs mesmo domínio inconsistente.")
    if n_com_detalhado + n_sem_detalhado != n_passagens:
        raise ValueError("Partição com/sem detalhado inconsistente.")

    contagens = {
        "passagens": n_passagens,
        "multi": n_multi,
        "unica": n_unica,
        "multi_dominio": n_multi_dominio,
        "mesmo_dominio": n_mesmo_dominio,
        "com_detalhado": n_com_detalhado,
        "sem_detalhado": n_sem_detalhado,
    }

    # Proporção próxima de A4 retrato (210 × 297 mm), com margens para Word.
    fig_w_in, fig_h_in = 7.0, 9.7
    fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_facecolor("white")

    ax.text(
        0.50,
        0.975,
        titulo,
        ha="center",
        va="top",
        fontsize=13,
        fontfamily="Times New Roman",
        fontweight="bold",
        color="#1F2A30",
        clip_on=False,
    )

    # ---- Bloco A: multialocação ----
    ax.text(
        0.08,
        0.930,
        "A. Multialocação de passagens",
        ha="left",
        va="center",
        fontsize=11,
        fontfamily="Times New Roman",
        fontweight="bold",
        color="#1F2A30",
        clip_on=False,
    )

    w_raiz, h_raiz = 0.46, 0.048
    w_meio, h_meio = 0.40, 0.068
    w_folha, h_folha = 0.40, 0.068

    raiz_a = _caixa_diagrama(
        ax,
        0.50,
        0.875,
        f"{n_passagens} passagens",
        largura=w_raiz,
        altura=h_raiz,
        facecolor="#4A6D7C",
        edgecolor="#4A6D7C",
        textcolor="white",
        fontsize=11,
        fontweight="bold",
    )
    caixa_multi = _caixa_diagrama(
        ax,
        0.28,
        0.760,
        (
            f"{n_multi} com mais de 1 codificação\n"
            f"{_pct_br(n_multi, n_passagens)} do corpus"
        ),
        largura=w_meio,
        altura=h_meio,
        fontsize=9.5,
    )
    caixa_unica = _caixa_diagrama(
        ax,
        0.72,
        0.760,
        (
            f"{n_unica} com 1 codificação apenas\n"
            f"{_pct_br(n_unica, n_passagens)} do corpus"
        ),
        largura=w_meio,
        altura=h_meio,
        facecolor="#F4F6F7",
        fontsize=9.5,
    )
    # Filhos da multialocação, lado a lado sob o ramo esquerdo (margens internas).
    caixa_multi_dom = _caixa_diagrama(
        ax,
        0.21,
        0.615,
        (
            f"{n_multi_dominio} em mais de 1 domínio\n"
            f"{_pct_br(n_multi_dominio, n_multi)} das {n_multi}"
        ),
        largura=0.32,
        altura=h_folha,
        fontsize=9,
    )
    caixa_mesmo_dom = _caixa_diagrama(
        ax,
        0.55,
        0.615,
        (
            f"{n_mesmo_dominio} no mesmo domínio\n"
            f"{_pct_br(n_mesmo_dominio, n_multi)} das {n_multi}"
        ),
        largura=0.32,
        altura=h_folha,
        fontsize=9,
    )
    _ligar_diagrama(ax, raiz_a, caixa_multi)
    _ligar_diagrama(ax, raiz_a, caixa_unica)
    _ligar_diagrama(ax, caixa_multi, caixa_multi_dom)
    _ligar_diagrama(ax, caixa_multi, caixa_mesmo_dom)

    ax.plot([0.08, 0.92], [0.540, 0.540], color="#C8D0D4", lw=0.8, clip_on=False)

    # ---- Bloco B: detalhado opcional ----
    ax.text(
        0.08,
        0.505,
        "B. Subdomínio detalhado (opcional)",
        ha="left",
        va="center",
        fontsize=11,
        fontfamily="Times New Roman",
        fontweight="bold",
        color="#1F2A30",
        clip_on=False,
    )

    raiz_b = _caixa_diagrama(
        ax,
        0.50,
        0.440,
        f"{n_passagens} passagens",
        largura=w_raiz,
        altura=h_raiz,
        facecolor="#4A6D7C",
        edgecolor="#4A6D7C",
        textcolor="white",
        fontsize=11,
        fontweight="bold",
    )
    caixa_com = _caixa_diagrama(
        ax,
        0.28,
        0.310,
        (
            f"{n_com_detalhado} com ao menos 1 detalhado\n"
            f"{_pct_br(n_com_detalhado, n_passagens)} do corpus"
        ),
        largura=w_meio,
        altura=h_meio,
        fontsize=9.5,
    )
    caixa_sem = _caixa_diagrama(
        ax,
        0.72,
        0.310,
        (
            f"{n_sem_detalhado} só domínio + subdomínio\n"
            f"{_pct_br(n_sem_detalhado, n_passagens)} do corpus"
        ),
        largura=w_meio,
        altura=h_meio,
        facecolor="#F4F6F7",
        fontsize=9.5,
    )
    _ligar_diagrama(ax, raiz_b, caixa_com)
    _ligar_diagrama(ax, raiz_b, caixa_sem)

    ax.text(
        0.50,
        0.175,
        (
            "Cada codificação exige Domínio + Subdomínio.\n"
            "O subdomínio detalhado é o terceiro nível, usado só quando o codebook o prevê."
        ),
        ha="center",
        va="center",
        fontsize=9,
        fontfamily="Times New Roman",
        color="#444444",
        linespacing=1.4,
        clip_on=False,
    )

    fig.subplots_adjust(left=0.05, right=0.95, top=0.97, bottom=0.05)

    if save_path is not None:
        save_path = Path(save_path)
        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")
        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            save_path,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.25,
            facecolor="white",
        )
        if mostrar:
            print(f"Imagem salva em: {save_path}")

    if mostrar:
        plt.show()

    return contagens, fig


################# Funcao: matriz de coocorrencia entre dominios #################


def _rotulo_curto_dominio(nome: str, largura: int = 18) -> str:
    return _quebrar_rotulo_categoria(str(nome).strip(), largura=largura)


def calcular_coocorrencia_dominios(data: pd.DataFrame) -> pd.DataFrame:
    """Conta passagens unicas compartilhadas entre pares de dominios.

    A diagonal é o total de passagens do domínio. Fora da diagonal, o número
    de passagens alocadas simultaneamente nos dois domínios.
    """
    if "id_passagem" not in data.columns or "Domínio" not in data.columns:
        raise ValueError("data deve conter as colunas 'id_passagem' e 'Domínio'.")

    presencia = (
        data.loc[data["Domínio"].notna(), ["id_passagem", "Domínio"]]
        .assign(Domínio=lambda d: d["Domínio"].astype(str).str.strip())
        .drop_duplicates()
    )
    if presencia.empty:
        raise ValueError("Nao ha dominios para calcular coocorrencia.")

    ordem = (
        presencia.groupby("Domínio")["id_passagem"]
        .nunique()
        .sort_values(ascending=False)
        .index.tolist()
    )
    conjuntos = {
        dominio: set(grupo["id_passagem"])
        for dominio, grupo in presencia.groupby("Domínio")
    }

    matriz = pd.DataFrame(0, index=ordem, columns=ordem, dtype=int)
    for i, dominio_i in enumerate(ordem):
        for j, dominio_j in enumerate(ordem):
            if i == j:
                matriz.loc[dominio_i, dominio_j] = len(conjuntos[dominio_i])
            else:
                matriz.loc[dominio_i, dominio_j] = len(
                    conjuntos[dominio_i] & conjuntos[dominio_j]
                )
    return matriz


def _pares_coocorrencia(matriz: pd.DataFrame) -> pd.DataFrame:
    pares = []
    rotulos = list(matriz.index)
    for i, dominio_i in enumerate(rotulos):
        for dominio_j in rotulos[i + 1 :]:
            n = int(matriz.loc[dominio_i, dominio_j])
            if n <= 0:
                continue
            pares.append(
                {
                    "Domínio A": dominio_i,
                    "Domínio B": dominio_j,
                    "Passagens em comum": n,
                }
            )
    tabela = pd.DataFrame(pares)
    if tabela.empty:
        return tabela
    return tabela.sort_values(
        ["Passagens em comum", "Domínio A", "Domínio B"],
        ascending=[False, True, True],
    ).reset_index(drop=True)


def matriz_coocorrencia_dominios(
    data: pd.DataFrame,
    titulo: str = "Coocorrência de domínios (passagens únicas)",
    top_pares: int = 10,
    tabela: bool = True,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    """Heatmap de coocorrencia entre dominios + tabela dos pares mais frequentes.

    Cada célula fora da diagonal é o número de passagens únicas codificadas
    nos dois domínios. A diagonal é o total de passagens do domínio.
    """
    matriz = calcular_coocorrencia_dominios(data)
    pares = _pares_coocorrencia(matriz)
    n_passagens_multi_dominio = int(
        data.groupby("id_passagem")["Domínio"].nunique().gt(1).sum()
    )

    if tabela and mostrar:
        _mostrar_tabela_categorias(
            pares.head(top_pares) if top_pares else pares,
            f"Pares de domínios com maior coocorrência (top {top_pares})",
        )

    try:
        import seaborn as sns

        sns.set_theme(
            context="paper",
            style="ticks",
            font="Times New Roman",
        )
    except ImportError:
        sns = None

    n = len(matriz)
    fig_w = max(8.0, 0.55 * n + 3.5)
    fig_h = max(7.2, 0.55 * n + 3.0)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    rotulos = [_rotulo_curto_dominio(nome) for nome in matriz.index]
    valores = matriz.to_numpy(dtype=float)
    vmax = float(valores.max()) if valores.size else 1.0

    if sns is not None:
        sns.heatmap(
            valores,
            ax=ax,
            cmap="Blues",
            vmin=0,
            vmax=vmax,
            annot=True,
            fmt=".0f",
            square=True,
            linewidths=0.6,
            linecolor="white",
            cbar_kws={
                "label": "Passagens únicas",
                "shrink": 0.75,
            },
            xticklabels=rotulos,
            yticklabels=rotulos,
            annot_kws={
                "fontsize": 8,
                "fontfamily": "Times New Roman",
            },
        )
    else:
        imagem = ax.imshow(valores, cmap="Blues", vmin=0, vmax=vmax)
        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    str(int(valores[i, j])),
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontfamily="Times New Roman",
                    color="#111111" if valores[i, j] < vmax * 0.6 else "white",
                )
        ax.set_xticks(range(n), rotulos)
        ax.set_yticks(range(n), rotulos)
        cbar = fig.colorbar(imagem, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Passagens únicas", fontfamily="Times New Roman")

    # Destaca a diagonal (totais por domínio).
    for i in range(n):
        ax.add_patch(
            plt.Rectangle(
                (i, i),
                1,
                1,
                fill=False,
                edgecolor="#1F2A30",
                linewidth=1.4,
                clip_on=False,
            )
        )

    ax.set_title(
        titulo,
        fontfamily="Times New Roman",
        fontsize=13,
        fontweight="bold",
        loc="left",
        pad=14,
        color="#1F2A30",
    )
    ax.tick_params(axis="both", labelsize=8, length=0)
    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")
    ax.set_xticklabels(rotulos, rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(rotulos, rotation=0)

    if ax.collections:
        cbar = ax.collections[0].colorbar
        if cbar is not None:
            cbar.ax.yaxis.label.set_fontfamily("Times New Roman")
            for texto in cbar.ax.get_yticklabels():
                texto.set_fontfamily("Times New Roman")

    nota = (
        "Diagonal (contorno escuro) = total de passagens no domínio. "
        "Fora da diagonal = passagens únicas alocadas nos dois domínios ao mesmo tempo. "
        f"{n_passagens_multi_dominio} passagens do corpus estão em mais de um domínio. "
        "O overlap é esperado pelo desenho de multialocação."
    )
    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.text(
        0.02,
        0.02,
        nota,
        transform=fig.transFigure,
        fontsize=9,
        fontfamily="Times New Roman",
        color="#444444",
        wrap=True,
    )

    if save_path is not None:
        save_path = Path(save_path)
        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")
        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            save_path,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.25,
            facecolor="white",
        )
        if mostrar:
            print(f"Imagem salva em: {save_path}")

    if mostrar:
        plt.show()

    return matriz, pares, fig


################# Funcao: heatmap de coocorrencia intradominio (subdominios) #################


def calcular_coocorrencia_subdominios(
    data: pd.DataFrame,
    dominio: str,
) -> pd.DataFrame:
    """Coocorrencia de subdominios dentro de um unico dominio.

    Diagonal = passagens unicas do subdominio naquele dominio.
    Fora da diagonal = passagens com os dois subdominios no mesmo dominio.
    """
    for coluna in ["id_passagem", "Domínio", "Sub-domínio"]:
        if coluna not in data.columns:
            raise ValueError(f"data deve conter a coluna '{coluna}'.")

    dominio = str(dominio).strip()
    opcoes = sorted(data["Domínio"].dropna().astype(str).str.strip().unique())
    if dominio not in opcoes:
        raise ValueError(f"dominio '{dominio}' nao encontrado. Opcoes: {opcoes}")

    filtrado = data.loc[
        data["Domínio"].astype(str).str.strip() == dominio,
        ["id_passagem", "Sub-domínio"],
    ].copy()
    filtrado["Sub-domínio"] = filtrado["Sub-domínio"].astype(str).str.strip()
    filtrado = filtrado.loc[
        filtrado["Sub-domínio"].ne("")
        & ~filtrado["Sub-domínio"].isin(["nan", "None", "NaN", "<NA>"])
    ].drop_duplicates()

    if filtrado.empty:
        raise ValueError(f"Nao ha subdominios em '{dominio}'.")

    ordem = (
        filtrado.groupby("Sub-domínio")["id_passagem"]
        .nunique()
        .sort_values(ascending=False)
        .index.tolist()
    )
    conjuntos = {
        sub: set(grupo["id_passagem"])
        for sub, grupo in filtrado.groupby("Sub-domínio")
    }

    matriz = pd.DataFrame(0, index=ordem, columns=ordem, dtype=int)
    for i, sub_i in enumerate(ordem):
        for j, sub_j in enumerate(ordem):
            if i == j:
                matriz.loc[sub_i, sub_j] = len(conjuntos[sub_i])
            else:
                matriz.loc[sub_i, sub_j] = len(conjuntos[sub_i] & conjuntos[sub_j])
    return matriz


def listar_dominios_com_overlap_subdominio(data: pd.DataFrame) -> list[str]:
    """Dominios em que ao menos uma passagem tem 2+ subdominios."""
    if "id_passagem" not in data.columns or "Domínio" not in data.columns:
        raise ValueError("data deve conter 'id_passagem' e 'Domínio'.")
    if "Sub-domínio" not in data.columns:
        raise ValueError("data deve conter 'Sub-domínio'.")

    contagem = (
        data.groupby(["Domínio", "id_passagem"])["Sub-domínio"]
        .nunique()
        .reset_index(name="n_sub")
    )
    com_overlap = (
        contagem.loc[contagem["n_sub"] > 1, "Domínio"]
        .astype(str)
        .str.strip()
        .value_counts()
    )
    # Ordena pelos domínios com mais passagens multi-subdomínio.
    return com_overlap.index.tolist()


def _slug_dominio(nome: str) -> str:
    mapa = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    texto = str(nome).strip().lower()
    for origem, destino in mapa.items():
        texto = texto.replace(origem, destino)
    limpo = "".join(ch if ch.isalnum() else "_" for ch in texto)
    while "__" in limpo:
        limpo = limpo.replace("__", "_")
    return limpo.strip("_")[:48]


def _reduzir_matriz_subdominios(
    matriz: pd.DataFrame,
    max_subdominios: int = 12,
) -> pd.DataFrame:
    if matriz.shape[0] <= max_subdominios:
        return matriz

    off = matriz.copy()
    for i in range(len(off)):
        off.iloc[i, i] = 0
    score = off.sum(axis=1).astype(float) + matriz.values.diagonal().astype(float) * 0.01
    keep = score.sort_values(ascending=False).head(max_subdominios).index.tolist()
    return matriz.loc[keep, keep]


def heatmap_coocorrencia_subdominios(
    data: pd.DataFrame,
    dominio: str | None = None,
    titulo: str | None = None,
    min_subdominios: int = 2,
    max_subdominios: int = 12,
    apenas_com_overlap: bool = True,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    """Heatmap de coocorrencia de subdominios (overlap intradominio).

    Parametros
    ----------
    dominio : str | None
        Se informado, gera o heatmap desse domínio. Se None, gera um heatmap
        por domínio que tem overlap intradomínio (passagem com ≥2 subdomínios).
    apenas_com_overlap : bool
        Quando dominio=None, ignora domínios sem nenhum par coocorrente.
    max_subdominios : int
        Limite de eixos no heatmap (prioriza subdomínios com mais coocorrência).
    """
    try:
        import seaborn as sns

        sns.set_theme(context="paper", style="ticks", font="Times New Roman")
    except ImportError:
        sns = None

    # Modo em lote: um arquivo/figura por domínio com overlap.
    if dominio is None:
        dominios = listar_dominios_com_overlap_subdominio(data)
        if not dominios:
            raise ValueError("Nenhum domínio com overlap intradomínio de subdomínios.")

        matrizes: dict[str, pd.DataFrame] = {}
        figuras: dict[str, object] = {}
        for nome_dominio in dominios:
            caminho = None
            if save_path is not None:
                base = Path(save_path)
                if base.suffix == "":
                    base = base.with_suffix(".png")
                caminho = base.with_name(
                    f"{base.stem}_{_slug_dominio(nome_dominio)}{base.suffix}"
                )
            mats_um, fig_um = heatmap_coocorrencia_subdominios(
                data=data,
                dominio=nome_dominio,
                titulo=titulo,
                min_subdominios=min_subdominios,
                max_subdominios=max_subdominios,
                apenas_com_overlap=apenas_com_overlap,
                save_path=caminho,
                dpi=dpi,
                mostrar=mostrar,
            )
            if not mats_um:
                continue
            matrizes.update(mats_um)
            figuras[nome_dominio] = fig_um
        if not matrizes:
            raise ValueError(
                "Nenhum domínio com overlap intradomínio de subdomínios para plotar."
            )
        return matrizes, figuras

    nome_dominio = str(dominio).strip()
    matriz = calcular_coocorrencia_subdominios(data, nome_dominio)
    if matriz.shape[0] < min_subdominios:
        raise ValueError(
            f"Dominio '{nome_dominio}' tem menos de {min_subdominios} subdominios."
        )

    off = matriz.copy()
    for i in range(len(off)):
        off.iloc[i, i] = 0
    if apenas_com_overlap and int(off.to_numpy().sum()) == 0:
        raise ValueError(
            f"Dominio '{nome_dominio}' nao tem overlap intradominio de subdominios."
        )

    matriz = _reduzir_matriz_subdominios(matriz, max_subdominios=max_subdominios)
    n_omitidos = (
        calcular_coocorrencia_subdominios(data, nome_dominio).shape[0] - matriz.shape[0]
    )

    n = len(matriz)
    fig_w = max(7.0, 0.55 * n + 3.2)
    fig_h = max(6.2, 0.55 * n + 2.8)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    rotulos = [_quebrar_rotulo_categoria(nome, largura=18) for nome in matriz.index]
    valores = matriz.to_numpy(dtype=float)
    vmax = float(valores.max()) if valores.size else 1.0

    if sns is not None:
        sns.heatmap(
            valores,
            ax=ax,
            cmap="Blues",
            vmin=0,
            vmax=vmax,
            annot=True,
            fmt=".0f",
            square=True,
            linewidths=0.6,
            linecolor="white",
            cbar_kws={"label": "Passagens únicas", "shrink": 0.75},
            xticklabels=rotulos,
            yticklabels=rotulos,
            annot_kws={"fontsize": 8, "fontfamily": "Times New Roman"},
        )
    else:
        imagem = ax.imshow(valores, cmap="Blues", vmin=0, vmax=vmax)
        for i in range(n):
            for j in range(n):
                ax.text(
                    j,
                    i,
                    str(int(valores[i, j])),
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontfamily="Times New Roman",
                )
        ax.set_xticks(range(n), rotulos)
        ax.set_yticks(range(n), rotulos)
        cbar = fig.colorbar(imagem, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Passagens únicas", fontfamily="Times New Roman")

    for i in range(n):
        ax.add_patch(
            plt.Rectangle(
                (i, i),
                1,
                1,
                fill=False,
                edgecolor="#1F2A30",
                linewidth=1.3,
                clip_on=False,
            )
        )

    n_multi = int(
        data.loc[data["Domínio"].astype(str).str.strip() == nome_dominio]
        .groupby("id_passagem")["Sub-domínio"]
        .nunique()
        .gt(1)
        .sum()
    )
    titulo_final = titulo or f"Coocorrência de subdomínios — {nome_dominio}"
    ax.set_title(
        titulo_final,
        fontfamily="Times New Roman",
        fontsize=12,
        fontweight="bold",
        loc="left",
        pad=12,
        color="#1F2A30",
    )
    ax.tick_params(axis="both", labelsize=8, length=0)
    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")
    ax.set_xticklabels(rotulos, rotation=45, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(rotulos, rotation=0)

    if ax.collections:
        cbar = ax.collections[0].colorbar
        if cbar is not None:
            cbar.ax.yaxis.label.set_fontfamily("Times New Roman")
            for texto in cbar.ax.get_yticklabels():
                texto.set_fontfamily("Times New Roman")

    nota = (
        "Overlap intradomínio: diagonal = passagens do subdomínio neste domínio; "
        "fora da diagonal = passagens com os dois subdomínios na mesma passagem. "
        f"{n_multi} passagens deste domínio têm ≥2 subdomínios."
    )
    if n_omitidos > 0:
        nota += (
            f" Exibindo os {n} subdomínios com maior coocorrência "
            f"({n_omitidos} omitidos por legibilidade)."
        )

    fig.tight_layout(rect=[0, 0.08, 1, 1])
    fig.text(
        0.02,
        0.02,
        nota,
        transform=fig.transFigure,
        fontsize=9,
        fontfamily="Times New Roman",
        color="#444444",
        wrap=True,
    )

    if save_path is not None:
        save_path = Path(save_path)
        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")
        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(
            save_path,
            dpi=dpi,
            bbox_inches="tight",
            pad_inches=0.25,
            facecolor="white",
        )
        if mostrar:
            print(f"Imagem salva em: {save_path}")

    if mostrar:
        plt.show()

    return {nome_dominio: matriz}, fig


################# Funcao: inventario de caminhos (apendice) #################


def _montar_caminho_codificacao(linha: pd.Series) -> str:
    dominio = str(linha["Domínio"]).strip()
    sub = str(linha["Sub-domínio"]).strip()
    detalhado = linha.get("Sub-domínio detalhado")
    partes = [dominio, sub]
    if pd.notna(detalhado):
        texto = str(detalhado).strip()
        if texto and texto not in {"nan", "None", "NaN", "<NA>"}:
            partes.append(texto)
    return " > ".join(partes)


def _gerar_html_tabela_generica(
    tabela: pd.DataFrame,
    titulo: str,
    caminho_html: str | Path,
    colunas: list[str] | None = None,
    alinhar_direita: list[str] | None = None,
) -> Path:
    caminho_html = Path(caminho_html)
    if not caminho_html.is_absolute():
        caminho_html = OUTPUT_DIR / caminho_html

    if colunas is None:
        colunas = list(tabela.columns)
    alinhar_direita = set(alinhar_direita or [])

    cabecalho = "".join(f"<th>{coluna}</th>" for coluna in colunas)
    linhas = []
    for _, linha in tabela.iterrows():
        celulas = []
        for coluna in colunas:
            estilo = (
                ' style="text-align: right; white-space: nowrap;"'
                if coluna in alinhar_direita
                else ""
            )
            celulas.append(f"<td{estilo}>{linha[coluna]}</td>")
        linhas.append("<tr>" + "".join(celulas) + "</tr>")

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>{titulo}</title>
    <style>
        body {{
            background: #f5f5f5;
            color: #111;
            font-family: "Times New Roman", Times, serif;
            margin: 0;
            padding: 32px;
        }}
        main {{
            background: white;
            margin: 0 auto;
            max-width: 1100px;
            padding: 40px 48px;
        }}
        h1 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 0 0 8px;
        }}
        .instrucao {{
            color: #444;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 10pt;
            margin: 0 0 24px;
        }}
        table {{
            border-collapse: collapse;
            font-size: 10.5pt;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #111;
            padding: 7px 9px;
            text-align: left;
            vertical-align: top;
        }}
        thead th {{
            background: #f0f0f0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <main>
        <h1>{titulo}</h1>
        <p class="instrucao">
            Selecione a tabela abaixo e copie (Ctrl/Cmd+C) para colar no Google Docs.
        </p>
        <table>
            <thead>
                <tr>{cabecalho}</tr>
            </thead>
            <tbody>
                {chr(10).join(linhas)}
            </tbody>
        </table>
    </main>
</body>
</html>
"""
    caminho_html.parent.mkdir(parents=True, exist_ok=True)
    caminho_html.write_text(html, encoding="utf-8")
    return caminho_html


def inventario_caminhos(
    data: pd.DataFrame,
    mostrar: bool = True,
    abrir_html: bool = False,
    caminho_html: str | Path | None = None,
) -> pd.DataFrame:
    """Inventario de caminhos de codificacao (para apendice).

    Cada linha é um caminho Domínio > Sub-domínio [> detalhado], com o número
    de passagens únicas alocadas nele.
    """
    colunas_obrigatorias = [
        "id_passagem",
        "Domínio",
        "Sub-domínio",
        "Sub-domínio detalhado",
    ]
    faltantes = [coluna for coluna in colunas_obrigatorias if coluna not in data.columns]
    if faltantes:
        raise ValueError("data deve conter as colunas: " + ", ".join(faltantes))

    base = data.copy()
    base["Caminho"] = base.apply(_montar_caminho_codificacao, axis=1)
    base["Domínio"] = base["Domínio"].astype(str).str.strip()
    base["Sub-domínio"] = base["Sub-domínio"].astype(str).str.strip()

    detalhado = base["Sub-domínio detalhado"]
    tem_det = detalhado.notna() & ~detalhado.astype(str).str.strip().isin(
        ["", "nan", "None", "NaN", "<NA>"]
    )
    base["Sub-domínio detalhado"] = detalhado.where(tem_det, pd.NA)
    base.loc[tem_det, "Sub-domínio detalhado"] = (
        base.loc[tem_det, "Sub-domínio detalhado"].astype(str).str.strip()
    )

    tabela = (
        base.groupby(
            ["Caminho", "Domínio", "Sub-domínio", "Sub-domínio detalhado"],
            dropna=False,
        )["id_passagem"]
        .nunique()
        .reset_index(name="Passagens únicas")
        .sort_values(
            ["Passagens únicas", "Domínio", "Sub-domínio", "Sub-domínio detalhado"],
            ascending=[False, True, True, True],
        )
        .reset_index(drop=True)
    )
    tabela["Sub-domínio detalhado"] = tabela["Sub-domínio detalhado"].fillna("—")
    tabela.insert(0, "#", range(1, len(tabela) + 1))

    titulo = "Inventário de caminhos de codificação"
    if mostrar:
        _mostrar_tabela_categorias(tabela, titulo)

    if abrir_html or caminho_html is not None:
        if caminho_html is None:
            caminho_html = OUTPUT_DIR / "inventario_caminhos.html"
        caminho_gerado = _gerar_html_tabela_generica(
            tabela=tabela,
            titulo=titulo,
            caminho_html=caminho_html,
            colunas=[
                "#",
                "Domínio",
                "Sub-domínio",
                "Sub-domínio detalhado",
                "Passagens únicas",
            ],
            alinhar_direita=["#", "Passagens únicas"],
        )
        if abrir_html:
            webbrowser.open(caminho_gerado.resolve().as_uri())
        if mostrar:
            print(f"\nTabela HTML salva em: {caminho_gerado}")

    return tabela


def _formatar_prevalencia(valor: float) -> str:
    texto = f"{float(valor):,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{texto}%"


_FONTE_TITULO_QUAL = 14
_FONTE_EIXO_QUAL = 12
_FONTE_TICK_QUAL = 11
_FONTE_ROTULO_QUAL = 11
_FONTE_NOTA_QUAL = 10


def plotar_categorias(
    data: pd.DataFrame,
    coluna: str = "Domínio",
    titulo: str | None = None,
    logica: LogicaCategoriasTipo = "coluna_simples",
    dominio: str | None = None,
    subdominio: str | None = None,
    agregacao_outros: bool = False,
    prevalencia: bool = False,
    tabela: bool = False,
    save_path: str | Path | None = None,
    dpi: int = 300,
    mostrar: bool = True,
):
    """Plota frequencia de categorias por passagem unica.

    Parametros
    ----------
    save_path : str | Path | None
        Caminho para salvar a figura (.png). Caminhos relativos vao para OUTPUT/.
        Se omitir a extensao, .png e adicionado automaticamente.
    prevalencia : bool
        Se True, exibe prevalencia em vez de contagens absolutas.
        Em logica='coluna_simples', divide pelo total de passagens do corpus.
        Em logica='hierarquia', divide pelas passagens do dominio selecionado.
        Em logica='subdominio_detalhado', divide pelas passagens do caminho
        dominio > subdominio.
    subdominio : str | None
        Obrigatorio quando logica='subdominio_detalhado'.
    """
    logica = _resolver_logica_categorias(logica)

    if agregacao_outros and logica != "hierarquia":
        raise ValueError(
            "agregacao_outros=True so se aplica quando logica='hierarquia'."
        )

    contagem, nome_coluna_tabela, rotulo_eixo = _contar_categorias(
        data=data,
        logica=logica,
        coluna=coluna,
        dominio=dominio,
        subdominio=subdominio,
    )

    if contagem.empty:
        raise ValueError("Nao ha dados para plotar.")

    if logica == "hierarquia":
        n_passagens_referencia = (
            data.loc[data["Domínio"].astype(str) == str(dominio).strip(), "id_passagem"]
            .nunique()
        )
        contagem = _preparar_subdominios_hierarquia(
            contagem,
            agregacao_outros=agregacao_outros,
        )
    elif logica == "subdominio_detalhado":
        n_passagens_referencia = _filtrar_caminho_codificacao(
            data, str(dominio).strip(), str(subdominio).strip()
        )["id_passagem"].nunique()
    else:
        n_passagens_referencia = data["id_passagem"].nunique()

    if titulo is None:
        if logica == "hierarquia":
            titulo = f"Frequência de Sub-domínios — {dominio}"
        elif logica == "subdominio_detalhado":
            titulo = (
                f"Prevalência de Sub-domínios detalhados — {dominio} › {subdominio}"
            )
        else:
            titulo = "Frequência de Domínios Relevantes"

    n_passagens_total = n_passagens_referencia

    tabela_df = (
        contagem.sort_values(ascending=False)
        .rename("passagens")
        .reset_index()
        .rename(columns={rotulo_eixo: nome_coluna_tabela})
    )

    if prevalencia:
        tabela_df["prevalência (%)"] = (
            tabela_df["passagens"] / n_passagens_referencia * 100
        ).map(_formatar_prevalencia)

    if tabela:
        _mostrar_tabela_categorias(tabela_df, titulo)

    try:
        import seaborn as sns

        sns.set_theme(
            context="paper",
            style="ticks",
            font="Times New Roman",
            palette="deep",
        )
    except ImportError:
        sns = None

    cor_destaque = "#91a8b8"
    cor_cinza = "#C4C4C4"
    n_categorias = len(contagem)
    cores = _cores_barras_categorias(contagem, logica, cor_destaque, cor_cinza)

    rotulos = [_quebrar_rotulo_categoria(categoria) for categoria in contagem.index.astype(str)]

    if prevalencia:
        valores_plot = contagem / n_passagens_referencia * 100
        rotulos_barras = [
            f"{_formatar_prevalencia(pct)} ({int(n)})"
            for pct, n in zip(valores_plot.values, contagem.values)
        ]
        if logica == "hierarquia":
            rotulo_eixo_x = "Prevalência no domínio (%)"
        elif logica == "subdominio_detalhado":
            rotulo_eixo_x = "Prevalência no caminho (%)"
        else:
            rotulo_eixo_x = "Prevalência (%)"
    else:
        valores_plot = contagem
        rotulos_barras = [str(int(valor)) for valor in contagem.values]
        rotulo_eixo_x = "Passagens únicas"

    fig, ax = plt.subplots(figsize=(9, max(4.8, 0.55 * n_categorias)))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    barras = ax.barh(rotulos, valores_plot.values, color=cores, edgecolor="white", linewidth=0.8)
    ax.bar_label(
        barras,
        labels=rotulos_barras,
        padding=4,
        fontsize=_FONTE_ROTULO_QUAL,
        fontfamily="Times New Roman",
    )

    ax.set_title(
        titulo,
        fontfamily="Times New Roman",
        fontsize=_FONTE_TITULO_QUAL,
        fontweight="bold",
        loc="left",
        pad=20,
    )
    ax.set_xlabel(rotulo_eixo_x, fontfamily="Times New Roman", fontsize=_FONTE_EIXO_QUAL)
    ax.set_ylabel("")
    # Mais espaço à direita quando o rótulo traz % e n.
    ax.set_xlim(0, valores_plot.max() * (1.18 if prevalencia else 1.1))
    ax.grid(False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#222222")
    ax.spines["bottom"].set_color("#222222")
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(axis="both", colors="#222222", width=0.8, labelsize=_FONTE_TICK_QUAL)

    for texto in ax.get_xticklabels() + ax.get_yticklabels():
        texto.set_fontfamily("Times New Roman")

    fig.subplots_adjust(left=0.34)

    nota_rodape = None
    if logica == "subdominio_detalhado":
        nota_rodape = (
            f"Prevalência de cada sub-domínio detalhado no caminho {dominio} › {subdominio}. "
            f"Denominador = {n_passagens_referencia} passagens no caminho. "
            "Percentagens não somam 100% quando uma passagem recebe mais de um detalhado."
        )
    elif logica == "hierarquia" and prevalencia:
        nota_rodape = (
            f"Prevalência de cada sub-domínio entre as passagens codificadas em {dominio}. "
            f"Denominador = {n_passagens_referencia} passagens no domínio. "
            "Percentagens não somam 100% quando uma passagem recebe mais de um sub-domínio."
        )

    if nota_rodape:
        fig.tight_layout(rect=[0, 0.1, 1, 1])
        fig.text(
            0.02,
            0.02,
            nota_rodape,
            transform=fig.transFigure,
            fontsize=_FONTE_NOTA_QUAL,
            fontfamily="Times New Roman",
            color="#444444",
            wrap=True,
        )
    else:
        fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)

        if save_path.suffix == "":
            save_path = save_path.with_suffix(".png")

        if not save_path.is_absolute():
            save_path = OUTPUT_DIR / save_path

        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight", facecolor="white")

        if mostrar:
            print(f"Imagem salva em: {save_path}")

    if mostrar:
        plt.show()

    return tabela_df, fig
