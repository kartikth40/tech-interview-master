# STAR Stories Bank Template

## 📝 Instructions

1. Prepare **12-15 stories** covering different categories (each can map to 2-3 company principles)
2. Use the **STAR format** (Situation, Task, Action, Result)
3. **Quantify results** wherever possible (numbers, %, $, time saved)
4. **Practice each story** out loud 3+ times
5. **Tag stories** with categories and company mappings

> ⚠️ **Use YOUR OWN stories.** The examples throughout this repo (checkout redesign, PostgreSQL-vs-MongoDB,
> the production-outage/missing-index story, "learned Kubernetes in 2 weeks") are **illustrative
> templates showing the format** - they recur across the company guides on purpose. Do NOT memorize and
> repeat them in a real loop: interviewers compare notes, and borrowed stories collapse under the
> follow-up drilling ("what exactly did *you* do? why that trade-off?"). Swap in your real experiences.

---

## 🎯 Story Categories Checklist

Prepare at least:
- [ ] 3 Leadership stories
- [ ] 3 Conflict/Collaboration stories
- [ ] 3 Failure/Learning stories
- [ ] 2 Innovation/Problem-Solving stories
- [ ] 2 Pressure/Deadline stories
- [ ] 2 Customer Focus stories
- [ ] 2-3 Technical Excellence stories

---

## Story Template

```markdown
## Story #X: [Catchy Title]

**Categories:** Leadership, Problem-Solving, Technical  
**Maps to:** Amazon's "Deliver Results", Google's "Bias for Action"  
**Best for Companies:** Amazon, Meta, Microsoft  
**Duration:** ~2.5 minutes

### Situation (Context - ~10-15%)
[Set the scene: When, where, who, what was happening?]
- 

### Task (Challenge - ~10-15%)
[What problem/goal? What was your responsibility?]
- 

### Action (What YOU did - ~50-60%)
[Specific steps YOU took. Focus on "I" not "we"]
1. 
2. 
3. 
4. 
5. 

### Result (Outcome - ~20-25%)
[Quantified impact and learning - this is where you show impact + what you learned]
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:** [Date]
```

---

## 📚 Your Story Bank

### LEADERSHIP STORIES

---

## Story #1: [Title - e.g., "Led Cross-Functional Feature Launch"]

**Categories:** Leadership, Initiative, Stakeholder Management  
**Maps to:** Amazon's "Deliver Results", "Ownership", Google's "Bias for Action"  
**Best for Companies:** Amazon, Meta, Microsoft, Google  
**Duration:** ~2.5 minutes

### Situation (Context)
[Example: During my role as SDE at Company X, we identified that 30% of users were abandoning the checkout flow. Leadership wanted a solution but no one owned it across 3 different teams (frontend, backend, payments).]

### Task
[Example: I volunteered to lead a cross-functional initiative to reduce checkout abandonment by 20% within one quarter, even though I was a junior engineer.]

### Action
1. [Conducted user research: Analyzed 10K user sessions using Mixpanel, identified top 3 friction points]
2. [Created proposal: Designed a simplified 2-step checkout flow with mockups]
3. [Rallied team: Pitched to eng managers from all 3 teams, got buy-in]
4. [Project management: Created Gantt chart, ran weekly standups, unblocked dependencies]
5. [Implemented: Led frontend implementation, coordinated with backend/payments teams]
6. [Validated: A/B tested with 10% traffic before full rollout]

### Result
- **Impact:**: Reduced checkout abandonment from 30% → 15% (50% improvement)
- **Metrics:** Increased revenue by $500K/quarter, improved NPS by 12 points
- **Learning:** Leadership isn't about title-it's about taking ownership and rallying others around a shared goal

**Keywords:** cross-functional, initiative, data-driven, stakeholder management  
**Practice Count:** 0/3  
**Last Practiced:** [Date]

---

## Story #2: [Your Leadership Story Here]

