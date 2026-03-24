# Psychometric Diagnosis Skill

## Purpose
Given any item-level response data and a user-specified construct, classify individuals into diagnostic categories using three psychometric approaches: (1) sum score cut-off, (2) Item Response Theory (IRT), and (3) Diagnostic Classification Models (DCM). Generate a structured report comparing results across methods.

This skill is instrument-agnostic. The user supplies the data, item descriptions, and domain context. The LLM selects appropriate parameters and interprets the output.

---

## Method A: Sum Score Cut-off

```r
diagnose_cutoff <- function(data,
                             cutoff,
                             severity_breaks = NULL,
                             severity_labels = NULL) {
  # data: data frame of item responses (rows = persons, cols = items)
  # cutoff: numeric threshold; sum score >= cutoff -> diagnosed
  # severity_breaks/labels: optional, for ordinal severity banding

  sum_scores <- rowSums(data, na.rm = TRUE)
  diagnosed  <- as.integer(sum_scores >= cutoff)

  result <- data.frame(
    id        = seq_len(nrow(data)),
    sum_score = sum_scores,
    cutoff    = cutoff,
    diagnosed = diagnosed
  )

  if (!is.null(severity_breaks) && !is.null(severity_labels)) {
    result$severity <- cut(sum_scores,
                           breaks = severity_breaks,
                           labels = severity_labels,
                           right  = TRUE)
  }

  result
}
```

**When to use:** Quick screening; validated cut-offs exist for the instrument (e.g., PHQ-9 >= 10, PCL-5 >= 33, GAD-7 >= 10).

---

## Method B: IRT — Graded Response Model

```r
# Requires: install.packages("mirt")
library(mirt)

fit_irt <- function(data,
                    itemtype     = "graded",  # "graded", "gpcm", "2PL", "3PL"
                    theta_cutoff = 0) {
  # data: data frame of item responses
  # itemtype: mirt item model; use "graded" for polytomous, "2PL" for binary
  # theta_cutoff: latent trait threshold for classification (default 0 = population mean)

  fit <- mirt(data     = data,
              model    = 1,
              itemtype = itemtype,
              verbose  = FALSE)

  theta <- fscores(fit, method = "EAP", full.scores.SE = TRUE)

  data.frame(
    id           = seq_len(nrow(data)),
    theta        = theta[, 1],
    theta_se     = theta[, 2],
    theta_cutoff = theta_cutoff,
    diagnosed    = as.integer(theta[, 1] >= theta_cutoff),
    ci_lower     = theta[, 1] - 1.96 * theta[, 2],
    ci_upper     = theta[, 1] + 1.96 * theta[, 2]
  )
}

get_irt_item_params <- function(fit) {
  coef(fit, simplify = TRUE, IRTpars = TRUE)$items
}
```

**When to use:** When individual-level measurement uncertainty matters; when items have varying discrimination; when the scale is polytomous or mixed.

---

## Method C: Diagnostic Classification Model (DCM)

```r
# Requires: install.packages("CDM")
library(CDM)

fit_dcm <- function(data,
                    q_matrix  = NULL,
                    theta_k   = c(0, 1),
                    prob_cutoff = 0.5) {
  # data: data frame of item responses
  # q_matrix: optional I x A matrix mapping items to attributes (default: all items -> 1 attribute)
  # theta_k: discrete latent class values (binary: 0/1; extend for polytomous attributes)
  # prob_cutoff: posterior probability threshold for classification

  n_items <- ncol(data)
  n_cats  <- max(sapply(data, max, na.rm = TRUE)) + 1

  if (is.null(q_matrix)) {
    # Default: single latent attribute, all items load on it
    q_matrix <- array(1, dim = c(n_items, 1, n_cats))
  }

  fit <- CDM::gdm(
    data    = data,
    theta.k = theta_k,
    Qmatrix = q_matrix,
    maxit   = 1000,
    convM   = 1e-4
  )

  person <- fit$person
  # Last column = posterior P(highest class) = P(attribute present)
  prob_dx <- person[, ncol(person)]

  data.frame(
    id             = seq_len(nrow(data)),
    prob_diagnosed = prob_dx,
    diagnosed      = as.integer(prob_dx >= prob_cutoff),
    map_class      = apply(person, 1, which.max) - 1L
  )
}
```

**When to use:** When the construct is inherently categorical (present/absent); when item-level fit to a continuous latent trait is poor; when you need probabilistic class membership for each person.

---

## Combine and Report

