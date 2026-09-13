# Company-Specific Interview Tips (MAANG)

## Overview

Each top tech company has unique interview styles, focus areas, and cultures. This guide helps you tailor your preparation to specific companies.

> ⚠️ **On the percentages below:** the DSA focus %, system-design/behavioral weights, and process
> durations are **approximate, directional signals** based on commonly-reported candidate experience -
> not official published data. Use them to bias your prep (e.g. "Meta leans trees/graphs"), not as exact truth.

---

## Google

### Interview Process
- **Phone Screen:** 1 technical (45 min)
- **Onsite:** 4-5 rounds (DSA coding + system design + Googleyness)
- **Duration:** 6-8 weeks total

### DSA Focus Areas (approximate)
1. **Arrays & Strings** (30%) - Heavy emphasis
2. **Dynamic Programming** (25%) - Very important
3. **Graphs** (20%) - BFS/DFS, shortest path
4. **Trees & Binary Search** (15%)
5. **Math & Bit Manipulation** (10%)

### Difficulty Distribution
- **Easy:** 5%
- **Medium:** 70% ⭐ (Most important)
- **Hard:** 25%

### What Makes Google Unique
- ✅ **Emphasis on optimal solutions** - Interviewers push for best time/space complexity
- ✅ **Multiple approaches** - Expect to discuss brute force → optimized
- ✅ **Code quality matters** - Clean, well-structured code
- ✅ **Broad, not deep** - More medium problems than hard
- ✅ **Math-heavy** - Combinatorics, probability questions

### Sample Questions (Google-Style)
- LeetCode 42: Trapping Rain Water
- LeetCode 72: Edit Distance
- LeetCode 76: Minimum Window Substring
- LeetCode 200: Number of Islands
- LeetCode 295: Find Median from Data Stream

### System Design
- **Scope:** Broad architectural discussions
- **Focus:** Scalability, trade-offs
- **Depth:** High-level more than implementation details
- **Duration:** 45 min

### Behavioral (Googleyness)
Googleyness (GCA, Leadership, RRK, and comfort-with-ambiguity / humility / collaboration) plus worked
example questions and stories are covered in depth in the canonical guide:
➡️ **[Behavioral/company-specific/google.md](../Behavioral/company-specific/google.md)**

Quick sampler: "Tell me about a time you had to learn something completely new", "Describe a situation
where you were wrong and someone corrected you".

### Pro Tips
- 🎯 **Practice explaining** - Google values communication
- 🎯 **Think out loud** - Show your thought process
- 🎯 **Ask clarifying questions** - Shows thoughtfulness
- 🎯 **Discuss trade-offs** - Always mention time/space complexity
- 🎯 **Be humble** - Acknowledge alternative approaches

### Resources
- Google's official interview prep: research.google/interview-prep
- LeetCode Google tagged problems (200+)
- Focus on Medium difficulty

---

## Meta (Facebook)

### Interview Process
- **Phone Screen:** 1-2 technical (45 min each)
- **Onsite:** 2 coding + 1 system design + 1 behavioral ("Jedi")
- **Duration:** 4-6 weeks total

### DSA Focus Areas
1. **Trees & Graphs** (35%) ⭐ **Heavy emphasis**
2. **Arrays & Strings** (25%)
3. **Dynamic Programming** (20%)
4. **Backtracking & Recursion** (10%)
5. **Hash Maps & Two Pointers** (10%)

### Difficulty Distribution
- **Easy:** 10%
- **Medium:** 75% ⭐ (Critical)
- **Hard:** 15%

### What Makes Meta Unique
- ✅ **Speed matters** - Finish in 30 min, discuss optimization for remaining 15 min
- ✅ **Production quality code** - Expect to run your code
- ✅ **Follow-up questions** - "What if input size is 1 billion?"
- ✅ **Communication** - Think out loud constantly
- ✅ **Move fast** - Reflects company culture

