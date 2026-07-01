from pathlib import Path
import scanpy as sc


def load_adata(path: str):
    """
    Load an AnnData object from an .h5ad file.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Could not find file: {path}")

    if path.suffix != ".h5ad":
        raise ValueError("SingleCellAgent currently expects an .h5ad file.")

    adata = sc.read_h5ad(path)
    return adata
