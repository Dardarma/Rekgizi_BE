from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from typing import Any


MODEL_PATH = Path(__file__).resolve().parent / "model_rekomendasi_diet_ginjal.joblib"

MODEL_FEATURES = (
    "BB",
    "Ureum",
    "Creatinin",
    "Kelebihan Natrium",
    "Kelebihan Karbohidrat",
    "Darah Tinggi",
    "Diabetes",
    "Edema",
    "Tekanan_Sistolik",
    "Tekanan_Diastolik",
)


class ModelInputError(ValueError):
    pass


@lru_cache(maxsize=1)
def load_model_bundle() -> dict[str, Any]:
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError(
            "Dependency ML belum terpasang. Jalankan `pip install -r requirements.txt`."
        ) from exc

    if not MODEL_PATH.exists():
        raise RuntimeError(f"File model tidak ditemukan: {MODEL_PATH}")

    bundle = joblib.load(MODEL_PATH)
    required_keys = {
        "model_decision_tree",
        "feature_cols_tree",
        "model_cluster_rp",
        "model_cluster_dialisa",
    }
    missing_keys = required_keys - set(bundle)
    if missing_keys:
        raise RuntimeError(f"Struktur model tidak lengkap: {sorted(missing_keys)}")
    return bundle


def _build_feature_frame(payload: Mapping[str, Any]):
    try:
        import numpy as np
        import pandas as pd
    except ImportError as exc:
        raise RuntimeError(
            "Dependency ML belum terpasang. Jalankan `pip install -r requirements.txt`."
        ) from exc

    missing = [name for name in MODEL_FEATURES if payload.get(name) is None]
    if missing:
        raise ModelInputError(f"Fitur model belum lengkap: {', '.join(missing)}")

    frame = pd.DataFrame(
        [{name: payload[name] for name in MODEL_FEATURES}],
        columns=list(MODEL_FEATURES),
    )
    frame = frame.apply(pd.to_numeric, errors="coerce")

    invalid = [name for name in MODEL_FEATURES if not np.isfinite(frame.at[0, name])]
    if invalid:
        raise ModelInputError(f"Fitur model bukan angka yang valid: {', '.join(invalid)}")

    binary_features = (
        "Kelebihan Natrium",
        "Kelebihan Karbohidrat",
        "Darah Tinggi",
        "Diabetes",
        "Edema",
    )
    invalid_binary = [
        name for name in binary_features if frame.at[0, name] not in (0, 1)
    ]
    if invalid_binary:
        raise ModelInputError(
            f"Fitur biner harus bernilai 0 atau 1: {', '.join(invalid_binary)}"
        )

    return frame


def _get_cluster_label(labels: Any, cluster: int) -> str:
    if isinstance(labels, Mapping):
        label = labels.get(cluster, labels.get(str(cluster)))
    else:
        try:
            label = labels[cluster]
        except (IndexError, KeyError, TypeError) as exc:
            raise RuntimeError(f"Label untuk cluster {cluster} tidak ditemukan") from exc

    if label is None:
        raise RuntimeError(f"Label untuk cluster {cluster} tidak ditemukan")
    return str(label).strip()


def _predict_subcluster(model_config: Mapping[str, Any], feature_frame) -> str:
    import numpy as np

    feature_columns = list(model_config["feature_columns"])
    cluster_frame = feature_frame.loc[:, feature_columns].astype(float).copy()

    numeric_columns = list(model_config.get("num_cols", []))
    scaler = model_config.get("scaler")
    if scaler is not None and numeric_columns:
        cluster_frame.loc[:, numeric_columns] = scaler.transform(
            cluster_frame.loc[:, numeric_columns]
        )

    weights = model_config.get("feature_weights")
    if isinstance(weights, Mapping):
        for column, weight in weights.items():
            if column in cluster_frame.columns:
                cluster_frame.loc[:, column] *= float(weight)
    elif weights is not None:
        weights_array = np.asarray(weights, dtype=float).reshape(-1)
        if len(weights_array) == len(cluster_frame.columns):
            cluster_frame = cluster_frame * weights_array

    cluster = int(model_config["kmeans_model"].predict(cluster_frame)[0])
    return _get_cluster_label(model_config["label_dominan_cluster"], cluster)


def predict_diet_service(payload: Mapping[str, Any]) -> str:
    """Prediksi label diet akhir, misalnya ``RP 40`` atau ``Dialisa 70``."""
    bundle = load_model_bundle()
    feature_frame = _build_feature_frame(payload)

    tree_columns = list(bundle.get("feature_cols_tree", MODEL_FEATURES))
    primary_class = str(
        bundle["model_decision_tree"].predict(feature_frame.loc[:, tree_columns])[0]
    ).strip()

    normalized_class = primary_class.casefold()
    if normalized_class == "rp":
        model_config = bundle["model_cluster_rp"]
    elif normalized_class == "dialisa":
        model_config = bundle["model_cluster_dialisa"]
    else:
        raise RuntimeError(f"Kelas Decision Tree tidak dikenali: {primary_class}")

    return _predict_subcluster(model_config, feature_frame)
