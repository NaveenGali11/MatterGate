# MatterGate: teammate visual test guide

**5-10 minutes for the main walkthrough, plus local setup.** Version 0.2.0, October 25, 2026.

This is a guided product check, not a claim of legal accuracy or production readiness.
The screenshots are reference views of earlier synthetic/public demonstrations, not
new results from your test session. Start fresh runs and record your own outcomes.

## Get the app running

On a new machine, follow [setup](setup.md) to clone the repository, install pinned
dependencies and create a private `.env`. Fixture mode needs no Nebius key. Do not
share `.env` or session secrets. Once installed, run from the repository root:

```sh
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Keep that terminal open and visit http://127.0.0.1:8000. This address reaches your
own machine; it does not reach a teammate's computer. Use one worker.

**Flow:** Request -> Permission -> Authorized evidence -> Draft -> Structural checks -> Human review -> Receipt.

## Start with the right expectations

![Overview: two scenarios with different permission boundaries.](images/devpost/04-product-overview.jpg)

*Overview: two scenarios with different permission boundaries.*

**Before you start:** Open the app on your own machine at http://127.0.0.1:8000. If it is not running, follow the repository setup guide. Localhost on your laptop is not your teammate's server.

**Two test modes:** **Fixture:** saved, repeatable answer for one exact question; no Nebius call. Use this first.

**Live:** real NVIDIA inference through Nebius; requires server-side credentials and may use paid quota.

**Who does what:** **Jordan** requests research. **Alex** reviews it. The identity switch is a demo simulation, not real authentication.

**What the app does:** Permission first, then authorized evidence, drafting, structural checks and human review. The model cannot grant access or approve itself.

> **Pass when:** Open System status. Confirm the database/corpus is ready. A configured live badge is not proof that inference has succeeded.

## 1. Create a run and inspect its evidence

![Reference screenshot: an earlier live run. Start a new run; IDs and wording will differ.](images/devpost/01-live-evidence-review.jpg)

*Reference screenshot: an earlier live run. Start a new run; IDs and wording will differ.*

**Click:** Open **New research**. Keep Jordan, Vendor onboarding / Vendor X, European Union and Vendor risk assessment. Keep the prefilled question unchanged. Select **Fixture**, then **Check scope and research**.

**Look for:** A granted research scope, a ready draft and **10/10 structural checks**. Open **Research brief** and select a numbered reference beside a claim.

**Try the navigation:** The corresponding authorized excerpt should open and receive focus. Read it, then use **Return to the claim**. Repeat once using the keyboard.

**Under the hood:** Policy limits source access before retrieval. The app checks citation IDs against selected evidence. Read the excerpt yourself: linkage does not prove that the claim is correct.

> **Pass when:** Each material claim has working evidence links. Navigation returns to the claim. No restricted material is shown.

## 2. Record a separate human decision

![Reference screenshot: a completed approval. Your new run begins awaiting review.](images/devpost/03-human-review-decision.jpg)

*Reference screenshot: a completed approval. Your new run begins awaiting review.*

**First, stay as Jordan:** Open **Human review**. Jordan should see **Continue as Alex**, rather than an active decision form.

**Then switch to Alex:** Select **Continue as Alex**. Confirm the rationale field and all three actions: **Approve draft**, **Request revision** and **Reject**.

**Review and submit:** Read the brief and cited excerpts. If the assessment is acceptable, add a short rationale and choose **Approve draft**. Check that the result says **Research draft approved**.

**What approval means:** You accepted the research assessment. You did not authorize data sharing. A draft can recommend **do not proceed** while you approve that assessment. One run accepts one decision.

> **Pass when:** Only the reviewer identity can submit. The decision persists after refresh. Do not expect to change an already recorded decision.

## 3. Inspect the receipt and download it

![Reference screenshot: real live diagnostics. Fixture mode must not claim live inference.](images/devpost/02-nebius-live-receipt.jpg)

*Reference screenshot: real live diagnostics. Fixture mode must not claim live inference.*

**Open run receipt:** Check the run ID, execution mode, permission, checks and human disposition. Expand the audit history and find **REVIEW_SUBMITTED**.

**Check the mode:** A new fixture run should report **zero provider transport attempts**. A successful live run should show actual provider metadata. Do not compare your token counts or latency to this screenshot.

**Download safe receipt:** Open the downloaded JSON. Match its run ID, mode and decision to the page. Confirm it excludes the question, source excerpts, prompts, credentials and review rationale.

**Understand the hash:** **Local hash chain verified** means the recorded event chain is consistent. It is not external notarization. The export still includes run and demo-identity metadata.

> **Pass when:** Page and JSON agree. REVIEW_SUBMITTED is present. Excluded free text and credentials are absent from the export.

## 4. Prove that denied research stops early

![Reference screenshot: an older denial without counters. Your newly created run should have measured zeros.](images/devpost/05-permission-boundary.jpg)

*Reference screenshot: an older denial without counters. Your newly created run should have measured zeros.*

**Create a fresh denial:** Return to **Overview**. Choose Scenario 02: **See the blocked request**. This uses Jordan and the restricted merger matter.

**Expected outcome:** The page should say **Research permission denied**. There must be no generated answer and no restricted source titles, IDs or excerpts.

**Check its receipt:** On the new run, retrieval attempts and provider transport attempts should both be **0**. The audit should have no retrieval-start or model-request event.

**Why this matters:** This is an expected pass for the boundary test. Permission is decided before source text enters model context. A denial is different from a provider failure or failed draft check.

> **Pass when:** Denied outcome, no answer, no restricted content and zero measured retrieval/provider attempts on the new run.

## Additional checks and bug reporting

### A. Revision / rejection

Create a fresh fixture run as Jordan for each action. Once ready, switch to Alex. Blank rationale must not save a rejection or revision. Add a reason and submit. Confirm the chosen disposition and REVIEW_SUBMITTED. Revision records feedback; it does not regenerate the draft.

### B. Unsupported fixture question

In New research, select Jordan, the seeded vendor/EU scope and Fixture mode. Change the question to: Can Vendor X retain support contact data for two years? Expect FIXTURE_SCENARIO_UNSUPPORTED and no reviewable answer. This is an expected guardrail, not a failed model call.

### C. History and readability

Return to Jordan and Overview. Try the history filters; opening a row must return to the matching run and mode. Test keyboard focus and 200% browser zoom. Expect readable text, usable controls and no overlap or page-wide horizontal scrolling.

### D. Optional live check

Only when live testing is intended and server credentials are configured: create a new seeded Live run as Jordan. Confirm actual completion metadata and inspect the draft before review. Record failures honestly; do not relabel a fixture result as a live success.

### If something stops

DENIED: policy boundary. BLOCKED: inspect the failed control or fixture explanation. MODEL_UNAVAILABLE: provider did not complete acceptably. Capture the error code and receipt. A separate fixture demo creates a new run and preserves the failed live record.

### Send this test report

Build/commit; browser and zoom; run ID; Live or Fixture; case; steps; expected result; actual result; screenshot; receipt if useful. Mark Pass, Fail or Not tested. Redact keys and private configuration. Use only synthetic/public research inputs.

## Copy this report

```text
Build/commit:
Browser / zoom:
Run ID / mode:
Case:
Result: Pass / Fail / Not tested
Steps:
Expected:
Actual:
Screenshot / receipt:
```

**Interpretation:** passing structural checks confirms the defined application
contract, not source support or legal correctness. Demo identities are selectable.
Human draft approval does not authorize business action. Local audit hashes are
unanchored. See the [user guide](user-guide.md) for more detail.
