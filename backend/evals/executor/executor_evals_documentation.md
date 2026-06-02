# Email Classification System — Evaluation & Iteration Report

## 1. System Overview

This project implements an LLM-based email classification system designed to route incoming emails into three operational categories:

### Classes

* **NON_BUSINESS**
  Personal, promotional, informational, or non-actionable emails that do not require business engagement.

* **BASIC**
  Business-related inquiries that require a response or information exchange (e.g., pricing questions, service inquiries, general requests).

* **PRIORITY**
  High-impact business communications involving active execution work such as:

  * scope expansion
  * system or pipeline modifications
  * ongoing project updates
  * operational or contractual execution requests

### System Goal

The goal is to reliably route emails into downstream workflows:

* NON_BUSINESS → ignored or lightly processed
* BASIC → RAG-based response generation
* PRIORITY → execution / workflow triggering

---

## 2. Evaluation Methodology

### 2.1 Dataset Structure

Each evaluation sample includes:

* Email ID
* Subject
* Body content
* Expected classification (human-labeled ground truth)
* Model prediction
* Confidence score
* Model reasoning output

This structure enables both:

* quantitative evaluation (accuracy, confusion matrix)
* qualitative analysis (reasoning inspection)

---

### 2.2 Evaluation Metrics

#### Overall Accuracy

Measures total classification correctness across all samples.

#### Per-Class Accuracy

Evaluates correctness per label:

* BASIC
* NON_BUSINESS
* PRIORITY

Used to detect class-specific weaknesses.

#### Confusion Matrix

Captures misclassification patterns between classes, especially:

* BASIC ↔ NON_BUSINESS
* BASIC ↔ PRIORITY

#### Confidence Analysis

Used to determine whether errors are:

* uncertain (low confidence)
* systematic misclassification (high confidence errors)

High-confidence errors are treated as **critical signal of rule misalignment**.

---

## 3. Evaluation Phases and System Evolution

## 3.1 Initial Baseline Evaluation

### Result

A first evaluation run produced:

* **100% accuracy**
* all classes correctly classified
* no observed failures

### Interpretation

At this stage, the system appeared fully correct. However, this result was based on a single evaluation pass and did not yet validate stability.

---

## 3.2 Consistency Validation Evaluation (Critical Discovery)

To verify robustness, a second evaluation was performed using the same classification setup.

### Result

* Accuracy dropped below 100%
* New boundary failures appeared
* NON_BUSINESS → BASIC misclassifications emerged

### Key Observation

The system was not unstable in a random sense — instead:

> it was sensitive to borderline intent cases not fully exposed in the first run.

### Impact

This evaluation revealed:

* hidden ambiguity in intent interpretation
* weak separation between BASIC and NON_BUSINESS
* early signs of boundary dependence on phrasing

---

## 3.3 First Prompt Refinement Phase

Following the consistency evaluation, prompt adjustments were introduced to better define intent strength.

### Objective

Improve separation between:

* genuine business intent
* casual or exploratory mentions of business topics

### Outcome

* partial improvement in NON_BUSINESS classification
* persistent BASIC over-triggering on weak intent emails

### Insight

The model was interpreting:

> any explicit business question → BASIC

regardless of intent strength.

---

## 3.4 Emergence of Secondary Boundary Failure

As BASIC vs NON_BUSINESS was refined, a new failure pattern appeared:

* PRIORITY emails were misclassified as BASIC

### Example pattern

* scope expansion requests
* system modification tasks
* active project updates

### Root Cause

PRIORITY was initially defined using:

* urgency
* meetings
* financial/legal signals

This created a missing dimension:

> execution impact on ongoing work

---

## 3.5 Over-Specification Phase

Further prompt iterations attempted to fix multiple boundaries simultaneously.

### Resulting issues:

* overlapping rules across classes
* conflicting heuristics for intent interpretation
* model defaulting to BASIC under ambiguity
* new instability introduced in PRIORITY classification

### Key Insight

> Increasing rule complexity did not improve performance; it introduced decision conflicts.

---

## 3.6 Simplification and Rollback Phase

A simplified version of the prompt was restored, reducing overlapping constraints and reinforcing clear decision boundaries.

### Result

* 100% accuracy on evaluation dataset
* stable classification across all classes
* elimination of boundary conflicts

---

## 4. Key Findings

### 4.1 Evaluation Stability Requires Repetition

A single perfect evaluation is insufficient. The second evaluation revealed:

> latent boundary sensitivity that was not visible initially.

---

### 4.2 Primary Failure Cause: Ambiguous Intent Boundaries

Errors consistently stemmed from:

* unclear distinction between intent strength levels
* overlap between BASIC and PRIORITY definitions
* presence of multiple competing heuristics

---

### 4.3 Over-Specification Degrades Performance

Adding rules without strict hierarchy caused:

* conflicting classification signals
* unstable decision-making under edge cases
* fallback behavior toward BASIC class

---

### 4.4 Confidence is a Strong Diagnostic Signal

High-confidence errors indicated:

* systematic rule misinterpretation
* not model uncertainty

This was critical in identifying prompt-level misalignment.

---

### 4.5 Simplicity Restored Stability

The final stable system was achieved through:

* removal of conflicting rules
* reduction of conditional complexity
* reliance on clear intent-based separation

---

## 5. Importance of the Evaluation System

This evaluation framework enabled:

* identification of hidden boundary failures
* iterative refinement of classification logic
* detection of overfitting to single-run evaluations
* structured comparison across prompt versions

Most importantly, it shifted the development process from:

> prompt experimentation

to:

> decision system engineering

---

## 6. Final Conclusion

The evolution of this system demonstrates that classification stability is not achieved through increasing rule complexity, but through:

* clear definition of intent boundaries
* elimination of overlapping decision criteria
* iterative validation under multiple evaluation runs

The final system succeeded not because it became more detailed, but because it became more consistent.
