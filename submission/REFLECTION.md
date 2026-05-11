# Day 23 Lab Reflection

> Fill in each section. Grader reads the "What I'd change" paragraph closest.

**Student:** Trịnh Đức An
**Submission date:** _2026-05-11_
**Lab repo URL:** https://github.com/trhndan21/Day23-Track2-Observability-Lab

---

## 1. Hardware + setup output

Paste output of `python3 00-setup/verify-docker.py`:

```text
Docker:        OK  (28.4.0)
Compose v2:    OK  (2.39.2-desktop.1)
RAM available: 5.79 GB (OK)
Ports free:    BOUND: [8000, 9090, 9093, 3000, 3100, 16686, 4317, 4318, 8888]
Report written: /Users/tda/Downloads/Day23-Track2-Observability-Lab/00-setup/setup-report.json
```

---

## 2. Track 02 — Dashboards & Alerts

### 6 essential panels (screenshot)

Drop `submission/screenshots/dashboard-overview.png`.

### Burn-rate panel

Drop `submission/screenshots/slo-burn-rate.png`.

### Alert fire + resolve

| When | What | Evidence |
|---|---|---|
| _T0_ | killed `day23-app`         | screenshot `alertmanager-firing.png` |
| _T0+90s_ | `ServiceDown` fired   | screenshot `slack-firing.png` |
| _T1_ | restored app              | — |
| _T1+60s_ | alert resolved        | screenshot `slack-resolved.png` |

### One thing surprised me about Prometheus / Grafana

It surprised me how seamlessly Grafana integrates with Prometheus just by providing the endpoint URL. Writing PromQL queries directly in Grafana to visualize raw metrics as beautiful dashboards without any middleware is incredibly powerful.

---

## 3. Track 03 — Tracing & Logs

### One trace screenshot from Jaeger

Drop `submission/screenshots/jaeger-trace.png` showing `embed-text → vector-search → generate-tokens` spans.

### Log line correlated to trace

Paste the log line and the trace_id it links to:

```json
{"model": "llama3-mock", "input_tokens": 4, "output_tokens": 54, "quality": 0.82, "duration_seconds": 15.1679, "trace_id": "2cfb529e3c578681387e306a79bd9853", "event": "prediction served", "level": "info", "timestamp": "2026-05-11T05:12:36.883785Z"}
```
Linked Trace ID: `2cfb529e3c578681387e306a79bd9853`

### Tail-sampling math

If your service produced N traces/sec, what fraction did the policy keep? Show the calculation.

Based on our `otel-config.yaml` policies (`keep-errors`, `keep-slow`, `probabilistic-1pct`):
- It keeps 100% of errors (HTTP 500/503).
- It keeps 100% of slow traces (> 2000ms latency).
- For the remaining healthy and fast traces, it keeps 1% (0.01).

Fraction kept = `(1.0 * N_errors + 1.0 * N_slow + 0.01 * N_healthy_fast) / N`

---

## 4. Track 04 — Drift Detection

### PSI scores

Paste `04-drift-detection/reports/drift-summary.json`:

```json
{
  "prompt_length": {
    "psi": 3.461,
    "kl": 1.7982,
    "ks_stat": 0.702,
    "ks_pvalue": 0.0,
    "drift": "yes"
  },
  "embedding_norm": {
    "psi": 0.0187,
    "kl": 0.0324,
    "ks_stat": 0.052,
    "ks_pvalue": 0.133853,
    "drift": "no"
  },
  "response_length": {
    "psi": 0.0162,
    "kl": 0.0178,
    "ks_stat": 0.056,
    "ks_pvalue": 0.086899,
    "drift": "no"
  },
  "response_quality": {
    "psi": 8.8486,
    "kl": 13.5011,
    "ks_stat": 0.941,
    "ks_pvalue": 0.0,
    "drift": "yes"
  }
}
```

### Which test fits which feature?

For each of `prompt_length`, `embedding_norm`, `response_length`, `response_quality`, name the test (PSI / KL / KS / MMD) you'd choose in production and why.

- **prompt_length**: KS (Kolmogorov-Smirnov). It is a continuous numerical feature, and KS is robust for comparing continuous distributions.
- **embedding_norm**: KS or MMD. Since it's derived from embeddings, MMD (Maximum Mean Discrepancy) is mathematically excellent for high-dimensional distribution shifts.
- **response_length**: KS test (continuous) to accurately measure shifts in continuous output length distributions.
- **response_quality**: PSI (Population Stability Index). Quality score is bounded (0-1), meaning we can easily bin it into categories (e.g., poor, fair, good) and compute PSI to evaluate population shifts across buckets.

---

## 5. Track 05 — Cross-Day Integration

### Which prior-day metric was hardest to expose? Why?

The Day 19 vector-store integration was challenging because we needed to ensure Prometheus inside the Docker network could correctly scrape metrics from a stub Python script running directly on the Mac host (`host.docker.internal`). Configuring `prometheus.yml` to bridge this network gap required careful attention to Docker networking rules.

---

## 6. The single change that mattered most

> **Grader reads this closest.** What one thing about your stack design — a metric you added, a label you dropped, a panel you reorganized, an alert threshold you tuned — made the biggest difference between "works" and "useful"? Write 1-2 paragraphs. Connect it to a concept from the deck.

The most impactful change was correctly structuring the OpenTelemetry traces by using `tracer.start_as_current_span` context managers instead of flat, disconnected manual spans. Initially, the spans for `embed-text`, `vector-search`, and `generate-tokens` were independent traces. While technically "working" (they were emitting data), it was impossible to see the end-to-end latency breakdown of a single `predict` request. 

By properly nesting them as child spans under the parent `predict` span, we unlocked the full power of distributed tracing in Jaeger. This directly aligns with the core concept of **context propagation** discussed in the deck. It transformed our observability from merely "working" to "useful", allowing us to instantly identify latency bottlenecks visually via flame graphs.
