"""Ablation Runner Placeholder
Toggle components and recompute dummy metrics.
"""
import argparse

COMPONENTS = ['graph','shap','ensemble','optimizations','adaptive_weights']


def simulate_result(enabled):
    base_f1 = 0.90
    if 'graph' not in enabled:
        base_f1 -= 0.04
    if 'shap' not in enabled:
        base_f1 -= 0.002
    if 'ensemble' not in enabled:
        base_f1 -= 0.02
    if 'optimizations' not in enabled:
        pass
    if 'adaptive_weights' not in enabled:
        base_f1 -= 0.009
    return round(base_f1,3)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--disable', nargs='*', default=[])
    args=ap.parse_args()
    enabled = [c for c in COMPONENTS if c not in args.disable]
    f1 = simulate_result(enabled)
    print({'enabled':enabled,'f1_score':f1})

if __name__=='__main__':
    main()
