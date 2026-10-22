# Low-Level Design (LLD) Interview Guide

!!! abstract "This page is the compact code reference for the LLD section"
    SOLID + GoF patterns + a few LLD problems, all runnable, in one place. For the fuller
    treatment, start here instead:

    - **[Overview](lld-overview.md)** - what LLD is, formats, rubric, the 7-step framework
    - **[Roadmap](roadmap.md)** - OOP → SOLID → patterns → UML in depth, with trade-offs
    - **[Concurrency](concurrency.md)** - thread-safety, the double-booking fix (SDE-2)
    - **[Extended Patterns](patterns-extended.md)** - Command, CoR, Proxy, Facade, and more
    - **[Java Cheat Sheet](java-cheatsheet.md)** · **[Worked Problems](worked-problems.md)** · **[Mental Models](lld-mental-models.md)**

## What is LLD?

Low-Level Design focuses on the **code-level architecture** of a system - class diagrams, design patterns, interfaces, and object relationships. LLD interviews are common at the entry-to-mid level and test your ability to translate requirements into clean, extensible code.

> 🧭 Prefer the *visual* thinking layer - the modeling process as a flowchart, a "which pattern?"
> decision tree, a SOLID-fix map, and a UML class-diagram example? See
> **[LLD Mental Models](lld-mental-models.md)**.

**LLD vs HLD:**
| | High-Level Design | Low-Level Design |
|--|--|--|
| Focus | System components, data flow | Classes, interfaces, patterns |
| Output | Architecture diagram | Class diagram + code |
| Scale | Distributed systems | Single service/module |
| Time | 30-45 min | 30-45 min |

---

## LLD Interview Framework (Use Every Time)

### Step 1: Clarify Requirements (5 min)
- What are the core entities?
- What operations are needed?
- Any constraints (thread safety, extensibility)?

### Step 2: Identify Entities & Relationships (5 min)
- Nouns → Classes
- Verbs → Methods
- Relationships → Associations, Inheritance, Composition

### Step 3: Define Interfaces & Abstractions (5 min)
- What should be abstract vs concrete?
- Where do you need extensibility?

### Step 4: Apply Design Patterns (10 min)
- Which patterns fit naturally?
- Don't force patterns - use them when they solve a real problem

### Step 5: Write Core Code (15 min)
- Implement key classes
- Show method signatures and logic
- Handle edge cases

### Step 6: Discuss Trade-offs (5 min)
- Thread safety
- Extensibility
- Performance

---

## SOLID Principles

Every LLD answer should demonstrate SOLID awareness.

### S - Single Responsibility Principle
> A class should have only one reason to change.

```java
// ❌ Bad: One class doing too much
class UserManager {
    void createUser(Data data) { }
    void sendWelcomeEmail(User user) { }  // Email logic here?
    void saveToDatabase(User user) { }    // DB logic here?
}

// ✅ Good: Separate responsibilities
class UserService {
    private final UserRepository userRepo;
    private final EmailService emailService;

    UserService(UserRepository userRepo, EmailService emailService) {
        this.userRepo = userRepo;
        this.emailService = emailService;
    }

    User createUser(Data data) {
        User user = new User(data);
        userRepo.save(user);
        emailService.sendWelcome(user);
        return user;
    }
}

class UserRepository {
    void save(User user) { }       // DB logic
    User findById(String id) { return null; }  // DB logic
}

class EmailService {
    void sendWelcome(User user) { }  // Email logic
}
```

---

### O - Open/Closed Principle
> Open for extension, closed for modification.

```java
// ❌ Bad: Adding a new payment type requires modifying the existing class
class PaymentProcessor {
    void process(String type, double amount) {
        if (type.equals("credit")) {
            // ...
        } else if (type.equals("debit")) {
            // ...
        } else if (type.equals("upi")) {
            // ...  keep adding branches?
        }
    }
}

// ✅ Good: Extend without modifying
interface Payment {
    void execute();
}

class PaymentProcessor {
    void process(Payment payment) {
        payment.execute();  // polymorphism
    }
}

class CreditCardPayment implements Payment {
    public void execute() { }  // credit card logic
}

class UPIPayment implements Payment {
    public void execute() { }  // UPI logic
}

class CryptoPayment implements Payment {  // new type - no existing code changed
    public void execute() { }  // crypto logic
}
```

---

### L - Liskov Substitution Principle
> Subtypes must be substitutable for their base types.

