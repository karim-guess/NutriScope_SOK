import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from IPython.display import Image, display

def figure(fig: plt.Figure, nom: str) -> None:
    """sauvegarde dans figures/ puis affiche l'image."""

    output_file = os.path.join("figures", f"{nom}.png")

    fig.savefig(output_file, bbox_inches="tight", dpi=150)

    plt.close(fig)

    display(Image(filename=output_file))

def resume_univarie(s: pd.Series) -> pd.Series:
    x = s.dropna()
    q1, med, q3 = x.quantile([0.25, 0.5, 0.75])
    return pd.Series({
        "n": len(x), "manquants" : s.isna().sum(), "moyenne" : x.mean(), "mediane" : med,
        "ecart_type": x.std(), "IQR" : q3 - q1, "MAD" : stats.median_abs_deviation(x),
        "CV" : x.std() / x.mean(), "asymetrie" : x.skew(), "aplatissement" : x.kurt(),
        'p05': x.quantile(0.05),
        'p95': x.quantile(0.95),
        "min": x.min(), "max" : x.max()
    })

def profil_par_rayon(df: pd.DataFrame, colonnes_nutriments: list[str], min_n: int = 30) -> pd.DataFrame:
    """
    Filtre les rayons (< min_n écartés et listés), calcule les médianes, quartiles (Q1/Q3), moyennes et effectifs
    """
    RAYON = "pnns_groups_1"

    comptage_rayon = df[RAYON].value_counts()
    rayons_ecartes = comptage_rayon[comptage_rayon < min_n].index.tolist()

    print(f"--- LISTE DES RAYONS ÉCARTÉS (Effectif < {min_n}) ---")
    if rayons_ecartes:
        for r in rayons_ecartes:
            print(f"• {r} (n = {comptage_rayon[r]})")
    else:
        print("Aucun rayon écarté.")

    # Filtrage : conservation uniquement des groupes valides
    df_valide = df[df[RAYON].isin(comptage_rayon[comptage_rayon >= min_n].index)].copy()

    lignes_bilan = []

    for nom_rayon, groupe in df_valide.groupby(RAYON, observed=True):
        for nutriment in colonnes_nutriments:
            valeurs = groupe[nutriment].dropna()
            if len(valeurs) > 0:
                lignes_bilan.append(
                    {
                        "rayon": nom_rayon,
                        "nutriment": nutriment,
                        "effectif": len(valeurs),
                        "moyenne": valeurs.mean(),
                        "mediane": valeurs.median(),
                        "q1": valeurs.quantile(0.25),
                        "q3": valeurs.quantile(0.75),
                    }
                )

    df_stats = pd.DataFrame(lignes_bilan).set_index(["nutriment", "rayon"])

    return df_stats