"""Stratified Chronological K-Fold Runner (Placeholder)
"""
import argparse, csv, datetime
from pathlib import Path
import numpy as np
from sklearn.model_selection import StratifiedKFold


def load_labels(path):
    y=[];X=[]
    with open(path,'r') as f:
        r=csv.DictReader(f)
        for row in r:
            y.append(int(row['label']))
            X.append([float(row['amount'])])
    return np.array(X), np.array(y)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--folds', type=int, default=5)
    args=ap.parse_args()
    X,y=load_labels(args.input)
    skf=StratifiedKFold(n_splits=args.folds, shuffle=True, random_state=42)
    for i,(tr,va) in enumerate(skf.split(X,y), start=1):
        print({'fold':i,'train_size':len(tr),'val_size':len(va),'fraud_ratio_train':float(y[tr].mean()),'fraud_ratio_val':float(y[va].mean())})

if __name__=='__main__':
    main()