### Sample Questions (Meta-Style)
- LeetCode 1: Two Sum (warmup)
- LeetCode EASY→ MEDIUM→ simulate progression
- LeetCode 236: L CA of Binary Tree
- LeetCode 938: Range Sum of BST
- LeetCode 314: Binary Tree Vertical Order Traversal (Meta favorite)
- LeetCode 71: Simplify Path
- LeetCode 791: Custom Sort String

### System Design
- **Scope:** Design social features (News Feed, Messenger, Stories)
- **Focus:** Real-time systems, scale
- **Unique:** Expect to code parts of system design
- **Duration:** 45 min

**Common Meta System Designs:**
- Design News Feed
- Design Messenger
- Design Instagram Stories
- Design Friend Suggestions
- Design Notification System

### Behavioral ("Jedi" Round)
Meta's core values (Move Fast, Be Bold, Focus on Impact, Be Open, Build Social Value) and worked
example questions/stories are covered in depth in the canonical guide:
➡️ **[Behavioral/company-specific/meta.md](../Behavioral/company-specific/meta.md)**

Quick sampler: "Describe a bold decision you made", "Tell me about maximizing impact with limited
resources", "Describe a time you gave/received difficult feedback".

### Pro Tips
- 🎯 **Write clean code fast** - Practice typing speed
- 🎯 **Test your code** - Walk through test cases
- 🎯 **Handle edge cases** - Empty arrays, null, negatives
- 🎯 **Be bold** - Meta values decisive action
- 🎯 **Social impact** - Frame stories around user impact

### Resources
- Meta interview prep: https://www.metacareers.com/swe-prep
- LeetCode Meta tagged problems (150+)
- Practice **trees and graphs extensively**

---

## Amazon

### Interview Process
- **Phone Screen:** 1 technical + behavioral (60 min)
- **Onsite:** 5-6 rounds (coding + system design + bar raiser)
- **Duration:** 6-10 weeks total
- **Unique:** Bar Raiser (extra tough interviewer)

### DSA Focus Areas
1. **Dynamic Programming** (25%) ⭐ **Very important**
2. **Arrays & Strings** (20%)
3. **Trees** (20%)
4. **Graphs** (15%)
5. **Greedy Algorithms** (10%)
6. **OOP Design** (10%) - Unique to Amazon

### Difficulty Distribution
- **Easy:** 15%
- **Medium:** 65%
- **Hard:** 20%

### What Makes Amazon Unique
- ✅ **Leadership Principles** - Every question maps to 1-2 of 16 principles
- ✅ **STAR format mandatory** - Situation, Task, Action, Result
- ✅ **Bar Raiser** - One interviewer deliberately tough
- ✅ **OOP questions** - Design a parking lot, library system
- ✅ **Behavioral weight** - 40-50% of evaluation

### Sample Questions (Amazon-Style)
- LeetCode 1: Two Sum
- LeetCode 146: LRU Cache (OOP + DSA)
- LeetCode 200: Number of Islands
- LeetCode 224: Basic Calculator
- LeetCode 297: Serialize and Deserialize Binary Tree
- LeetCode 994: Rotting Oranges

### System Design
- **Scope:** E-commerce systems (cart, inventory, recommendations)
- **Focus:** Reliability, scale, consistency
- **Unique:** Expect database design questions
- **Duration:** 60 min (longer than others)

**Common Amazon System Designs:**
- Design Amazon Shopping Cart
- Design Product Recommendation System
- Design Order Management System
- Design Inventory Management
- Design Amazon Prime Video

### Behavioral (Leadership Principles)
**Prepare 12-15 strong stories, each mapping to 2-3 principles** (covers all 16). Full framework + how to tag stories: [leadership-principles.md](../Behavioral/leadership-principles.md) and [Amazon guide](../Behavioral/company-specific/amazon.md).

**Top 5 Principles Tested:**
1. Customer Obsession
2. Ownership
3. Deliver Results
4. Invent and Simplify
5. Dive Deep

**Sample Questions:**
- "Tell me about a time you went above and beyond for a customer"
- "Describe a time you took ownership beyond your role"
- "Tell me about delivering results despite obstacles"
- "Describe a time you simplified a complex problem"
- "Tell me about diving deep to find root cause"

