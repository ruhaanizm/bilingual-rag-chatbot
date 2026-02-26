# pipeline/utils.py

import hashlib
import random
import numpy as np


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()