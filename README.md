# Huntable-SIGMA-Rules
Curated, high-signal Sigma detection rules crafted by the workflow from Huntable CTI Studio
 rules derived from threat intelligence analysis and manual review.

This repository is content-only. It contains detection rules, validation metadata, and supporting CI — not application code.

---

## Scope & Philosophy

- Rules are based on explicitly observable behavior
- Rules may originate from automation but are human-reviewed

----

## Rule Standards

All rules must:

- Pass Sigma validation (pySigma / sigma-cli)
- Have a unique id
- Include meaningful title, description, and references

Experimental or campaign-specific rules should be marked accordingly (e.g. status: experimental).

---

## CI Checks

Pull requests are automatically checked for:

- YAML syntax and linting
- Sigma schema validity
- Duplicate or near-duplicate detection logic
- Required field presence and conventions

Pull requests failing checks will not merge.

---

## Contribution Workflow

1. New rules are added via pull request
2. CI validates structure and novelty
3. Manual review focuses on:
   - Behavioral clarity
   - False positive risk
   - Long-term usefulness

External contributions are welcome but subject to the same gates.

---

## Relationship to SigmaHQ

This repository is not a mirror of SigmaHQ.

- New rules have passed a novelty test against SigmaHQ before being pushed here (similar to the methods used in https://github.com/dfirtnt/SIGMASimTest). 
- SigmaHQ PRs are selective and intentional, not automatic

---

## License

Unless otherwise stated, rules are released under the same permissive license as the Sigma project to enable reuse and collaboration.

---

## Disclaimer

Rules are provided as-is. Detection efficacy depends on telemetry quality, backend implementation, and environment-specific tuning.
