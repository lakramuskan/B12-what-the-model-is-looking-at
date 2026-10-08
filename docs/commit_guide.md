# Four people, four real commits (graded: "commits show four people working")
Do NOT commit for each other from one account. Each person clones, adds their own files, commits under their own Git identity, pushes.

One-time setup for everyone:
    git clone https://github.com/lakramuskan/B12-what-the-model-is-looking-at.git
    cd B12-what-the-model-is-looking-at
    git config user.name "Your Name"; git config user.email "your-github-email"
Muskan first pushes (data/raw/scorecards/ is 14 MB; fine for GitHub) the full project folder (the zip contents) in one commit, then the others pull and add:

| Person | Files they own and should commit/extend | Commit message (write what changed) |
|---|---|---|
| Muskan | README.md, INTEGRATION.md, Makefile, requirements.txt, .gitignore, src/make_report.py, paper/ | initialize B12 repository structure, README and integration note |
| Pooja | docs/data_notes.md, src/build_dataset.py, data/README.md, src/data_loader.py, src/features.py, notebooks/01_exploration.ipynb, docs/observations.md | add data contract notes, loader, momentum features and exploration notebook |
| Kunal | docs/model_plan.md, src/model.py, src/train.py, src/plots.py, results/plots/ | add gradient boosting model, SHAP importance and interaction pipeline |
| Samarth | docs/evaluation_plan.md, src/evaluate.py, src/analysis.py, src/compare_b1.py, tests/, experiments.csv, docs/literature_table.md | add baseline evaluation, failure and robustness analysis, tests and literature table |

Each person: `git pull`, edit/review their files (make at least one real change, e.g. rewrite your docs in your own words), `git add <your files>`, `git commit -m "<message>"`, `git push`.
Better still: split the first push so the history shows real work over several days (commit each file as you actually review it).
Rename the repo (or note why not) to sequence-b12-what-the-model-is-looking-at to match Rule 3.
