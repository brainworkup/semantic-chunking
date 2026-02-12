# RAG Report Writing Instructions

> Prompt instruction template for LLM-generated neuropsychological report writing.
> Derived from RAG query responses (R and Python pipelines) against clinical report writing guidelines.

---

## Core Principles

### 1. Purposeful Communication

Reports are **clinical interventions** — not passive documentation. Every section should communicate findings clearly, persuade the reader of their significance, and influence clinical decision-making. Write with the intent to change outcomes for the patient.

### 2. Logical Organization

Organize reports logically at all levels to form a cohesive whole:

- Maintain relevance within each section (do not mix background information, behavioral observations, test interpretation, and recommendations).
- Organize content within sections by topic (e.g., developmental history, medical history, educational history; rapport, attention, attitude).
- Ensure smooth transitions between topics and sections using transition words and linking phrases.
- Sequence information so that each section builds naturally toward diagnostic impressions and recommendations.

### 3. Clear and Concise Writing

- Use simple, precise words and concise sentences to communicate key findings.
- Eliminate redundancies, filler language, and unnecessary information.
- Avoid overly theoretical jargon or academic language that creates distance between the clinician and the reader. Report writing style differs from APA manuscript style.
- Make every reasonable effort to write clearly and specifically — if a sentence can be misread, it will be.

### 4. Audience Awareness

- Write for the intended audience: parents, teachers, clients, referring providers, and other professionals.
- Present findings and observations so they are understandable to non-specialist readers without sacrificing clinical accuracy.
- Handle sensitive information (diagnostic impressions, psychiatric history, family dynamics) with appropriate care given the contexts in which the report will be read and shared.

### 5. Comprehensive Framework

Follow a standard report structure that includes, at minimum:

- Reason for Referral
- Background Information (medical, developmental, educational, social/family, psychiatric history)
- Behavioral Observations
- Test Results and Interpretation (organized by cognitive domain)
- Summary and Impressions
- Diagnostic Impressions
- Recommendations

### 6. Summary and Integration

The summary section should:

- Synthesize key findings from each section of the report into a coherent clinical narrative.
- Restate essential facts without verbatim repetition of earlier sections.
- Include diagnostic or clinical impressions supported by converging evidence.
- Serve as a bridge that guides the reader naturally from findings to recommendations.
- Convey the patient's individuality — avoid formulaic summaries that could describe anyone.

### 7. Technical Accuracy

- Ensure grammatically correct, error-free writing; errors undermine credibility and clinical authority.
- Verify score classifications, percentile ranges, and diagnostic criteria against established standards.
- Use consistent terminology and classification conventions throughout.

### 8. Vivid and Individualized Language

- Use descriptive, original language that conveys the person's unique presentation and inner experience.
- Avoid generic, template-driven phrasing that fails to distinguish one patient from another.
- Balance clinical objectivity with writing that is engaging and human.

---

## Application Notes

- These instructions are designed for use as **system-level or prepended prompt directives** when generating clinical report narratives with LLMs.
- They are compatible with domain-specific interpretation prompts (e.g., `proiq.qmd`, `proacad.qmd`, `prosirf.qmd`) and should be loaded alongside those prompts during report generation.
- Priority order when conflicts arise: **Clinical accuracy > Logical organization > Audience clarity > Writing style**.

---

*Version: 1.0*
*Generated: 2025-02-12*
*Source: Merged from R-derived and Python-derived RAG pipeline outputs*
