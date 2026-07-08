import argparse
from pathlib import Path

from .observability import DEFAULT_LOG_PATH
from .report import build_report
from .validate_cli import DEFAULT_DECISIONS_PATH


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Statistiques sur les analyses passées : score moyen, coûts, et corrélation "
            "entre le score de l'agent et les décisions humaines (ao-agent-validate)."
        )
    )
    parser.add_argument("--log-path", type=Path, default=DEFAULT_LOG_PATH, help="Journal des analyses")
    parser.add_argument(
        "--decisions-path", type=Path, default=DEFAULT_DECISIONS_PATH, help="Journal des décisions"
    )
    args = parser.parse_args()

    report = build_report(args.log_path, args.decisions_path)

    print(f"Nombre d'analyses : {report['nombre_analyses']}")
    print(f"Score moyen donné par l'agent : {report['score_moyen']}")
    print(
        f"Tokens (entrée / sortie, total) : {report['tokens_entree_total']} / {report['tokens_sortie_total']}"
    )
    print(f"Durée moyenne par analyse : {report['duree_moyenne_secondes']} s")
    print()

    if report["score_moyen_par_decision"]:
        print(
            f"Score moyen de l'agent par décision humaine "
            f"(sur {report['nombre_decisions_liees']} analyses validées) :"
        )
        for decision, avg in report["score_moyen_par_decision"].items():
            print(f"  - {decision} : {avg}")
    else:
        print("Aucune décision humaine liée à une analyse pour l'instant (utilisez ao-agent-validate).")


if __name__ == "__main__":
    main()
