# 🏋️ SQL Query Practice Set

> ~12 worked query problems, easy → hard. Try each against the schema before reading the solution.
> Patterns are explained in [sql-query-patterns.md](sql-query-patterns.md). Tags are indicative
> (`Easy/Med/Hard` · common companies), not guarantees.

## Schema

```sql
Employee(id, name, salary, dept_id, manager_id, hire_date)
Department(id, name)
Sales(id, emp_id, amount, sold_at)
Users(id, email, signup_date)
Logins(user_id, login_date)
```

---

### 1. Employees earning more than 50k `Easy` · `MAANG`
```sql
SELECT name, salary FROM Employee WHERE salary > 50000;
```
*Tests:* basic filtering.

### 2. Headcount per department `Easy` · `MAANG`
```sql
SELECT d.name, COUNT(*) AS headcount
FROM Employee e JOIN Department d ON e.dept_id = d.id
GROUP BY d.name;
```
*Tests:* JOIN + GROUP BY + COUNT.

### 3. Departments with average salary above 60k `Easy` · `Amazon`
```sql
SELECT d.name, AVG(e.salary) AS avg_sal
FROM Employee e JOIN Department d ON e.dept_id = d.id
GROUP BY d.name
HAVING AVG(e.salary) > 60000;
```
*Tests:* HAVING (group filter) vs WHERE.

### 4. Find duplicate emails `Easy` · `MAANG`
```sql
SELECT email, COUNT(*) AS cnt
FROM Users GROUP BY email HAVING COUNT(*) > 1;
```
*Tests:* GROUP BY + HAVING to detect duplicates.

### 5. Employees with no manager `Easy` · `Startups`
```sql
SELECT name FROM Employee WHERE manager_id IS NULL;
```
*Tests:* NULL handling (`IS NULL`, not `= NULL`).

### 6. Each employee with their manager's name `Med` · `MAANG`
```sql
SELECT e.name AS employee, m.name AS manager
FROM Employee e LEFT JOIN Employee m ON e.manager_id = m.id;
```
*Tests:* self-join + LEFT JOIN (keep managerless employees).

### 7. 2nd-highest salary `Med` · `MAANG`
```sql
WITH ranked AS (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk FROM Employee
)
SELECT DISTINCT salary FROM ranked WHERE rnk = 2;
```
*Tests:* window ranking + tie semantics. Clarify distinct vs offset.

### 8. Top earner per department `Med` · `Amazon`
```sql
WITH ranked AS (
    SELECT name, dept_id, salary,
           ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS rn
    FROM Employee
)
SELECT name, dept_id, salary FROM ranked WHERE rn = 1;
```
*Tests:* per-group top-N with PARTITION BY.

### 9. Employees earning above their department average `Med` · `Google`
```sql
SELECT e.name, e.salary
FROM Employee e
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM Employee e2 WHERE e2.dept_id = e.dept_id
);
```
*Tests:* correlated subquery (per-row aggregate comparison).

### 10. Running total of sales over time `Med` · `Meta`
```sql
SELECT sold_at, amount,
       SUM(amount) OVER (ORDER BY sold_at
                         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM Sales;
```
*Tests:* windowed running aggregate.

### 11. Users who logged in on consecutive days `Hard` · `Meta`
```sql
WITH numbered AS (
    SELECT user_id, login_date,
           login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::int AS grp
    FROM (SELECT DISTINCT user_id, login_date FROM Logins) d
)
SELECT user_id, MIN(login_date) AS streak_start, COUNT(*) AS streak_len
FROM numbered
GROUP BY user_id, grp
HAVING COUNT(*) >= 2;
```
*Tests:* the "gaps and islands" trick - a date minus its row number is constant within a consecutive
run, so grouping by it finds streaks.

### 12. Month-over-month sales growth `Hard` · `Amazon`
```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', sold_at) AS mon, SUM(amount) AS total
    FROM Sales GROUP BY DATE_TRUNC('month', sold_at)
)
SELECT mon, total,
       total - LAG(total) OVER (ORDER BY mon) AS mom_change
FROM monthly ORDER BY mon;
```
*Tests:* date bucketing + LAG for period-over-period comparison.

---

## Notes

- Syntax leans PostgreSQL (`DATE_TRUNC`, `::int`); adjust for MySQL (`DATE_FORMAT`, `CAST`).
- For "nth-highest" / "top per group," always clarify tie handling (ROW_NUMBER vs DENSE_RANK).
- The gaps-and-islands pattern (Q11) recurs for streaks, sessions, and consecutive-range problems.

## Related

- Pattern explanations → [sql-query-patterns.md](sql-query-patterns.md)
- Theory → [sql-theory-qa.md](sql-theory-qa.md)
- Q&A → [QA-Bank/qa-databases.md](../QA-Bank/qa-databases.md)