```java
// ❌ Bad: Square breaks Rectangle's contract
class Rectangle {
    protected int width, height;
    void setWidth(int w)  { this.width = w; }
    void setHeight(int h) { this.height = h; }
    int area() { return width * height; }
}

class Square extends Rectangle {
    void setWidth(int w)  { this.width = this.height = w; }   // breaks LSP!
    void setHeight(int h) { this.width = this.height = h; }   // breaks LSP!
}

// ✅ Good: Use a separate hierarchy
interface Shape {
    int area();
}

class Rectangle implements Shape {
    private final int w, h;
    Rectangle(int w, int h) { this.w = w; this.h = h; }
    public int area() { return w * h; }
}

class Square implements Shape {
    private final int side;
    Square(int side) { this.side = side; }
    public int area() { return side * side; }
}
```

---

### I - Interface Segregation Principle
> Clients should not be forced to depend on interfaces they don't use.

```java
// ❌ Bad: Fat interface forces all implementors to implement everything
interface Animal {
    void eat();
    void sleep();
    void fly();   // not all animals fly!
    void swim();  // not all animals swim!
}

// ✅ Good: Segregated interfaces
interface Animal {
    void eat();
    void sleep();
}

interface Flyable {
    void fly();
}

interface Swimmable {
    void swim();
}

// Duck can fly AND swim
class Duck implements Animal, Flyable, Swimmable {
    public void eat() { }
    public void sleep() { }
    public void fly() { }
    public void swim() { }
}

// Dog can only swim
class Dog implements Animal, Swimmable {
    public void eat() { }
    public void sleep() { }
    public void swim() { }
}
```

---

### D - Dependency Inversion Principle
> Depend on abstractions, not concretions.

```java
// ❌ Bad: High-level module depends on a low-level module
class OrderService {
    private final MySQLDatabase db = new MySQLDatabase();  // tightly coupled to MySQL!
}

// ✅ Good: Depend on an abstraction (inject the dependency)
interface Database {
    Object save(Data data);
}

class OrderService {
    private final Database db;
    OrderService(Database db) { this.db = db; }  // injected

    Object createOrder(Data data) {
        return db.save(data);
    }
}

// Swap implementations without changing OrderService
OrderService mysqlService = new OrderService(new MySQLDatabase());
OrderService mongoService = new OrderService(new MongoDatabase());
OrderService testService  = new OrderService(new InMemoryDatabase());
```

---

## Design Patterns (Interview Essentials)

### Creational Patterns

#### Singleton
> Ensure only one instance of a class exists.

```java
public class DatabaseConnection {
    private static DatabaseConnection instance;
    private final String connection;

    private DatabaseConnection(String host) {    // private constructor
        this.connection = connect(host);
    }

    // thread-safe lazy init via synchronized getter
    public static synchronized DatabaseConnection getInstance(String host) {
        if (instance == null) {
            instance = new DatabaseConnection(host);
        }
        return instance;
    }

    private static String connect(String host) {
        return "connected to " + host;
    }
}

// Usage
DatabaseConnection db1 = DatabaseConnection.getInstance("localhost");
DatabaseConnection db2 = DatabaseConnection.getInstance("localhost");
System.out.println(db1 == db2);  // true
```

**Use when:** Logger, config manager, connection pool, cache

---

#### Factory Method
> Let a factory decide which class to instantiate.

```java
interface Notification {
    void send(String to, String message);
}

class EmailNotification implements Notification {
    public void send(String to, String message) {
        System.out.println("Email to " + to + ": " + message);
    }
}

class SMSNotification implements Notification {
    public void send(String to, String message) {
        System.out.println("SMS to " + to + ": " + message);
    }
}

class PushNotification implements Notification {
    public void send(String to, String message) {
        System.out.println("Push to " + to + ": " + message);
    }
}

class NotificationFactory {
    static Notification create(String type) {
        switch (type) {
            case "email": return new EmailNotification();
            case "sms":   return new SMSNotification();
            case "push":  return new PushNotification();
            default: throw new IllegalArgumentException("Unknown type: " + type);
        }
    }
}

// Usage
Notification notif = NotificationFactory.create("email");
notif.send("user@example.com", "Welcome!");
```

**Use when:** Object creation logic is complex or varies by type

---

#### Builder
> Construct complex objects step by step.

Each setter returns `this` so calls chain fluently, and a final `build()` produces the object:
```java
String sql = new QueryBuilder().from("users").select("id", "name")
                 .where("age > 18").limit(10).build();
// each method sets a field and returns this; build() assembles the final result
```

**Use when:** Object has many optional parameters (avoids telescoping constructors)

---

### Structural Patterns

