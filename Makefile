.PHONY: help up up-all down test e2e smoke prometheus-test ui-build sync-chart helm-lint
help:           ## list targets
	@grep -E '^[a-z0-9-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/ -\t/'
up:             ## core stack (api, canary-listener, ui, postgres)
	docker compose up -d --build
up-all:         ## core + honeypot + ELK
	docker compose --profile honeypot --profile elk up -d --build
down:           ## stop everything
	docker compose --profile honeypot --profile elk down
test:           ## run all unit tests
	cd services/api && python -m pytest -q
	cd services/canary-listener && python -m pytest -q
	cd services/generator && python -m pytest -q
e2e:            ## full flow without Docker: generator -> trap -> alert, incl. API outage
	python tests/e2e/run_e2e.py
smoke:          ## full-stack test against a RUNNING `make up-all` stack (needs .env, paramiko)
	python tests/e2e/compose_smoke.py --env-file .env
prometheus-test: ## unit-test the chart's alert rules with promtool (needs helm + docker)
	./tests/prometheus/run.sh
ui-build:       ## typecheck + build the dashboard
	cd services/ui && npm ci && npm run build

sync-chart:     ## copy pipeline configs into the Helm chart (run after editing pipeline/)
	cp pipeline/filebeat/filebeat.yml deploy/helm/deception-platform/files/filebeat.yml
	cp pipeline/logstash/pipeline/honeypot.conf deploy/helm/deception-platform/files/logstash-honeypot.conf
	cp pipeline/elasticsearch/*.json pipeline/kibana/deception.ndjson pipeline/setup.sh deploy/helm/deception-platform/files/
helm-lint:      ## lint + render the chart
	helm lint deploy/helm/deception-platform $(HELM_ARGS)
