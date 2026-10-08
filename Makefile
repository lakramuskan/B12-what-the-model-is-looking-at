.PHONY: all dataset run analysis b1 plots report test docx slides synthetic clean
# Full pipeline on the real scorecards (about 8-10 minutes on a laptop; see README)
all: dataset run analysis b1 plots report test
dataset:   ; python src/build_dataset.py
run:       ; : > experiments.csv; PYTHONPATH=src python src/train.py --seeds 10
analysis:  ; PYTHONPATH=src python src/analysis.py
b1:        ; PYTHONPATH=src python src/compare_b1.py
plots:     ; PYTHONPATH=src python src/plots.py
report:    ; PYTHONPATH=src python src/make_report.py
test:      ; PYTHONPATH=src python -m pytest -q tests
docx:      ; cd paper && pandoc paper.md -o paper.docx --resource-path=. --from markdown+implicit_figures
slides:    ; python slides/make_data.py && cd slides && node build_deck.js
synthetic: ; python src/make_synthetic.py        # test fallback only, never report from it