#### Adapter
> Convert one interface to another that clients expect.

Wrap the incompatible object and expose the interface your app wants; the adapter translates
calls/return shapes internally:
```java
class PaymentAdapter {            // app calls pay(...); legacy exposes makePayment(...)
    private final LegacyGateway legacy;
    PaymentAdapter(LegacyGateway legacy) { this.legacy = legacy; }

    PayResult pay(String card, double amount, String currency) {
        LegacyResult r = legacy.makePayment(card, amount, currency);
        return new PayResult(r.status.equals("success"), r.transactionId);
    }
}
```

**Use when:** Integrating third-party libraries, legacy code migration

---

#### Decorator
> Add behavior to objects dynamically without subclassing.

Each decorator wraps a component sharing the same interface and augments its result, so you stack
them at runtime:
```java
class MilkDecorator implements Coffee {    // same interface as Coffee
    private final Coffee coffee;
    MilkDecorator(Coffee coffee) { this.coffee = coffee; }
    public int cost() { return coffee.cost() + 15; }
    public String description() { return coffee.description() + ", milk"; }
}

Coffee coffee = new MilkDecorator(new SugarDecorator(new PlainCoffee()));  // stack features
```

**Use when:** Adding features to objects at runtime (logging, auth, caching middleware)

---

#### Proxy
> Control access to an object (same interface as the real object, adds a gate).

```java
class CachingProxy implements DataService {    // same interface as the real service
    private final DataService service;
    private final Map<String, String> cache = new HashMap<>();
    CachingProxy(DataService service) { this.service = service; }

    public String fetchData(String key) {
        if (!cache.containsKey(key)) {          // add caching / auth / lazy-init here
            cache.put(key, service.fetchData(key));
        }
        return cache.get(key);
    }
}
```

**Use when:** Lazy loading, caching, access control, logging

---

### Behavioral Patterns

#### Observer
> Define a one-to-many dependency so when one object changes, all dependents are notified.

```java
interface Listener {
    void handle(String data);
}

class EventEmitter {
    private final Map<String, List<Listener>> listeners = new HashMap<>();

    EventEmitter on(String event, Listener cb) {
        listeners.computeIfAbsent(event, k -> new ArrayList<>()).add(cb);
        return this;
    }

    void off(String event, Listener cb) {
        listeners.getOrDefault(event, List.of()).remove(cb);
    }

    void emit(String event, String data) {
        for (Listener cb : listeners.getOrDefault(event, List.of())) {
            cb.handle(data);
        }
    }
}

// Usage: Order system
EventEmitter orderEvents = new EventEmitter();
orderEvents.on("order:placed", id -> System.out.println("Send confirmation email for " + id));
orderEvents.on("order:placed", id -> System.out.println("Notify warehouse for " + id));
orderEvents.on("order:placed", id -> System.out.println("Update analytics for " + id));

orderEvents.emit("order:placed", "ORD-001");
// All 3 handlers fire
```

**Use when:** Event systems, pub/sub, UI state management, notifications

---

#### Strategy
> Define a family of algorithms, encapsulate each one, make them interchangeable.

```java
interface SortStrategy {
    int[] sort(int[] arr);
}

class BubbleSort implements SortStrategy {
    public int[] sort(int[] arr) {
        int[] a = arr.clone();
        for (int i = 0; i < a.length; i++) {
            for (int j = 0; j < a.length - i - 1; j++) {
                if (a[j] > a[j + 1]) {
                    int tmp = a[j]; a[j] = a[j + 1]; a[j + 1] = tmp;
                }
            }
        }
        return a;
    }
}

class QuickSort implements SortStrategy {
    public int[] sort(int[] arr) {
        int[] a = arr.clone();
        Arrays.sort(a);   // stdlib quicksort/dual-pivot; keep the example simple
        return a;
    }
}

class Sorter {
    private SortStrategy strategy;
    Sorter(SortStrategy strategy) { this.strategy = strategy; }

    void setStrategy(SortStrategy strategy) { this.strategy = strategy; }

    int[] sort(int[] arr) { return strategy.sort(arr); }
}

// Usage
Sorter sorter = new Sorter(new QuickSort());
sorter.sort(new int[]{3, 1, 4, 1, 5});

// Swap strategy at runtime
sorter.setStrategy(new BubbleSort());
sorter.sort(new int[]{3, 1, 4, 1, 5});
```

**Use when:** Multiple algorithms for same task, runtime algorithm selection

---

#### Command
> Encapsulate a request as an object with `execute()` + `undo()`, enabling undo/redo.

