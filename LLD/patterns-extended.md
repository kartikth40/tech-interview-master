---
title: Design Patterns - Extended
description: Mid-level design patterns beyond the common eight - Command, Chain of Responsibility, Template Method, Facade, Proxy, Composite, Null Object - with trade-offs, "when NOT to use" guidance, and a pattern-selection cheat sheet.
---

# Design Patterns - Extended

The [Roadmap](roadmap.md#6-design-patterns) covers the common eight (Singleton, Factory, Builder,
Adapter, Decorator, Strategy, Observer, State). This page adds the patterns that show up at
mid-level and - more importantly - the **trade-offs and "when NOT to use"** judgement
interviewers probe. For compact runnable examples of the common patterns, see the
[Low-Level Design Guide](LowLevelDesign.md).

!!! note "Language"
    Examples in **Java** - the language most LLD rounds expect ([Java Cheat Sheet](java-cheatsheet.md)).

## The meta-skill: justify, don't name-drop

At SDE-2 the pattern itself is table stakes. What distinguishes you:

- **Recognize the need** before naming the pattern ("these are interchangeable algorithms →
  Strategy", not "let me apply Strategy").
- **State the trade-off**: every pattern adds indirection = more classes = harder to read.
  Patterns pay for flexibility you actually need; don't pre-pay.
- **Know the alternative**: Strategy vs a simple `if/else`; Builder vs a dataclass with
  defaults; Observer vs a direct call. Picking the simpler one *with reasoning* scores higher
  than forcing a pattern.

> Red flag: "I'll use the Factory pattern" with no reason. Green flag: "Creation varies by
> input and I want callers decoupled from concrete classes, so a Factory earns its place."

---

## Command - encapsulate a request as an object

**Use for:** undo/redo, queuing requests, logging/replaying operations, macro commands.
Each action becomes an object with `execute()` (and often `undo()`).

```java
interface Command {
    void execute();
    void undo();
}

class AddTextCommand implements Command {
    private final List<String> doc;
    private final String text;
    AddTextCommand(List<String> doc, String text) { this.doc = doc; this.text = text; }
    public void execute() { doc.add(text); }
    public void undo()    { doc.remove(doc.size() - 1); }
}

class Editor {                        // invoker - keeps history, doesn't know command internals
    private final Deque<Command> history = new ArrayDeque<>();
    void run(Command cmd) {
        cmd.execute();
        history.push(cmd);
    }
    void undo() {
        if (!history.isEmpty()) history.pop().undo();
    }
}
```

- Decouples the **invoker** (who triggers) from the **receiver** (who does the work).
- **Don't use** if there's no undo/queue/log need - it's just an extra indirection otherwise.

---

## Chain of Responsibility - pass a request along a chain

**Use for:** middleware pipelines, approval chains, validation chains, event filters,
logging levels. Each handler either handles the request or passes it on.

```java
abstract class Handler {
    protected Handler next;
    Handler setNext(Handler h) {
        this.next = h;
        return h;                      // enables fluent chaining
    }
    abstract String handle(Request req);

    protected String passOn(Request req) {
        return next != null ? next.handle(req) : "OK";
    }
}

class AuthHandler extends Handler {
    String handle(Request req) {
        if (req.token == null) return "401 Unauthorized";
        return passOn(req);
    }
}

class RateLimitHandler extends Handler {
    String handle(Request req) {
        if (req.count > 100) return "429 Too Many Requests";
        return passOn(req);
    }
}

// wire the chain
Handler auth = new AuthHandler();
auth.setNext(new RateLimitHandler());
System.out.println(auth.handle(new Request("x", 5)));   // OK
```

- Each handler has one responsibility (SRP); add/remove/reorder handlers freely (OCP).
- **Don't use** for a fixed 2-step check - a chain is overkill.

Real LLD uses: expense approval (manager → director → VP by amount), request middleware,
money-dispensing in an ATM (dispense ₹2000 notes → ₹500 → ₹100).

---

## Template Method - fix the skeleton, vary the steps

**Use for:** algorithms with a fixed sequence but variable steps (data parsers, report
generators, game turns). Base class defines the order; subclasses fill in steps.

```java
abstract class DataExporter {
    final void export(List<String> data) {  // template method - fixed skeleton, final = DON'T override
        open();
        writeHeader();
        writeRows(data);               // varies
        close();
    }
    void open()  { System.out.println("open file"); }
    void close() { System.out.println("close file"); }
    abstract void writeHeader();
    abstract void writeRows(List<String> data);
}

class CsvExporter extends DataExporter {
    void writeHeader()                 { System.out.println("id,name"); }
    void writeRows(List<String> data)  { System.out.println(String.join("\n", data)); }
}
```

- Strategy vs Template Method: Strategy varies an algorithm via **composition** (inject an
  object); Template Method varies steps via **inheritance** (override methods). Prefer
  Strategy when you want runtime swapping; Template Method when the skeleton is truly fixed.

---

## Facade - one simple front for a complex subsystem

**Use for:** hiding a messy set of subsystems behind one clean entry point (e.g. an
`OrderFacade` that coordinates inventory + payment + shipping + notification).

```java
class OrderFacade {
    private final Inventory inv;
    private final Payment pay;
    private final Shipping ship;
    private final Notifier notify;
    OrderFacade(Inventory inv, Payment pay, Shipping ship, Notifier notify) {
        this.inv = inv; this.pay = pay; this.ship = ship; this.notify = notify;
    }
    void placeOrder(User user, Item item) {     // client calls ONE method
        inv.reserve(item);
        pay.charge(user, item.price);
        ship.schedule(user, item);
        notify.send(user, "order placed");
    }
}
```

- Simplifies the client's view; doesn't *restrict* access to subsystems (unlike encapsulation).
- **Don't confuse with Adapter**: Adapter changes an interface to match an expectation; Facade
  simplifies *many* interfaces into one.

---

## Proxy - stand-in that controls access

**Use for:** lazy loading (virtual proxy), access control (protection proxy), caching,
logging, remote calls. Same interface as the real object; adds a layer around it.

```java
interface Image {
    void display();
}

class RealImage implements Image {    // expensive to create
    private final String path;
    RealImage(String path) {
        this.path = path;
        load();                       // heavy disk load
    }
    private void load() { System.out.println("loading " + path); }
    public void display() { System.out.println("showing " + path); }
}

class ImageProxy implements Image {   // defers creation until actually needed
    private final String path;
    private RealImage real;
    ImageProxy(String path) { this.path = path; }
    public void display() {
        if (real == null) {           // lazy load on first use
            real = new RealImage(path);
        }
        real.display();
    }
}
```

- Proxy vs Decorator: both wrap and share the interface. **Decorator adds behavior**; **Proxy
  controls access** (may not even create the real object).

---

## Composite - treat individual objects and groups uniformly

**Use for:** tree structures where a leaf and a container should be used the same way - file
systems, UI components, org charts, menu + submenus.

```java
interface FileSystemNode {
    int size();
}

class File implements FileSystemNode {    // leaf
    private final int size;
    File(int size) { this.size = size; }
    public int size() { return size; }
}

class Directory implements FileSystemNode {  // composite
    private final List<FileSystemNode> children = new ArrayList<>();
    void add(FileSystemNode node) { children.add(node); }
    public int size() {
        int total = 0;
        for (FileSystemNode c : children) total += c.size();  // recurse uniformly
        return total;
    }
}

Directory root = new Directory();
root.add(new File(100));
Directory sub = new Directory();
sub.add(new File(50));
root.add(sub);
System.out.println(root.size());      // 150 - same size() call on file or dir
```

---

## Null Object - a do-nothing default instead of `None`/`null`

**Use for:** avoiding null checks everywhere. Provide a neutral implementation.

```java
interface Logger {
    void log(String msg);
}

class ConsoleLogger implements Logger {
    public void log(String msg) { System.out.println(msg); }
}

class NullLogger implements Logger {  // does nothing - no caller null-checks needed
    public void log(String msg) { }
}

void service(Logger logger) {         // pass NullLogger when "no logger" was wanted
    logger.log("started");            // safe - no null check needed
}
```

- Removes scattered `if logger is not None` checks. **Don't use** if "absent" must be
  distinguishable from "present but no-op".

---

## Pattern selection cheat sheet

| You see... | Reach for | Not if... |
|---|---|---|
| Interchangeable algorithms chosen at runtime | **Strategy** | there are only 2 fixed cases → just `if/else` |
| Create one of several subtypes by input | **Factory** | only one concrete type exists |
| Object with many optional fields | **Builder** | a dataclass + defaults suffices (esp. Python) |
| Exactly one shared instance | **Singleton** | you can pass the object in (DI) instead |
| Add stackable behavior at runtime | **Decorator** | behavior is fixed → subclass or compose |
| Incompatible third-party interface | **Adapter** | you control both sides → just align them |
| One change notifies many | **Observer** | one fixed listener → direct call |
| Behavior differs per internal state | **State** | 2 states → a boolean + `if` is fine |
| Undo / queue / log operations | **Command** | no undo/queue need |
| Sequential handlers, each may handle/pass | **Chain of Responsibility** | fixed 2-step check |
| Fixed skeleton, variable steps | **Template Method** | you want runtime swapping → Strategy |
| Simplify a complex subsystem | **Facade** | there's only one subsystem already |
| Control access / lazy-load / cache | **Proxy** | you want to *add behavior* → Decorator |
| Tree of leaves + containers | **Composite** | structure is flat |
| Avoid null checks | **Null Object** | absence must be detectable |

> Keep the judgement front-and-center: **the simplest design that meets the requirements and
> stays open to the changes you actually expect.** A pattern you can justify beats three you
> forced in.

## Related

- The common eight + per-pattern trade-offs → [Roadmap → Design Patterns](roadmap.md#6-design-patterns)
- Compact runnable examples → [Low-Level Design Guide](LowLevelDesign.md)
- "Which pattern?" decision tree → [LLD Mental Models](lld-mental-models.md)
- Patterns applied in full solutions → [Worked Problems](worked-problems.md)
