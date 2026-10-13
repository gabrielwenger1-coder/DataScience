"""Lecture et écriture de fichiers Parquet, sur S3 ou en local selon l'environnement."""

import io
import os

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq
import s3fs
from fsspec import AbstractFileSystem
from fsspec.implementations.local import LocalFileSystem

from cadres_lycees import config


def _systeme_fichiers(chemin: str) -> tuple[AbstractFileSystem, str]:
    """Renvoie le système de fichiers à utiliser et le chemin complet de `chemin` dedans.

    `chemin` est relatif à la racine du stockage du projet, par exemple "raw/annuaire.parquet".
    Les valeurs des identifiants ne sont jamais lues ici : s3fs les prend dans l'environnement.
    """
    if all(variable in os.environ for variable in config.VARIABLES_AWS):
        assert config.VARIABLE_BUCKET_S3 in os.environ, (
            f"Identifiants AWS trouvés mais pas {config.VARIABLE_BUCKET_S3} : "
            "définir le nom du bucket (voir README)."
        )
        bucket = os.environ[config.VARIABLE_BUCKET_S3]
        return s3fs.S3FileSystem(), f"{bucket}/{config.PREFIXE_S3}/{chemin}"
    return LocalFileSystem(auto_mkdir=True), f"{config.DOSSIER_LOCAL}/{chemin}"


def ecrire_octets(octets: bytes, chemin: str) -> None:
    """Écrit `octets` tels quels à `chemin` (copie brute d'une source)."""
    systeme, complet = _systeme_fichiers(chemin)
    systeme.pipe_file(complet, octets)


def ecrire_parquet(df: pd.DataFrame, chemin: str) -> None:
    """Écrit `df` en Parquet à `chemin`. Un GeoDataFrame est écrit en GeoParquet."""
    # Sérialiser en mémoire d'abord : si to_parquet échoue, aucun fichier partiel ne reste,
    # et existe() ne le prendra pas pour un succès (la collecte ne le retélécharge pas).
    tampon = io.BytesIO()
    df.to_parquet(tampon)
    ecrire_octets(tampon.getvalue(), chemin)


def lire_parquet(chemin: str) -> pd.DataFrame:
    """Lit le Parquet à `chemin` ; un GeoParquet revient en GeoDataFrame.

    Il faut distinguer les deux : `pd.read_parquet` lirait la géométrie comme des octets
    bruts, sans erreur, et les jointures spatiales échoueraient beaucoup plus loin.
    """
    systeme, complet = _systeme_fichiers(chemin)
    with systeme.open(complet, "rb") as fichier:
        metadonnees = pq.read_schema(fichier).metadata or {}
        fichier.seek(0)
        if b"geo" in metadonnees:
            return gpd.read_parquet(fichier)
        return pd.read_parquet(fichier)


def existe(chemin: str) -> bool:
    """Indique si le fichier `chemin` existe, pour ne pas retélécharger une source (PLAN §8.2)."""
    systeme, complet = _systeme_fichiers(chemin)
    return systeme.exists(complet)
