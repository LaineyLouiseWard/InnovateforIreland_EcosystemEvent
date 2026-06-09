# Origin — how the idea formed

Where the carer map started, and how the one-day build converged on what shipped.

## The question

**How might we** help a carer-support service see where unpaid carers are most at risk across
Ireland, so support reaches them before crisis?

We can't see individual carers in open data, so from the outset the map was always **area-level**:
it shows where the *drivers* of carer strain concentrate (heavy care load, deprived or isolated
areas, an ageing population), never a verdict about a person.

## What we explored, and what we kept

The first sketch was a single-measure map you moved through **time** (a "Now" carer-rate view and a
2042 demand projection with migration scenarios). We set that aside: the national carer rate is
nearly flat (5.2–6.3% across the 8 regions), so carer rate alone isn't really "at risk," and a
time-projection added modelling without sharpening the decision.

What shipped is the opposite instinct, and stronger for it: a **present-day composite** of need,
fused with **where the services actually are**. That join — need against supply — is the thing
nobody had done for Ireland, and it's what makes the map decision-useful rather than descriptive.

## What shipped

- **Vulnerability Index** — a 4-theme composite (carer load, deprivation, demand, isolation) per
  small area, percentile-ranked, no invented weights.
- **Service Desert** — vulnerability × distance to the nearest carer support, so an area scores
  high only when need is high *and* help is far.
- **Market Gap** — need vs provider density rolled up to the 20 HSE areas, the operator view.
- **Need × Supply bivariate** and a **"target your supply here"** drill-down.

Full method in [`../methods/METHODOLOGY.md`](../methods/METHODOLOGY.md); the data behind each layer
in [`../methods/DATA.md`](../methods/DATA.md); the product shape in
[`../design/CAPSTONE_CONCEPT.md`](../design/CAPSTONE_CONCEPT.md). The commercial angle that emerged
along the way is in [`BUSINESS_CASE.md`](BUSINESS_CASE.md); ideas we parked in
[`EXTENSIONS.md`](EXTENSIONS.md).