Each command knows how to do and reverse itself; an invoker keeps a history stack:
```java
class InsertCommand implements Command {    // each command stores what it needs to undo
    private final String text;
    InsertCommand(String text) { this.text = text; }
    public void execute(Editor editor) { editor.text += text; }
    public void undo(Editor editor) {
        editor.text = editor.text.substring(0, editor.text.length() - text.length());
    }
}

// Invoker: execute(cmd) runs it and pushes to history; undo() pops and calls cmd.undo()
```

**Use when:** Undo/redo, transaction queues, macro recording

---

## Common LLD Interview Problems

### 1. Parking Lot

```java
// Entities: ParkingLot, ParkingFloor, ParkingSpot, Vehicle, ParkingTicket
class Vehicle {
    String plate;
    String type;  // "bike", "car", "truck"
    Vehicle(String plate, String type) { this.plate = plate; this.type = type; }
}

class ParkingSpot {
    String id;
    String type;  // "small", "medium", "large"
    Vehicle vehicle;

    ParkingSpot(String id, String type) { this.id = id; this.type = type; }

    boolean isAvailable() { return vehicle == null; }

    boolean canFit(Vehicle v) {
        Map<String, List<String>> fits = Map.of(
            "small",  List.of("bike"),
            "medium", List.of("bike", "car"),
            "large",  List.of("bike", "car", "truck"));
        return fits.get(type).contains(v.type);
    }

    void park(Vehicle v) { this.vehicle = v; }
    void vacate() { this.vehicle = null; }
}

class ParkingFloor {
    int floorNum;
    List<ParkingSpot> spots;
    ParkingFloor(int floorNum, List<ParkingSpot> spots) {
        this.floorNum = floorNum; this.spots = spots;
    }

    ParkingSpot findAvailableSpot(Vehicle v) {
        for (ParkingSpot s : spots) {
            if (s.isAvailable() && s.canFit(v)) return s;
        }
        return null;
    }
}

class ParkingTicket {
    String id;
    ParkingSpot spot;
    long entryTime;
    long exitTime;

    ParkingTicket(ParkingSpot spot) {
        this.id = "TKT-" + System.currentTimeMillis();
        this.spot = spot;
        this.entryTime = System.currentTimeMillis();
    }

    int checkout() {
        this.exitTime = System.currentTimeMillis();
        spot.vacate();
        return calculateFee();
    }

    private int calculateFee() {
        long hours = (long) Math.ceil((exitTime - entryTime) / 3_600_000.0);
        Map<String, Integer> rates = Map.of("small", 20, "medium", 40, "large", 60);
        return (int) hours * rates.get(spot.type);
    }
}

class ParkingLot {
    List<ParkingFloor> floors;
    Map<String, ParkingTicket> activeTickets = new HashMap<>();
    ParkingLot(List<ParkingFloor> floors) { this.floors = floors; }

    ParkingTicket park(Vehicle v) {
        for (ParkingFloor floor : floors) {
            ParkingSpot spot = floor.findAvailableSpot(v);
            if (spot != null) {
                spot.park(v);
                ParkingTicket ticket = new ParkingTicket(spot);
                activeTickets.put(ticket.id, ticket);
                return ticket;
            }
        }
        throw new IllegalStateException("Parking lot is full");
    }

    int checkout(String ticketId) {
        ParkingTicket ticket = activeTickets.get(ticketId);
        if (ticket == null) throw new IllegalArgumentException("Invalid ticket");
        int fee = ticket.checkout();
        activeTickets.remove(ticketId);
        return fee;
    }
}
```

---

### 2. Elevator System