### Pro Tips
- 🎯 **Start with principle** - "This demonstrates **Ownership**..."
- 🎯 **Quantify everything** - Numbers, percentages, dollars
- 🎯 **Prepare 20-30 STAR stories** - More than any other company
- 🎯 **Practice OOP design** - Unique to Amazon
- 🎯 **Bar Raiser strategy** - Stay calm, they're testing resilience

### Resources
- Amazon's 16 Leadership Principles (mandatory reading)
- LeetCode Amazon tagged problems (300+)
- Practice STAR method extensively

---

## Microsoft

### Interview Process
- **Phone Screen:** 1 technical (60 min)
- **Onsite:** 4-5 rounds (coding + system design + behavioral)
- **Duration:** 4-6 weeks total

### DSA Focus Areas
1. **Trees** (30%) ⭐ **Extremely important**
2. **Arrays & Strings** (25%)
3. **Recursion & Backtracking** (20%)
4. **Dynamic Programming** (15%)
5. **Linked Lists** (10%)

### Difficulty Distribution
- **Easy:** 20%
- **Medium:** 60%
- **Hard:** 20%

### What Makes Microsoft Unique
- ✅ **Trees obsession** - Expect 2-3 tree problems
- ✅ **Recursive thinking** - They love recursion
- ✅ **Follow-up questions** - "Now solve it iteratively"
- ✅ **Nice interviewers** - Less pressure than MAANG peers
- ✅ **OOP design** - Similar to Amazon

### Sample Questions (Microsoft-Style)
- LeetCode 102: Binary Tree Level Order Traversal
- LeetCode 226: Invert Binary Tree
- LeetCode 297: Serialize Binary Tree
- LeetCode 236: LCA of Binary Tree
- LeetCode 124: Binary Tree Maximum Path Sum
- LeetCode 46: Permutations (backtracking)

### System Design
- **Scope:** Enterprise software, cloud systems
- **Focus:** Azure integration, microservices
- **Duration:** 45 min

### Behavioral
**Microsoft Values:**
- Respect
- Integrity
- Accountability

**Sample Questions:**
- "Tell me about a time you collaborated across teams"
- "Describe handling constructive criticism"
- "Tell me about a time you learned from failure"

### Pro Tips
- 🎯 **Master trees** - Practice ALL tree patterns
- 🎯 **Recursion fluency** - Think recursively first
- 🎯 **Be collaborative** - Microsoft values teamwork
- 🎯 **Discuss Azure** - If you know cloud, mention it
- 🎯 **Friendly but rigorous** - Don't underestimate

### Resources
- LeetCode Microsoft tagged problems (200+)
- Focus heavily on **tree problems**

---

## Apple

### Interview Process
- **Phone Screen:** 1-2 technical (45 min each)
- **Onsite:** 4-6 rounds (coding + system design + domain-specific)
- **Duration:** 6-8 weeks total

### DSA Focus Areas
1. **Arrays & Strings** (30%)
2. **Trees** (25%)
3. **Dynamic Programming** (20%)
4. **Design Patterns** (15%) ⭐ **Unique to Apple**
5. **Linked Lists & Stacks** (10%)

### Difficulty Distribution
- **Easy:** 25%
- **Medium:** 60%
- **Hard:** 15%

### What Makes Apple Unique
- ✅ **Domain-specific round** - iOS, hardware, ML depending on role
- ✅ **Design patterns** - OOP, MVC, Singleton, Observer
- ✅ **Product thinking** - "How would you improve [Apple Product]?"
- ✅ **Attention to detail** - Code quality matters
- ✅ **Secretive** - Less info available than other MAANG

### Sample Questions (Apple-Style)
- LeetCode 1: Two Sum
- LeetCode 206: Reverse Linked List
- LeetCode 21: Merge Two Sorted Lists
- LeetCode 242: Valid Anagram
- LeetCode 347: Top K Frequent Elements