**Categories:**  
**Maps to:**  
**Best for Companies:**  
**Duration:**

### Situation


### Task


### Action
1. 
2. 
3. 

### Result
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #3: [Your Leadership Story Here]

[Use same template]

---

### CONFLICT & COLLABORATION STORIES

---

## Story #4: [Title - e.g., "Resolved Technical Disagreement Through Data"]

**Categories:** Conflict Resolution, Data-Driven, Collaboration  
**Maps to:** Amazon's "Have Backbone; Disagree and Commit", "Are Right, A Lot"  
**Best for Companies:** Amazon, Google, Meta  

### Situation
[Example: My team was split on choosing between SQL vs NoSQL for a new microservice. Senior engineer pushed for NoSQL (MongoDB), I believed SQL (PostgreSQL) was better for our use case.]

### Task
[Example: I needed to challenge a senior engineer's decision without seeming insubordinate, while ensuring we made the right technical choice for the product.]

### Action
1. [Requested 1-on-1 to understand their reasoning (turned out they valued scalability over consistency)]
2. [Created decision matrix comparing both options across 6 criteria: consistency, query complexity, team expertise, ops overhead, cost, scalability]
3. [Ran load tests on both: PostgreSQL handled our projected load (10K QPS) fine, MongoDB was overkill]
4. [Presented data to team in design review, proposed PostgreSQL with caching layer for scalability]
5. [Senior engineer agreed after seeing data, we committed together]

### Result
- **Impact:** Saved $20K/year in infrastructure costs (PostgreSQL cheaper than MongoDB)
- **Metrics:** Launched on time, system handled 15K QPS at 99th percentile <50ms latency
- **Learning:** Disagree with data, not opinions. Respectfully challenging decisions makes both parties better.

**Keywords:** technical decision, data-driven, diplomacy, SQL vs NoSQL  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #5: [Your Conflict Story Here]

[Use template]

---

## Story #6: [Your Conflict Story Here]

[Use template]

---

### FAILURE & LEARNING STORIES

---

## Story #7: [Title - e.g., "Production Outage I Caused"]

**Categories:** Failure, Learning, Accountability  
**Maps to:** Amazon's "Learn and Be Curious", "Ownership", Meta's "Be Open"  
**Best for Companies:** Amazon, Meta, Google  

### Situation
[Example: During my first year as SDE, I was tasked with deploying a database migration to add an index on a 100M row table.]

### Task
[Example: I needed to add the index without downtime during peak hours. I tested on dev/staging which had 10K rows and it worked fine.]

### Action (What went wrong)
1. [Deployed directly to production during business hours without load testing on prod-scale data]
2. [Index creation locked the table for 3 hours instead of expected 5 minutes]
3. [This brought down the entire checkout service-$200K revenue lost]
4. [Immediately rolled back, but damage was done]

### Action (How I fixed it)
1. [Created incident report: Did root cause analysis, identified 3 failures: (1) no large-scale testing, (2) no rollback plan, (3) deployed during peak hours]
2. [Implemented safeguards: Created runbook for DB migrations, mandated load testing on prod replica, required approval for peak-hour deploys]
3. [Made it right: Volunteered to work weekend to properly deploy using online index creation (no locking)]
4. [Shared learnings: Presented to team about migration best practices]

### Result
- **Impact:** No further production incidents from DB migrations (24 months and counting)
- **Metrics:** Team adopted my runbook, reduced migration time by 60% using online index creation
- **Learning:** Failed miserably, but took ownership, fixed the process, and became the go-to person for DB migrations. Failure is the best teacher if you own it.

**Keywords:** production outage, ownership, failure, database, learning  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #8: [Your Failure Story Here]

[Use template]

---

## Story #9: [Your Failure Story Here]

[Use template]

---

### INNOVATION & PROBLEM-SOLVING STORIES

---

## Story #10: [Title - e.g., "Optimized Query Performance 100x"]

**Categories:** Problem-Solving, Technical Excellence, Innovation  
**Maps to:** Amazon's "Invent and Simplify", Google's "Technical Excellence"  

### Situation


### Task


### Action
1. 
2. 
3. 

### Result
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #11: [Your Innovation Story Here]

[Use template]

---

### PRESSURE & DEADLINE STORIES

---

## Story #12: [Title - e.g., "Delivered Critical Feature Under Impossible Deadline"]

**Categories:** Pressure, Time Management, Prioritization  
**Maps to:** Amazon's "Bias for Action", "Deliver Results"  

### Situation


### Task


### Action
1. 
2. 
3. 

### Result
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #13: [Your Pressure Story Here]

[Use template]

---

### CUSTOMER FOCUS STORIES

---

## Story #14: [Title - e.g., "Redesigned Feature Based on User Feedback"]

**Categories:** Customer Obsession, User Research, Impact  
**Maps to:** Amazon's "Customer Obsession", Google's "User Focus"  

### Situation


### Task


### Action
1. 
2. 
3. 

### Result
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #15: [Your Customer Focus Story Here]

[Use template]

---

### TECHNICAL EXCELLENCE STORIES

---

## Story #16: [Title - e.g., "Architected Scalable System from Scratch"]

**Categories:** System Design, Scalability, Architecture  
**Maps to:** Google's "Technical Excellence", "Think Big"  

### Situation


### Task


### Action
1. 
2. 
3. 

### Result
- **Impact:** 
- **Metrics:** 
- **Learning:** 

**Keywords:**  
**Practice Count:** 0/3  
**Last Practiced:**

---

## Story #17-20: [Add More Stories]

[Continue adding stories until you have 15-20 total covering all categories]

---

## 📊 Story Coverage Matrix

Use this to ensure you have balanced coverage:

| Category | Goal | Count | Status |
|----------|------|-------|--------|
| Leadership | 3+ | 0 | ❌ |
| Conflict/Collaboration | 3+ | 0 | ❌ |
| Failure/Learning | 3+ | 0 | ❌ |
| Innovation/Problem-Solving | 2+ | 0 | ❌ |
| Pressure/Deadline | 2+ | 0 | ❌ |
| Customer Focus | 2+ | 0 | ❌ |
| Technical Excellence | 2+ | 0 | ❌ |
| **Total** | **15-20** | **0** | ❌ |

---

## 🎯 Practice Tracker

| Story # | Title | Practice 1 | Practice 2 | Practice 3 | Interview Ready? |
|---------|-------|-----------|-----------|-----------|-----------------|
| 1 | | ❌ | ❌ | ❌ | ❌ |
| 2 | | ❌ | ❌ | ❌ | ❌ |
| 3 | | ❌ | ❌ | ❌ | ❌ |
| ... | | | | | |

---

## 💡 Tips for Writing Great Stories

1. **Start with the result** - Work backwards from impact
2. **Use numbers** - "Increased X by Y%" is better than "improved X"
3. **Show, don't tell** - Instead of "I'm a good leader", tell a story that proves it
4. **One story, multiple uses** - Can reframe same story for different questions
5. **Recent is better** - Last 1-2 years preferred, but exceptions okay for strong stories
6. **Practice variety** - Don't use all stories from same job/project

---

## 🚀 Next Steps

1. Fill out at least 15 stories using this template
2. Practice each story 3+ times out loud
3. Record yourself and watch for:
   - Filler words ("um", "like", "you know")
   - Going over 3 minutes
   - Not quantifying results
   - Using "we" instead of "I"
4. Map stories to specific companies you're interviewing with
5. Update [Practice Tracker](#practice-tracker) after each practice session

---

**Remember:** Quality stories > quantity. 10 well-crafted, practiced stories are better than 30 rushed ones.

Start filling this out NOW! Your future self will thank you. 💪