```java
// Entities: ElevatorSystem, Elevator, Request, Direction
class Request {
    int floor;
    String direction;  // "up" | "down"
    Request(int floor, String direction) { this.floor = floor; this.direction = direction; }
}

class Elevator {
    int id;
    int currentFloor = 0;
    String direction = "idle";  // "up" | "down" | "idle"
    Set<Integer> destinations = new TreeSet<>();

    Elevator(int id) { this.id = id; }

    void addDestination(int floor) {
        destinations.add(floor);
        updateDirection();
    }

    void move() {
        if (destinations.isEmpty()) { direction = "idle"; return; }

        if (direction.equals("up"))        currentFloor++;
        else if (direction.equals("down")) currentFloor--;

        if (destinations.remove(currentFloor)) {
            System.out.println("Elevator " + id + " stopped at floor " + currentFloor);
        }
        updateDirection();
    }

    private void updateDirection() {
        if (destinations.isEmpty()) { direction = "idle"; return; }
        int maxDest = Collections.max(destinations);
        int minDest = Collections.min(destinations);
        if (direction.equals("up")   && maxDest > currentFloor) return;
        if (direction.equals("down") && minDest < currentFloor) return;
        direction = maxDest > currentFloor ? "up" : "down";
    }

    int distanceTo(int floor) { return Math.abs(currentFloor - floor); }
}

class ElevatorSystem {
    List<Elevator> elevators = new ArrayList<>();

    ElevatorSystem(int numElevators) {
        for (int i = 0; i < numElevators; i++) elevators.add(new Elevator(i));
    }

    // Dispatch: find nearest idle or same-direction elevator
    Elevator dispatch(Request request) {
        Elevator best = null;
        for (Elevator e : elevators) {
            boolean usable = e.direction.equals("idle") || e.direction.equals(request.direction);
            if (!usable) continue;
            if (best == null || e.distanceTo(request.floor) < best.distanceTo(request.floor)) {
                best = e;
            }
        }
        if (best == null) best = elevators.get(0);  // fall back to any elevator
        best.addDestination(request.floor);
        return best;
    }
}
```

---

### 3. Rate Limiter

```java
// Token Bucket Algorithm
class TokenBucket {
    private final double capacity;     // max tokens
    private double tokens;             // current tokens
    private final double refillRate;   // tokens per second
    private long lastRefill = System.currentTimeMillis();

    TokenBucket(double capacity, double refillRate) {
        this.capacity = capacity;
        this.tokens = capacity;
        this.refillRate = refillRate;
    }

    private void refill() {
        long now = System.currentTimeMillis();
        double elapsed = (now - lastRefill) / 1000.0;
        tokens = Math.min(capacity, tokens + elapsed * refillRate);
        lastRefill = now;
    }

    synchronized boolean consume(int count) {
        refill();
        if (tokens >= count) {
            tokens -= count;
            return true;   // allowed
        }
        return false;      // rate limited
    }
}

class RateLimiter {
    private final double capacity;
    private final double refillRate;
    private final Map<String, TokenBucket> buckets = new HashMap<>();  // userId -> bucket

    RateLimiter(double capacity, double refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
    }

    boolean isAllowed(String userId) {
        TokenBucket bucket = buckets.computeIfAbsent(
            userId, k -> new TokenBucket(capacity, refillRate));
        return bucket.consume(1);
    }
}

// Usage: 10 requests/sec per user
RateLimiter limiter = new RateLimiter(10, 10);
System.out.println(limiter.isAllowed("user1"));  // true
```

---

## Design Pattern Quick Reference

| Pattern | Category | Use When |
|---------|----------|----------|
| Singleton | Creational | One instance needed (DB, Logger) |
| Factory | Creational | Object creation varies by type |
| Builder | Creational | Complex object with many options |
| Adapter | Structural | Incompatible interfaces |
| Decorator | Structural | Add behavior dynamically |
| Proxy | Structural | Control access (cache, auth) |
| Observer | Behavioral | One-to-many event notification |
| Strategy | Behavioral | Interchangeable algorithms |
| Command | Behavioral | Undo/redo, queued operations |

---

## Common LLD Mistakes

| Mistake | Fix |
|---------|-----|
| God class (one class does everything) | Apply SRP, split responsibilities |
| Hardcoded dependencies | Use dependency injection |
| No interfaces/abstractions | Program to interfaces, not implementations |
| Inheritance over composition | Prefer composition for flexibility |
| Ignoring thread safety | Mention locks/atomic ops for shared state |
| Over-engineering | Start simple, add patterns only when needed |

---

## Interview Tips

1. **Start with entities** - list all nouns from the problem
2. **Draw the class diagram first** - relationships before code
3. **Apply patterns naturally** - don't force them
4. **Mention extensibility** - "If we add X later, we'd just..."
5. **Talk about thread safety** - especially for Singleton, shared state
6. **Keep it simple** - interviewers want clean code, not clever code

---

## Related Resources

- LLD section: [Overview](lld-overview.md) · [Roadmap](roadmap.md) · [Concurrency](concurrency.md)
  · [Extended Patterns](patterns-extended.md) · [Worked Problems](worked-problems.md)
  · [Java Cheat Sheet](java-cheatsheet.md) · [Mental Models](lld-mental-models.md)
- [System Design Guide](../SystemDesign/SystemDesignGuide.md)
- [API Design Patterns](../SystemDesign/APIDesignPatterns.md)
