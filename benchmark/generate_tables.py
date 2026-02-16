"""Generate LaTeX Tables (Placeholder)
"""

def table_perf():
    rows = [
        ('LogReg',0.892,0.634,0.587,0.610),
        ('RandomForest',0.941,0.892,0.867,0.879),
        ('XGBoost',0.953,0.908,0.881,0.894),
        ('Autoencoder',0.927,0.875,0.842,0.858),
        ('GNNOnly',0.962,0.921,0.895,0.908),
        ('OurMethod',0.974,0.943,0.918,0.930)
    ]
    print("\\begin{tabular}{lcccc}")
    print("Method & Acc & Prec & Rec & F1 \\\")
    print("\\hline")
    for r in rows:
        print(f"{r[0]} & {r[1]:.3f} & {r[2]:.3f} & {r[3]:.3f} & {r[4]:.3f} \\")
    print("\\end{tabular}")

if __name__=='__main__':
    table_perf()
