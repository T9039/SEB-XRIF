"""Unsupervised views: a PCA projection and KMeans cluster profiles."""

from __future__ import annotations

from typing import Any

from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .config import Settings, get_settings
from .data import features_and_target, load_source
from .schema import BEHAVIOURAL


def compute_embedding(
    settings: Settings | None = None, n_clusters: int = 3
) -> dict[str, Any]:
    """Project learners to 2-D with PCA and cluster them with KMeans."""
    settings = settings or get_settings()
    frame, source = load_source(settings)
    features, target = features_and_target(frame, settings)

    numeric = features[BEHAVIOURAL].astype(float).to_numpy()
    scaled = StandardScaler().fit_transform(numeric)

    pca = PCA(n_components=2, random_state=settings.seed)
    coordinates = pca.fit_transform(scaled)
    clusters = KMeans(
        n_clusters=n_clusters, random_state=settings.seed, n_init=10
    ).fit_predict(scaled)

    points = [
        {
            "x": round(float(coordinates[index, 0]), 4),
            "y": round(float(coordinates[index, 1]), 4),
            "tier": str(target.iloc[index]),
            "cluster": int(clusters[index]),
        }
        for index in range(len(coordinates))
    ]

    values = features[BEHAVIOURAL].to_numpy()
    profiles = []
    for column_index, behaviour in enumerate(BEHAVIOURAL):
        row: dict[str, Any] = {"x": behaviour}
        for cluster in range(n_clusters):
            mask = clusters == cluster
            row[str(cluster)] = round(float(values[mask, column_index].mean()), 3)
        profiles.append(row)

    return {
        "data_source": source,
        "n_clusters": n_clusters,
        "explained_variance": [
            round(float(value), 4) for value in pca.explained_variance_ratio_
        ],
        "points": points,
        "profiles": profiles,
        "clusters": [str(cluster) for cluster in range(n_clusters)],
    }
