"""
Utilitário CLI para executar consultas manuais e inspecionar os resultados e telemetria.
Uso:
  python scripts/query_cli.py "minha internet caiu" --tipo semantic
  python scripts/query_cli.py "minha internet caiu" --tipo lexical
  python scripts/query_cli.py "erro dpkg" --tipo semantic --categoria "Gerenciamento de Pacotes"
"""

import sys
import os
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from app.services.search_service import search_service

console = Console()

def main():
    parser = argparse.ArgumentParser(description="CLI de Consulta de Busca Semântica e Lexical (TCC UTFPR)")
    parser.add_argument("query", type=str, help="Texto da dúvida ou chamado técnico")
    parser.add_argument("--tipo", choices=["semantic", "lexical"], default="semantic", help="Tipo de motor de busca")
    parser.add_argument("--top", type=int, default=5, help="Quantidade de resultados Top-N")
    parser.add_argument("--categoria", type=str, default=None, help="Pré-filtragem por categoria")
    parser.add_argument("--fonte", choices=["Microsoft", "Ubuntu"], default=None, help="Filtrar por fonte")

    args = parser.parse_args()

    console.print(Panel.fit(
        f"[bold cyan]Consulta:[/bold cyan] {args.query}\n"
        f"[bold yellow]Tipo de Busca:[/bold yellow] {args.tipo.upper()}\n"
        f"[bold magenta]Pré-filtro Categoria:[/bold magenta] {args.categoria or 'Nenhum'}\n"
        f"[bold magenta]Pré-filtro Fonte:[/bold magenta] {args.fonte or 'Nenhum'}",
        title="[bold green]Mecanismo de Busca Help Desk[/bold green]"
    ))

    if args.tipo == "semantic":
        res = search_service.semantic_search(
            query=args.query,
            top_n=args.top,
            categoria=args.categoria,
            fonte=args.fonte
        )
    else:
        res = search_service.lexical_search(
            query=args.query,
            top_n=args.top,
            categoria=args.categoria,
            fonte=args.fonte
        )

    table = Table(title=f"Resultados Top-{args.top} Recuperados ({res.tipo_busca})", show_lines=True)
    table.add_column("Rank", justify="center", style="bold")
    table.add_column("Doc ID", justify="center")
    table.add_column("Fonte / Categoria", style="cyan")
    table.add_column("Título", style="bold white")
    table.add_column("Score / Distância", justify="center", style="green")
    table.add_column("Trecho do Conteúdo", style="dim")

    for idx, item in enumerate(res.resultados, 1):
        score_info = f"Score: {item.score:.4f}"
        if item.distancia_cosseno is not None:
            score_info += f"\n(Dist: {item.distancia_cosseno:.4f})"

        trecho = (item.conteudo[:180] + "...") if len(item.conteudo) > 180 else item.conteudo
        table.add_row(
            str(idx),
            str(item.documento_id),
            f"{item.fonte}\n[{item.categoria}]",
            item.titulo,
            score_info,
            trecho
        )

    console.print(table)

    console.print(Panel(
        f"[bold]T_emb (Inferência vetorial):[/bold] {res.telemetria.t_emb_ms:.2f} ms\n"
        f"[bold]T_sql (Busca & Ordenação PostgreSQL):[/bold] {res.telemetria.t_sql_ms:.2f} ms\n"
        f"[bold green]T_total (Latência Total):[/bold green] {res.telemetria.t_total_ms:.2f} ms",
        title="[bold blue]Telemetria Computacional[/bold blue]",
        expand=False
    ))

if __name__ == "__main__":
    main()

