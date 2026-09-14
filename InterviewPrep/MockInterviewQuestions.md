# Mock Interview Questions

A comprehensive collection of questions organized by difficulty and topic to practice for technical interviews at top tech companies.

---

## How to Use This Guide

### **Week 8 Mock Interview Schedule:**
- **Days 1-2**: Easy/Medium questions (warm-up)
- **Days 3-5**: Medium/Hard questions (peak difficulty)
- **Days 6-7**: Company-specific mocks (simulate real interviews)

### **Format:**
Each mock interview should last 45-60 minutes:
- 5 min: Introduction, clarifying questions
- 35-40 min: Problem solving (think aloud!)
- 10-15 min: Questions for interviewer, wrap-up

### **Grading Yourself:**
After each mock, evaluate:
- ✅ **Problem Understanding** (asked clarifying questions?)
- ✅ **Approach** (discussed multiple approaches?)
- ✅ **Code Quality** (clean, readable, idiomatic?)
- ✅ **Testing** (thought about edge cases?)
- ✅ **Communication** (explained thought process?)
- ✅ **Time Management** (finished on time?)

---

## Mock Interview Set 1: Easy/Medium (Warm-up)

**Duration:** 45 minutes  
**Target:** Get comfortable with interview format

### **Problem 1: Two Sum Variants (15 min)**
```
Given an array of integers and a target, find two numbers that add up to target.

Follow-ups:
1. What if array is sorted? (Two pointers: O(n))
2. What if we need all pairs? (Set-based approach)
3. What if we need to find three numbers (3Sum)? (O(n²))
4. What if duplicates matter?

Test cases:
- [2,7,11,15], target=9 → [0,1]
- [3,2,4], target=6 → [1,2]
- [3,3], target=6 → [0,1]
- [], target=0 → [] (edge case)
```

### **Problem 2: Valid Parentheses (15 min)**
```
Given a string containing just '(', ')', '{', '}', '[', ']', 
determine if the input string is valid.

Examples:
- "()" → true
- "()[]{}" → true
- "(]" → false
- "([)]" → false
- "{[]}" → true

Follow-ups:
1. What if we need to find minimum additions to make valid?
2. What if we need to remove minimum to make valid?
3. Handle nested depths?
```

### **Problem 3: Merge Two Sorted Lists (15 min)**
```
Merge two sorted linked lists.

Example:
list1 = 1→2→4
list2 = 1→3→4
output = 1→1→2→3→4→4

Follow-ups:
1. Merge K sorted lists (use heap)
2. Merge in-place without extra space
3. What if lists have cycles?
```

---

## Mock Interview Set 2: Medium (Core Patterns)

**Duration:** 45-60 minutes  
**Target:** Pattern recognition and optimization

### **Problem 1: LRU Cache (30 min)**
```
Design and implement an LRU (Least Recently Used) cache.

Operations:
- get(key): Get value (return -1 if not exists), mark as recently used
- put(key, value): Set value, evict LRU if at capacity

Requirements:
- O(1) get
- O(1) put

Example:
LRUCache cache = new LRUCache(2); // capacity = 2
cache.put(1, 1);
cache.put(2, 2);
cache.get(1);       // returns 1
cache.put(3, 3);    // evicts key 2
cache.get(2);       // returns -1 (not found)

Follow-ups:
1. Thread safety? (locks, concurrent access)
2. Persistent storage?
3. LFU (Least Frequently Used) instead?
4. TTL (time-to-live) support?

Implementation hint: HashMap + DoublyLinkedList
```

### **Problem 2: Word Break (15 min)**
```
Given string s and dictionary wordDict, return true if s can be 
segmented into space-separated sequence of dictionary words.

Examples:
- s = "leetcode", wordDict = ["leet","code"] → true
- s = "applepenapple", wordDict = ["apple","pen"] → true
- s = "catsandog", wordDict = ["cats","dog","sand","and","cat"] → false

Follow-ups:
1. Return all possible sentences (DFS + backtracking)
2. Minimum number of words needed?
3. What if dictionary is very large? (Trie)

Pattern: Dynamic Programming
```

---

## Mock Interview Set 3: Medium/Hard (Challenging)

**Duration:** 60 minutes  
**Target:** Advanced problem-solving

