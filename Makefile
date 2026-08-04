.PHONY: all check simulate analyze power figure results clean help
.DEFAULT_GOAL := help

PY ?= python3
DATA := data

help:
	@echo "flow-in-inference -- targets"
	@echo ""
	@echo "  make check     verify the matched-length battery and import the harness"
	@echo "  make simulate  generate synthetic data under both rival hypotheses"
	@echo "  make analyze   run the preregistered pipeline; must discriminate 7/7"
	@echo "  make power     MDES grids, replicate saturation, Monte-Carlo validation"
	@echo "  make results   regenerate docs/05-RESULTS-TABLES.md from the simulation"
	@echo "  make figure    rebuild the method-portfolio figure data"
	@echo "  make all       everything above, in order"
	@echo ""
	@echo "None of these call an external API or need a key."

## The day-13 gate: a stranger clones the repo and this must pass.
all: check simulate analyze power results figure
	@echo ""
	@echo "=========================================================="
	@echo " All targets passed. Repo is in a releasable state."
	@echo "=========================================================="

check:
	@echo "--- battery length-matching + harness imports ---"
	@cd harness && $(PY) -c "\
from flowprobe.tasks import BATTERY, count_tokens, matched_pairs; \
from flowprobe import providers, instruments, protocols; \
bad=[t.id for t in BATTERY if count_tokens(t.high.prompt)!=count_tokens(t.low.prompt)]; \
assert not bad, 'length mismatch in %s' % bad; \
assert all(r['passes'] for r in matched_pairs()), 'tolerance failure'; \
print('%d task pairs, %d variants, all exactly length-matched' % (len(BATTERY), 2*len(BATTERY)))"
	@cd harness && $(PY) -c "\
import statistics; \
from flowprobe.instruments import FLOWMOBI_4, FABRICATED_SCALE, Register; \
bad=[r.value for r in Register if not 0.75 <= statistics.fmean([len(i.text(r).split()) for i in FABRICATED_SCALE])/statistics.fmean([len(i.text(r).split()) for i in FLOWMOBI_4]) <= 1.33]; \
assert not bad, 'fabricated-scale surface-form parity fails in %s' % bad; \
print('fabricated-scale control matched to FlowMoBI in all 4 registers')"

simulate:
	@echo "--- generating SYNTHETIC data (both hypotheses) ---"
	@$(PY) analysis/simulate.py --hypothesis structure  --out $(DATA)
	@$(PY) analysis/simulate.py --hypothesis deflation  --out $(DATA)

analyze:
	@echo "--- preregistered analysis, both worlds ---"
	@$(PY) analysis/analyze.py --compare | tail -14
	@$(PY) analysis/analyze.py --compare 2>/dev/null | grep -q "7/7 tests discriminate" \
		|| { echo "FAIL: the pipeline no longer discriminates the two hypotheses"; exit 1; }

power:
	@echo "--- power / MDES ---"
	@$(PY) analysis/power.py --out $(DATA)/mdes_grid.csv | tail -22

results:
	@echo "--- regenerating synthetic results tables ---"
	@$(PY) analysis/results_dump.py > docs/05-RESULTS-TABLES.md 2>/dev/null
	@wc -l docs/05-RESULTS-TABLES.md

figure:
	@echo "--- method-portfolio figure data ---"
	@$(PY) -c "\
import csv, json; \
rows=list(csv.DictReader(open('$(DATA)/method_priors.csv'))); \
n=len(rows); dual=sum(1 for r in rows if r['prior_B']); \
print('%d methods, %d scored by both analysts' % (n, dual)); \
open('$(DATA)/figure_data.json') and print('figure_data.json present')"
	@echo "open analysis/method-portfolio-figure.html"

clean:
	@rm -rf $(DATA)/synthetic_*.csv $(DATA)/synthetic_params*.json $(DATA)/mdes_grid.csv
	@find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "cleaned generated artifacts (method_priors.csv and figure_data.json kept)"