### System Design
- **Scope:** iOS/macOS features, hardware integration
- **Focus:** Performance, user experience
- **Unique:** May ask **low-level design** (classes, interfaces)
- **Duration:** 45 min

**Common Apple System Designs:**
- Design iMessage
- Design Find My iPhone
- Design Photo Library Sync
- Design AirDrop

### Behavioral
**Apple Values:**
- Innovation
- Excellence
- Attention to detail

**Sample Questions:**
- "Tell me about a project you're most proud of"
- "Describe a time you paid attention to small details"
- "Tell me about innovating on a product"

### Pro Tips
- 🎯 **Know Apple products** - Use them, understand them
- 🎯 **Design patterns fluency** - Be ready for OOP design
- 🎯 **Quality over speed** - Apple values perfection
- 🎯 **Product passion** - Show genuine interest in Apple
- 🎯 **Less leetcode grinding** - More real-world problem-solving

### Resources
- LeetCode Apple tagged problems (100+)
- Study design patterns (Gang of Four)
- Use Apple products extensively

---

## MAANG Comparison Matrix

| Aspect | Google | Meta | Amazon | Microsoft | Apple |
|--------|--------|------|--------|-----------|-------|
| **DSA Difficulty** | Medium-Hard | Medium | Medium | Easy-Medium | Easy-Medium |
| **Top Focus** | DP, Graphs | Trees, Graphs | DP, Greedy | Trees | Arrays, Design |
| **System Design Weight** | 20% | 20% | 25% | 20% | 15% |
| **Behavioral Weight** | ~30% | ~30-35% | 40-50% | ~25% | ~25% |
| **Interview Pressure** | High | High | Very High | Medium | Medium |
| **Process Duration** | 6-8 weeks | 4-6 weeks | 6-10 weeks | 4-6 weeks | 6-8 weeks |
| **Unique Aspect** | Googleyness | Move Fast | 16 Leadership Principles | Trees | Design Patterns |

---

## How to Use This Guide

### 1. Choose Your Top 2 Companies
Focus deeply on 2 companies max. Trying to prepare for all 5 dilutes your effort.

### 2. Tailor Your Study Plan
- **Targeting Google?** → Extra DP, graph problems
- **Targeting Meta?** → Extra trees, BFS/DFS
- **Targeting Amazon?** → Write 30 STAR stories
- **Targeting Microsoft?** → Master all tree patterns
- **Targeting Apple?** → Study design patterns

### 3. Solve Company-Tagged Problems
Use LeetCode's company filter (requires premium):
- Google: 200+ problems
- Meta: 150+ problems
- Amazon: 300+ problems
- Microsoft: 200+ problems
- Apple: 100+ problems

### 4. Study Company-Specific System Designs
- **E-commerce?** → Amazon patterns
- **Social media?** → Meta patterns
- **Search/Ads?** → Google patterns
- **Enterprise software?** → Microsoft patterns
- **Consumer products?** → Apple patterns

---

## General MAANG Tips

### All Companies Value:
✅ **Communication** - Think out loud  
✅ **Problem-solving process** - Show your approach  
✅ **Code quality** - Clean, tested, maintainable  
✅ **Time/space complexity** - Always discuss  
✅ **Handling ambiguity** - Ask clarifying questions  
✅ **Humility** - Admit when you don't know  
✅ **Curiosity** - Ask questions about the company  

### Red Flags to Avoid:
❌ **Silent solving** - Not explaining your thought process  
❌ **Jumping to code** - Not discussing approach first  
❌ **Giving up** - Show persistence  
❌ **Memorized solutions** - Interviewers can tell  
❌ **Arrogance** - Being dismissive or overconfident  
❌ **No questions for interviewer** - Shows lack of interest  

---

## Final Strategy

**Week 1-4:** Build DSA fundamentals (all companies)  
**Week 5-6:** Focus on top 2 company patterns  
**Week 7:** Solve company-tagged problems exclusively  
**Week 8:** Mock interviews in company style  

**Remember:** Quality preparation for 2 companies > superficial prep for 5.

Good luck! 💪