### **Problem 1: Design Twitter (45 min)**
```
Design a simplified version of Twitter with:
1. postTweet(userId, tweetId): Create new tweet
2. getNewsFeed(userId): Retrieve 10 most recent tweets 
   from user and people they follow
3. follow(followerId, followeeId): Follower follows followee
4. unfollow(followerId, followeeId): Follower unfollows followee

Example:
Twitter twitter = new Twitter();
twitter.postTweet(1, 5);
twitter.getNewsFeed(1);   // [5]
twitter.follow(1, 2);
twitter.postTweet(2, 6);
twitter.getNewsFeed(1);   // [6, 5]
twitter.unfollow(1, 2);
twitter.getNewsFeed(1);   // [5]

Follow-ups:
1. Scale to millions of users (sharding, caching)
2. Trending topics
3. Retweets, likes
4. Search functionality

Data structures: HashMap, Heap (for merge K sorted lists)
```

### **Problem 2: Serialize and Deserialize Binary Tree (15 min)**
```
Design algorithm to serialize/deserialize binary tree.

Example:
    1
   / \
  2   3
     / \
    4   5

serialize(root) → "1,2,#,#,3,4,#,#,5,#,#"
deserialize(data) → reconstruct tree

Follow-ups:
1. Multiple serialization formats (BFS, DFS, level-order)
2. Optimize for space
3. Handle null nodes efficiently
4. N-ary tree instead

Pattern: Tree traversal (preorder/level-order)
```

---

## Mock Interview Set 4: Hard (Advanced)

**Duration:** 60 minutes  
**Target:** Demonstrate expertise

### **Problem 1: Median of Data Stream (20 min)**
```
Design data structure that supports:
1. addNum(int num): Add integer from data stream
2. findMedian(): Return median of all elements so far

Example:
MedianFinder mf = new MedianFinder();
mf.addNum(1);
mf.addNum(2);
mf.findMedian(); // 1.5
mf.addNum(3);
mf.findMedian(); // 2

Follow-ups:
1. Optimize for space
2. Parallel streams
3. 95th percentile instead of median
4. Sliding window median

Solution: Two heaps (max-heap for lower half, min-heap for upper half)
Time: O(log n) add, O(1) median
```

### **Problem 2: Trapping Rain Water (20 min)**
```
Given n non-negative integers representing elevation map 
where width of each bar is 1, compute how much water can trap.

Example:
height = [0,1,0,2,1,0,1,3,2,1,2,1]

           #
     #~~~~~##~#
 _#~##~####### 
 0 1 0 2 1 0 1 3 2 1 2 1     (# = bar, ~ = trapped water)

Output: 6   (units of water trapped between the bars)

Follow-ups:
1. 2D version (water trapped in 2D grid)
2. Optimize space to O(1)
3. What if heights can be negative?

Approaches:
- Two pointers: O(n) time, O(1) space ⭐
- DP: O(n) time, O(n) space
- Stack: O(n) time, O(n) space
```

### **Problem 3: Regular Expression Matching (20 min)**
```
Implement regex matching with '.' and '*':
- '.' matches any single character
- '*' matches zero or more of preceding element

Examples:
- s = "aa", p = "a" → false
- s = "aa", p = "a*" → true
- s = "ab", p = ".*" → true

Follow-ups:
1. Add '+' (one or more)
2. Add '?' (zero or one)
3. Wildcard matching (different from regex)

Pattern: Dynamic Programming (2D DP)
Time: O(m*n), Space: O(m*n)
```

---

## Company-Specific Mock Interviews

### **Google Style (60 min)**

**Problem 1: Number of Islands (20 min)**
```
Given 2D grid of '1's (land) and '0's (water), 
count number of islands.

Example:
11110
11010
11000
00000
Output: 1

Follow-up (Google loves this):
1. What if grid doesn't fit in memory? (Map-Reduce)
2. What if grid updates dynamically? (Union-Find)
3. Count island perimeters?
4. Largest island by area?

Expected: Multiple solutions (DFS, BFS, Union-Find)
Google wants: Optimal solution + discussion of trade-offs
```

