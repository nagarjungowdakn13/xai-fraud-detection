"""Utility to set global deterministic seeds across libraries.
Run: python scripts/set_global_seed.py 42
Optionally import set_seed(seed) in training scripts.
"""
import os
import sys
import random

try:
    import numpy as np
except ImportError:
    np = None

try:
    import torch
except ImportError:
    torch = None


def set_seed(seed: int):
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/set_global_seed.py <seed>")
        return
    seed = int(sys.argv[1])
    set_seed(seed)
    print(f"Seeds set to {seed}")

if __name__ == "__main__":
    main()
