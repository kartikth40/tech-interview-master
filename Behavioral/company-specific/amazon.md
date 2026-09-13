# Amazon - Behavioral Interview Guide

## Amazon Interview Overview

**Format:**
- 5-7 rounds (1 phone screen + 4-6 onsite/virtual + 1 "Bar Raiser")
- **Behavioral**: 40-50% of total interview (HIGHEST among MAANG)
- **Technical**: 50-60%
- **Duration**: 60 min per round

**Unique Features:**
- **Bar Raiser**: Independent interviewer ensures high hiring bar
- **Loop Interview**: Each interviewer tests different Leadership Principles (LPs)
- **16 Leadership Principles**: Must prepare stories for ALL 16

---

## Amazon's 16 Leadership Principles (LPs)

The **full LP reference** - each principle's definition, the questions it maps to, and what
interviewers look for - lives in one canonical place so it stays consistent:

➡️ **[Leadership Principles guide](../leadership-principles.md)** (all 16, with definitions + question
examples + a story hook each).

Below we focus on what's *Amazon-interview-specific*: how to TAG stories to LPs, a coverage matrix,
and the do's/don'ts. Study the LP reference first, then map your own stories using the matrix.

### How to tag a story to an LP (3 worked examples)

The technique Amazon rewards: name the LP, then tell a quantified STAR that demonstrates it. A few
exemplars (you don't need one per LP - see the coverage matrix):

**Ownership** - *"This shows Ownership."*
```
S: Payment service (another team's) was down, ~$50K/hr revenue loss, owners asleep.
T: Fix it now rather than wait / escalate and stall.
A: Debugged it myself; found a third-party API timeout; shipped retry-with-backoff in 2h;
   wrote a post-mortem for the owning team + added a monitoring alert.
R: Stopped the bleed; owning team adopted the alert.  Learning: ownership = solve it, not assign blame.
```

**Are Right, A Lot** - *"This shows Are Right, A Lot - including admitting when I was wrong."*
```
S: Picking a DB; my instinct was MongoDB (familiar).
T: Make the right call, not the comfortable one.
A: Sought 3 senior perspectives; one flagged our data is relational; I researched, changed my mind, chose PostgreSQL.
R: Complex queries ~10x faster than the Mongo path would've been.  Learning: ego is the enemy of the right decision.
```

**Have Backbone; Disagree and Commit** - *"This shows Have Backbone; Disagree and Commit."*
```
S: Manager wanted a full rewrite; I favored incremental refactor.
T: Push back honestly, then align.
A: Presented data on rewrite-failure rates + an incremental alternative; manager still chose rewrite; I committed 100% and led it.
R: Rewrite shipped (a bit late) and enabled new features - I was partly wrong, and the trust grew.
```

> For stories covering the other principles (Customer Obsession, Dive Deep, Frugality, etc.), reuse
> the hooks in the [LP reference](../leadership-principles.md) and flesh them out with your own numbers.

---

## Amazon LP Coverage Matrix

Prepare 12-15 stories that each map to multiple LPs:

| Story | Primary LP | Secondary LP |
|-------|-----------|--------------|
| Optimized checkout | Customer Obsession | Deliver Results |
| Fixed production bug (not my team) | Ownership | Bias for Action |
| Automated deployments | Invent and Simplify | Frugality |
| Chose PostgreSQL over MongoDB | Are Right, A Lot | Learn and Be Curious |
| Learned Kubernetes | Learn and Be Curious | Deliver Results |
| Mentored junior engineer | Hire and Develop | Earn Trust |
| Pushed back on buggy release | Insist on Highest Standards | Have Backbone |
| Migrated to microservices | Think Big | Deliver Results |
| Added read replica under pressure | Bias for Action | Ownership |
| Used Prometheus vs paid tool | Frugality | Invent and Simplify |
| Missed deadline but told client early | Earn Trust | Deliver Results |
| Debugged latency issue | Dive Deep | Insist on Standards |
| Disagreed with manager | Have Backbone | Earn Trust |

---

## Amazon-Specific Do's and Don'ts

### ✅ Do:
- **Map every story to LPs** - "This shows Ownership because..."
- **Use data** - Amazon is metrics-driven
- **Show customer impact** - Always bring it back to customer
- **Prepare 12-15 stories** minimum (cover all 16 LPs)
- **Practice STAR format** - Amazon invented it!
- **Show long-term thinking** - Not just quick wins
- **Admit failures** - Especially for "Deliver Results" (failure story)
- **Say "I" not "we"** - Amazon wants YOUR contribution

### ❌ Don't:
- Skip any LPs (Bar Raiser will notice gaps)
- Only talk about successes (need failure stories too)
- Take all credit ("I" good, but mention team support)
- Focus only on technical (show leadership, people skills)
- Give vague answers (Amazon wants specifics)

---

## Questions to Ask Interviewer

**Customer Obsession:**
- "Can you share an example of when your team went above and beyond for a customer?"

**Leadership Principles:**
- "Which Leadership Principles are most important for this team?"
- "How does [specific LP] manifest in your day-to-day work?"

**Impact:**
- "What's the most impactful project this team has shipped recently?"

---

## 💡Pro Tips for Amazon

1. **Learn the 16 LPs by heart** - Interviewers will ask: "Which LP does this show?"

2. **Use the LP language** - Say "This demonstrates Customer Obsession because..."

3. **12-15 stories minimum** - Each story should map to 2-3 LPs

4. **Prepare deep dives** - Amazon interviewers will ask follow-ups for 10+ minutes on ONE story

5. **Customer Obsession is #1** - Most important LP, always bring it back to customer

6. **Failure stories required** - Especially "Deliver Results" - tell me about a deadline you missed

7. **"I" not "we"** - Amazon wants to know YOUR role specifically

8. **Quantify everything** - $X revenue, Y% improvement, Z users impacted

---

## Summary

**Amazon wants:**
- 🎯 Customer-obsessed leaders
- 💪 Owners who solve problems beyond job scope  
- ⭐ High standards maintainers
- 🚀 Big thinkers who deliver results
- ⚡ Action-takers with calculated risks
- 🤝 Trust earners through transparency

**Prepare:**
- **Memorize all 16 Leadership Principles**
- 12-15 stories covering all LPs (some stories hit multiple)
- Practice STAR format religiously
- Prepare deep dives (interviewers dig for 10 min per story)
- **Must have failure stories** (Deliver Results, Are Right A Lot)

**Remember:**
- Bar Raiser interview is hardest - different LP tested
- Each interviewer assigned specific LPs before loop
- 40-50% of interview is behavioral (highest of MAANG)
- LP language is critical - speak Amazon's language

**Next Steps:**
- Review full [Leadership Principles guide](../leadership-principles.md)
- Create [STAR stories](../STAR-stories.md) for all 16 LPs
- Practice saying which LP each story demonstrates