**Problem 2: Design Google Docs (Real-time Collaboration) (40 min)**
```
Design real-time collaborative document editing.

Requirements:
1. Multiple users can edit simultaneously
2. Changes appear in real-time (<100ms latency)
3. Conflict resolution (two users edit same word)
4. Offline support (edit offline, sync later)

Key concepts to discuss:
- Operational Transformation (OT) or CRDT
- WebSocket for real-time updates
- Conflict resolution strategies
- Data structures (piece table, rope)
- Scale to millions of documents

Google grading:
- Problem clarification (5 min)
- High-level design (15 min)
- Deep dive on conflict resolution (15 min)
- Scaling considerations (5 min)
```

---

### **Meta Style (60 min)**

**Problem 1: Clone Graph (15 min)**
```
Clone an undirected graph. Each node contains value and list of neighbors.

Example:
1 --- 2
|     |
4 --- 3

Follow-ups (Meta style):
1. Scale to billion nodes (distributed system)
2. Optimize for space (don't use HashMap)
3. Clone only reachable nodes from given node
4. Detect if graph is bipartite while cloning

Meta wants: Quick solution + scaling discussion
```

**Problem 2: Design Instagram Feed (45 min)**
```
Design Instagram's news feed.

Requirements:
1. User follows other users
2. Feed shows photos from followed users (reverse chronological)
3. Like, comment on photos
4. Scale to 500M users

Key discussions:
- Fan-out on write vs fan-out on read
- Caching strategy (Redis)
- Database schema (PostgreSQL + Cassandra)
- CDN for images
- Ranking algorithm (ML-based)

Meta grading:
- Capacity estimation (5 min)
- API design (5 min)
- Database schema (10 min)
- Feed generation algorithm (15 min)  ⭐ Most important
- Scaling and optimization (10 min)

Meta loves: Metrics, A/B testing discussion
```

---

### **Amazon Style (60 min)**

**Problem 1: Two Sum - Leadership Principles (10 min)**
```
Standard Two Sum, but interviewer will ask:
- "Which Leadership Principle does your solution demonstrate?"
- "How would you test this code?" (Insist on Highest Standards)
- "What if constraints change?" (Are Right, A Lot)

Amazon behavioral twist: Even coding questions test LPs
```

**Problem 2: Design Amazon Cart (50 min)**
```
Design Amazon's shopping cart.

Requirements:
1. Add/remove items
2. Update quantities
3. Calculate total (with tax, discounts)
4. Persist cart across sessions
5. Handle inventory (item out of stock)

Leadership Principles to demonstrate:
- Customer Obsession: Handle out-of-stock gracefully
- Ownership: Think about edge cases
- Invent and Simplify: Simple API design
- Frugality: Efficient data structures
- Dive Deep: Explain tax calculation complexity

Amazon grading:
- Functional design (20 min)
- Edge cases and error handling (15 min) ⭐ Amazon loves this
- Scalability (10 min)
- Which LPs demonstrated (5 min)

Amazon unique: They WILL ask which LP your design shows
```

---

## System Design Mock Topics (Choose 1-2)

### **Easy:**
1. **URL Shortener** (Bit.ly)
2. **Pastebin** (Share code snippets)
3. **Rate Limiter** (API throttling)

### **Medium:**
1. **Design Twitter** (News feed, follow/unfollow)
2. **Design Instagram** (Photo sharing, feed)
3. **Design Dropbox** (File sync and sharing)
4. **Design Uber** (Ride matching)

### **Hard:**
1. **Design YouTube** (Video streaming)
2. **Design Netflix** (Adaptive bitrate streaming)
3. **Design WhatsApp** (Real-time messaging)
4. **Design Ticketmaster** (High concurrency booking)

**Structure (45 min):**
- Requirements clarification (5 min)
- Capacity estimation (5 min)
- API design (5 min)
- Database schema (10 min)
- High-level design (10 min)
- Deep dive (10 min)

---

## Behavioral Mock Questions (15-20 min)

### **Must Prepare:**

**General:**
1. Tell me about yourself (2 min pitch)
2. Why do you want to work here?
3. Where do you see yourself in 5 years?

**Conflict:**
1. Tell me about a time you disagreed with a teammate
2. Describe a conflict with your manager
3. How do you handle feedback?

**Failure:**
1. Tell me about your biggest failure
2. Describe a time you missed a deadline
3. When did you make a wrong technical decision?

