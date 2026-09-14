# 📝 SQL Query Patterns

> The query shapes interviewers ask again and again (LeetCode SQL 50 style). Each has a worked query
> + **what it's testing**. Theory behind them: [SQL Theory Q&A](sql-theory-qa.md). Drill:
> [Query Practice Set](query-practice-set.md).

Sample schema used below:
```sql
Employee(id, name, salary, dept_id, manager_id)
Department(id, name)
Sales(id, emp_id, amount, sold_at)
```

---

## Joins (inner / outer / self)

```sql
-- Employees with their department name (INNER: only matched rows)
SELECT e.name, d.name AS dept
FROM Employee e
JOIN Department d ON e.dept_id = d.id;

-- All employees, dept name NULL if unassigned (LEFT OUTER)
SELECT e.name, d.name AS dept
FROM Employee e
LEFT JOIN Department d ON e.dept_id = d.id;

-- Self-join: each employee with their manager's name
SELECT e.name AS employee, m.name AS manager
FROM Employee e
LEFT JOIN Employee m ON e.manager_id = m.id;
```
**Tests:** do you know INNER drops unmatched rows while LEFT keeps them (NULLs), and that a table can
join to itself via aliases.

---

## GROUP BY + HAVING + aggregates

```sql
-- Departments with average salary > 50k (HAVING filters groups, WHERE filters rows)
SELECT d.name, COUNT(*) AS headcount, AVG(e.salary) AS avg_sal
FROM Employee e
JOIN Department d ON e.dept_id = d.id
WHERE e.salary IS NOT NULL          -- row filter (before grouping)
GROUP BY d.name
HAVING AVG(e.salary) > 50000;       -- group filter (after aggregation)
```
**Tests:** the WHERE-vs-HAVING distinction (row filter before grouping vs aggregate filter after) -
a top interview probe.

---

## Subqueries vs CTEs

```sql
-- Employees earning above their department's average (correlated subquery)
SELECT e.name, e.salary
FROM Employee e
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM Employee e2 WHERE e2.dept_id = e.dept_id
);

-- Same idea, readable with a CTE
WITH dept_avg AS (
    SELECT dept_id, AVG(salary) AS avg_sal FROM Employee GROUP BY dept_id
)
SELECT e.name, e.salary
FROM Employee e
JOIN dept_avg da ON e.dept_id = da.dept_id
WHERE e.salary > da.avg_sal;
```
**Tests:** correlated subqueries (run per outer row) vs CTEs (named, readable, reusable). Prefer CTEs
for clarity; know both.

---

## Window functions (the mid-level differentiator)

```sql
-- Rank employees by salary within each department
SELECT name, dept_id, salary,
       ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn,
       RANK()       OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS drnk
FROM Employee;

-- Running total of sales over time
SELECT sold_at, amount,
       SUM(amount) OVER (ORDER BY sold_at
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM Sales;

-- Compare each sale to the previous one (LAG)
SELECT sold_at, amount,
       amount - LAG(amount) OVER (ORDER BY sold_at) AS delta_vs_prev
FROM Sales;
```
**Tests:** window functions keep every row (unlike GROUP BY) while computing over a partition.
Know **ROW_NUMBER vs RANK vs DENSE_RANK** (tie handling) and LAG/LEAD for row-to-row comparisons.

---

## Nth-highest value

```sql
-- 2nd-highest salary (window approach - handles ties predictably)
WITH ranked AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
    FROM Employee
)
SELECT DISTINCT salary FROM ranked WHERE rnk = 2;
```
**Tests:** the classic. Discuss whether "2nd highest" means 2nd distinct value (DENSE_RANK) or
literal offset (ROW_NUMBER / `LIMIT 1 OFFSET 1`), and how ties change the answer.

---

## Finding & removing duplicates

```sql
-- Find duplicate emails
SELECT email, COUNT(*) FROM Users GROUP BY email HAVING COUNT(*) > 1;

-- Keep one row per duplicate group, delete the rest (by lowest id)
WITH dupes AS (
    SELECT id, ROW_NUMBER() OVER (PARTITION BY email ORDER BY id) AS rn
    FROM Users
)
DELETE FROM Users WHERE id IN (SELECT id FROM dupes WHERE rn > 1);
```
**Tests:** GROUP BY + HAVING to detect, and ROW_NUMBER partitioned by the dup key to keep exactly one.

---

## Pivot (rows → columns)

```sql
-- Sales per employee split into columns by year (conditional aggregation)
SELECT emp_id,
       SUM(CASE WHEN EXTRACT(YEAR FROM sold_at) = 2024 THEN amount ELSE 0 END) AS y2024,
       SUM(CASE WHEN EXTRACT(YEAR FROM sold_at) = 2025 THEN amount ELSE 0 END) AS y2025
FROM Sales
GROUP BY emp_id;
```
**Tests:** pivoting with `CASE` inside an aggregate - the portable way (vs vendor `PIVOT`).

---

## Date bucketing

```sql
-- Daily sales totals
SELECT DATE_TRUNC('day', sold_at) AS day, SUM(amount) AS total
FROM Sales
GROUP BY DATE_TRUNC('day', sold_at)
ORDER BY day;
```
**Tests:** grouping by a truncated/bucketed date rather than the raw timestamp - common in analytics
questions.

---

## Common interview traps

- Putting an aggregate in `WHERE` (use `HAVING`).
- Forgetting `LEFT JOIN` + `WHERE right.col = x` silently turns it back into an inner join (filter in
  the `ON` instead).
- Assuming `ROW_NUMBER` and `RANK` are the same - they differ on ties.
- `COUNT(*)` vs `COUNT(col)` - the latter skips NULLs.
- Selecting non-aggregated columns not in `GROUP BY` (invalid in standard SQL).

## Related

- Theory behind these → [SQL Theory Q&A](sql-theory-qa.md)
- Timed practice → [Query Practice Set](query-practice-set.md)
- Q&A → [Databases Q&A](../QA-Bank/qa-databases.md)