```r
compare_methods <- function(cutoff_res, irt_res, dcm_res) {
  data.frame(
    id                = cutoff_res$id,
    sum_score         = cutoff_res$sum_score,
    dx_cutoff         = cutoff_res$diagnosed,
    theta             = irt_res$theta,
    theta_se          = irt_res$theta_se,
    dx_irt            = irt_res$diagnosed,
    prob_dcm          = dcm_res$prob_diagnosed,
    dx_dcm            = dcm_res$diagnosed,
    n_methods_agree   = cutoff_res$diagnosed + irt_res$diagnosed + dcm_res$diagnosed,
    consensus_dx      = as.integer((cutoff_res$diagnosed + irt_res$diagnosed + dcm_res$diagnosed) >= 2)
  )
}

generate_report <- function(comparison,
                             construct  = "construct",
                             instrument = "instrument",
                             n_items    = NULL,
                             cutoff     = NULL) {
  n      <- nrow(comparison)
  n_dx   <- sum(comparison$consensus_dx)

  cat("==================================================\n")
  cat(sprintf("  PSYCHOMETRIC DIAGNOSIS REPORT\n"))
  cat(sprintf("  Construct:  %s\n", construct))
  cat(sprintf("  Instrument: %s", instrument))
  if (!is.null(n_items)) cat(sprintf(" (%d items)", n_items))
  cat(sprintf("\n  N = %d\n", n))
  cat("==================================================\n\n")

  cat("--- Prevalence by Method ---\n")
  cat(sprintf("  Cut-off (sum >= %s): %d / %d (%.1f%%)\n",
              ifelse(is.null(cutoff), "?", cutoff),
              sum(comparison$dx_cutoff), n, 100 * mean(comparison$dx_cutoff)))
  cat(sprintf("  IRT (theta >= 0):    %d / %d (%.1f%%)\n",
              sum(comparison$dx_irt), n, 100 * mean(comparison$dx_irt)))
  cat(sprintf("  DCM (P >= 0.5):      %d / %d (%.1f%%)\n",
              sum(comparison$dx_dcm), n, 100 * mean(comparison$dx_dcm)))
  cat(sprintf("  Consensus (>=2/3):   %d / %d (%.1f%%)\n\n", n_dx, n, 100 * n_dx / n))

  cat("--- Method Agreement ---\n")
  print(table(`Methods agreeing` = comparison$n_methods_agree))

  cat("\n--- Cross-tabulation: Cut-off vs DCM ---\n")
  print(table(CutOff = comparison$dx_cutoff, DCM = comparison$dx_dcm))

  cat("\n--- Ambiguous Cases (methods disagree) ---\n")
  ambiguous <- comparison[comparison$n_methods_agree == 1 | comparison$n_methods_agree == 2, ]
  cat(sprintf("  %d persons with partial method agreement (review recommended)\n\n",
              nrow(ambiguous[ambiguous$n_methods_agree != 3 & ambiguous$n_methods_agree != 0, ])))

  invisible(comparison)
}
```

---

## Full Pipeline (Entry Point)

```r
run_diagnosis_pipeline <- function(data,
                                    construct    = "construct",
                                    instrument   = "instrument",
                                    cutoff       = NULL,
                                    itemtype     = "graded",
                                    theta_cutoff = 0,
                                    q_matrix     = NULL,
                                    prob_cutoff  = 0.5,
                                    output_csv   = NULL) {
  # data:         data frame, rows = persons, cols = items (all numeric)
  # construct:    name of the latent construct (e.g., "depression", "PTSD")
  # instrument:   name of the scale (e.g., "PHQ-9", "PCL-5")
  # cutoff:       sum score threshold for Method A (required)
  # itemtype:     mirt item model for Method B ("graded", "2PL", etc.)
  # theta_cutoff: IRT theta threshold for Method B (default 0)
  # q_matrix:     optional Q-matrix array for Method C (default: single attribute)
  # prob_cutoff:  DCM posterior threshold for Method C (default 0.5)
  # output_csv:   optional file path to save person-level results

  stopifnot(!is.null(cutoff), is.data.frame(data))

  message("[1/4] Running cut-off diagnosis...")
  res_cutoff <- diagnose_cutoff(data, cutoff = cutoff)

  message("[2/4] Fitting IRT model...")
  res_irt <- fit_irt(data, itemtype = itemtype, theta_cutoff = theta_cutoff)

  message("[3/4] Fitting DCM...")
  res_dcm <- fit_dcm(data, q_matrix = q_matrix, prob_cutoff = prob_cutoff)

  message("[4/4] Generating report...")
  comparison <- compare_methods(res_cutoff, res_irt, res_dcm)
  generate_report(comparison,
                  construct  = construct,
                  instrument = instrument,
                  n_items    = ncol(data),
                  cutoff     = cutoff)

  if (!is.null(output_csv)) {
    write.csv(comparison, output_csv, row.names = FALSE)
    message(sprintf("Results saved to: %s", output_csv))
  }

  invisible(comparison)
}
```

---

## LLM Workflow

When the user asks to diagnose from response data:

1. **Clarify inputs** — ask for: instrument name, construct name, cut-off score, number of response categories, and whether a Q-matrix is needed.
2. **Load data** — read from user-supplied path or use a pre-loaded data frame.
3. **Call `run_diagnosis_pipeline()`** with appropriate arguments.
4. **Interpret output** — highlight consensus diagnoses, flag ambiguous cases, and note if the three methods give substantially different prevalences.
5. **Summarize** in plain language for the user.

## Method Selection Guide

| Situation | Use |
|---|---|
| Validated cut-off exists for this instrument | Method A (cut-off) |
| Items differ in quality / discrimination | Method B (IRT) |
| Construct is naturally categorical | Method C (DCM) |
| Want robust person-level classification | All three + consensus |
| Uncertainty quantification per person needed | Method B (theta SE / CI) |

## Required Packages

```r
install.packages(c("mirt", "CDM"))
```