**Leadership:**
1. Give an example of when you showed leadership
2. Tell me about a time you mentored someone
3. Describe when you influenced without authority

**Problem Solving:**
1. Tell me about a complex problem you solved
2. Describe when you learned a new technology quickly
3. When did you have to make a decision with incomplete information?

---

## ✅ Pre-Interview Checklist

**Day Before:**
- [ ] Review your resume (know every project deeply)
- [ ] Sleep 7-8 hours
- [ ] Prepare workspace (quiet, good lighting)
- [ ] Test video/audio (Zoom, Google Meet)
- [ ] Prepare questions to ask interviewer (3-5 questions)

**1 Hour Before:**
- [ ] Solve 1 easy problem (warm-up brain)
- [ ] Review core patterns (sliding window, two pointers, etc.)
- [ ] Practice STAR format (1-2 behavioral stories)
- [ ] Use bathroom, get water
- [ ] Close all distracting tabs/apps

**During Interview:**
- [ ] Think aloud (explain your thought process)
- [ ] Ask clarifying questions (constraints, edge cases)
- [ ] Discuss multiple approaches before coding
- [ ] Write clean, readable code (naming matters!)
- [ ] Test with example inputs
- [ ] Discuss time/space complexity
- [ ] Ask thoughtful questions at end

**After Interview:**
- [ ] Write down all questions asked
- [ ] Note what went well and what to improve
- [ ] Send thank-you email within 24 hours

---

## Mock Interview Partners

**Where to Find:**
1. **Pramp** (free, peer-to-peer)
2. **Interviewing.io** (free + paid with MAANG interviewers)
3. **LeetCode** (mock assessments)
4. **Friends/colleagues** (reciprocal practice)

**Best Practice:**
- Do 10+ mocks before real interview
- Get feedback after each mock
- Record yourself (watch for verbal tics, filler words)
- Simulate real environment (time pressure, video call)

---

## Progress Tracker

Track your mock interview performance:

| Date | Problem/Topic | Difficulty | Time Taken | Solved? | Notes |
|------|---------------|-----------|------------|---------|-------|
| | | | | | |
| | | | | | |
| | | | | | |

**Goal:** 10 successful mocks before real interviews

---

## Final Tips

### **Red Flags to Avoid:**
- ❌ Jumping into code without discussing approach
- ❌ Not asking clarifying questions
- ❌ Writing buggy code without testing
- ❌ Giving up when stuck
- ❌ Not thinking aloud (silent coding)
- ❌ Ignoring hints from interviewer
- ❌ Poor communication skills

### **Green Flags (What Interviewers Love):**
- ✅ Ask about constraints (input size, edge cases)
- ✅ Discuss multiple approaches (brute force → optimal)
- ✅ Analyze time/space complexity
- ✅ Write clean, readable code
- ✅ Test code with examples
- ✅ Handle edge cases
- ✅ Communicate thought process clearly
- ✅ Stay calm under pressure

### **If You Get Stuck:**
1. **Talk through the problem** - Explaining helps clarify
2. **Use examples** - Walk through small input
3. **Ask for hints** - "I'm considering X, is that on the right track?"
4. **Start with brute force** - Better than nothing, optimize later
5. **Take a breath** - 10 seconds of silence is OK to think

---

## Summary

**Mock Interview Best Practices:**
- 🎯 Practice 10+ mocks before real interviews
- ⏱️ Simulate real conditions (45-60 min, video call)
- 📝 Track performance, identify weak areas
- 🔄 Review mistakes, redo failed problems
- 🤝 Find mock partners (Pramp, Interviewing.io)
- 📊 Cover all types: DSA, System Design, Behavioral

**Week 8 Schedule:**
- Days 1-2: Easy/Medium warm-ups
- Days 3-5: Medium/Hard challenges
- Days 6-7: Full company-specific simulations

**Remember:**
- Mocks are for learning, not passing
- Feedback is gold - ask specific questions
- Every failure in mock = success in real interview
- Communication matters as much as correct answer

Good luck! 🚀

**Next Steps:**
- Schedule first mock interview today
- Review [10-Week Study Plan](StudyPlan-10weeks.md) for context
- Prepare STAR stories from [Behavioral Guide](../Behavioral/BehavioralGuide.md)
