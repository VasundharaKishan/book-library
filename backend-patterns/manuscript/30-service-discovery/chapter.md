# Chapter 30: Service Discovery -- Finding Services in Dynamic Environments

## What You Will Learn

- What Service Discovery is and why static configuration breaks at scale
- The difference between client-side and server-side discovery
- How Eureka, Consul, and similar registries work
- How Kubernetes handles service discovery natively
- How auto-scaling and dynamic environments depend on discovery
- Practical implementations in Java and Python

## Why This Chapter Matters

In the previous chapter, the API Gateway routed requests to backend services. But we
hardcoded the service URLs: `http://users.internal:8001`. In production, services are
not at fixed addresses. They run in containers that start and stop. Auto-scaling adds
new instances when traffic spikes and removes them when traffic drops. Deployments
replace old instances with new ones.

If your gateway has a hardcoded list of service addresses, it breaks every time an
instance moves, scales, or restarts. Service Discovery solves this by providing a
dynamic registry where services register themselves and clients look them up.

---

## The Problem

You have 5 microservices, each running 3 instances for reliability. That is 15
addresses to track.

```
WITHOUT SERVICE DISCOVERY:

application.yml:
  user-service:
    - http://10.0.1.10:8001
    - http://10.0.1.11:8001
    - http://10.0.1.12:8001
  order-service:
    - http://10.0.2.20:8002
    - http://10.0.2.21:8002
    - http://10.0.2.22:8002
  product-service:
    - http://10.0.3.30:8003
    - ...

Problems:
- Auto-scaling adds instance at 10.0.1.13 -- config is stale
- Instance 10.0.1.10 crashes -- requests still route there
- Deploy moves service to new IP -- manual config update
- 50 services x 5 instances = 250 addresses to maintain
```

Every change requires a configuration update and often a restart. This does not work
in dynamic environments.

---

## The Solution: Service Discovery

```
WITH SERVICE DISCOVERY:

+----------------+                    +-----------------+
| Service A      |--- register ------>|   Service       |
| (startup)      |    name: "users"   |   Registry      |
|                |    host: 10.0.1.10 |                 |
|                |    port: 8001      | users:          |
+----------------+                    |   - 10.0.1.10   |
                                      |   - 10.0.1.11   |
+----------------+                    |   - 10.0.1.12   |
| Service B      |--- lookup -------->|                 |
| (needs users)  |    name: "users"   | orders:         |
|                |<-- [10.0.1.10,     |   - 10.0.2.20   |
|                |     10.0.1.11,     |   - 10.0.2.21   |
|                |     10.0.1.12] ----|                 |
+----------------+                    +-----------------+

On crash:
  10.0.1.10 stops sending heartbeat
  Registry removes it after timeout
  Clients get updated list: [10.0.1.11, 10.0.1.12]

On scale-up:
  10.0.1.13 starts and registers
  Clients get updated list: [10.0.1.11, 10.0.1.12, 10.0.1.13]
```

**Key concepts:**

- **Service Registration**: When a service starts, it registers its name, address, and
  port with the registry
- **Health Checks**: Services send periodic heartbeats. If a service stops responding,
  the registry removes it
- **Service Lookup**: Clients query the registry by service name to get available
  instances
- **Load Balancing**: Clients choose among multiple instances (round-robin, random,
  least connections)

---

## Client-Side vs Server-Side Discovery

### Client-Side Discovery

The client queries the registry directly and chooses which instance to call.

```
+--------+    1. lookup("orders")    +----------+
| Client |---------------------------->| Registry |
|        |<---[inst1, inst2, inst3]---|          |
+--------+                           +----------+
    |
    | 2. client picks inst2 (load balancing)
    v
+---------+
| inst2   |
| (orders)|
+---------+
```

**How it works:**
1. Client asks registry: "Where is the order service?"
2. Registry returns: [instance1, instance2, instance3]
3. Client picks one (round-robin, random, etc.)
4. Client calls the chosen instance directly

**Examples:** Netflix Eureka, client-side load balancing

**Pros:** No extra network hop, client controls load balancing strategy
**Cons:** Client must implement discovery logic, tightly couples client to registry

### Server-Side Discovery

The client calls a load balancer or router that handles discovery internally.

```
+--------+    1. call /api/orders    +----------+    2. lookup    +----------+
| Client |--------------------------->|   Load   |--------------->| Registry |
|        |                           | Balancer |<--[inst1,2,3]--|          |
+--------+                           +----------+                +----------+
                                          |
                                          | 3. forward to inst2
                                          v
                                     +---------+
                                     | inst2   |
                                     | (orders)|
                                     +---------+
```

**How it works:**
1. Client calls a well-known load balancer address
2. Load balancer queries registry for available instances
3. Load balancer picks an instance and forwards the request

**Examples:** AWS ALB, Kubernetes Services, Nginx

**Pros:** Client is simple (just knows one URL), discovery logic is centralized
**Cons:** Extra network hop, load balancer is a potential bottleneck

```
+---------------------+---------------------------+---------------------------+
| Aspect              | Client-Side               | Server-Side               |
+---------------------+---------------------------+---------------------------+
| Discovery logic     | In each client            | In load balancer/proxy    |
| Network hops        | Client -> Service         | Client -> LB -> Service   |
| Client complexity   | High (discovery + LB)     | Low (just call one URL)   |
| Language support    | Need library per language | Language agnostic         |
| Example             | Eureka + Ribbon           | Kubernetes Service        |
+---------------------+---------------------------+---------------------------+
```

---

## Java Implementation: Service Registry

### The Registry Core

```java
import java.util.*;
import java.util.concurrent.*;

public class ServiceInstance {
    private final String serviceId;
    private final String instanceId;
    private final String host;
    private final int port;
    private final Map<String, String> metadata;
    private long lastHeartbeat;
    private InstanceStatus status;

    public enum InstanceStatus {
        UP, DOWN, STARTING, OUT_OF_SERVICE
    }

    public ServiceInstance(String serviceId, String host, int port) {
        this.serviceId = serviceId;
        this.instanceId = serviceId + "-" + host + ":" + port;
        this.host = host;
        this.port = port;
        this.metadata = new HashMap<>();
        this.lastHeartbeat = System.currentTimeMillis();
        this.status = InstanceStatus.STARTING;
    }

    public void heartbeat() {
        this.lastHeartbeat = System.currentTimeMillis();
        this.status = InstanceStatus.UP;
    }

    public boolean isExpired(long timeoutMs) {
        return System.currentTimeMillis() - lastHeartbeat > timeoutMs;
    }

    public String getUrl() {
        return String.format("http://%s:%d", host, port);
    }

    // Getters
    public String getServiceId() { return serviceId; }
    public String getInstanceId() { return instanceId; }
    public String getHost() { return host; }
    public int getPort() { return port; }
    public InstanceStatus getStatus() { return status; }
    public void setStatus(InstanceStatus s) { this.status = s; }

    @Override
    public String toString() {
        return String.format("%s [%s] %s", instanceId, status, getUrl());
    }
}
```

```java
public class ServiceRegistry {
    private final ConcurrentHashMap<String, List<ServiceInstance>> services;
    private final long heartbeatTimeoutMs;
    private final ScheduledExecutorService cleaner;

    public ServiceRegistry(long heartbeatTimeoutMs) {
        this.services = new ConcurrentHashMap<>();
        this.heartbeatTimeoutMs = heartbeatTimeoutMs;

        // Background thread to evict expired instances
        this.cleaner = Executors.newSingleThreadScheduledExecutor();
        this.cleaner.scheduleAtFixedRate(
            this::evictExpired, 5, 5, TimeUnit.SECONDS);
    }

    public ServiceInstance register(String serviceId, String host,
                                     int port) {
        ServiceInstance instance = new ServiceInstance(
                serviceId, host, port);
        instance.heartbeat();

        services.computeIfAbsent(serviceId, k -> new CopyOnWriteArrayList<>())
                .add(instance);

        System.out.printf("[Registry] Registered: %s%n", instance);
        return instance;
    }

    public void deregister(String instanceId) {
        services.values().forEach(instances ->
            instances.removeIf(i -> {
                if (i.getInstanceId().equals(instanceId)) {
                    System.out.printf("[Registry] Deregistered: %s%n",
                            instanceId);
                    return true;
                }
                return false;
            })
        );
    }

    public void heartbeat(String instanceId) {
        services.values().forEach(instances ->
            instances.stream()
                .filter(i -> i.getInstanceId().equals(instanceId))
                .forEach(ServiceInstance::heartbeat)
        );
    }

    public List<ServiceInstance> getInstances(String serviceId) {
        List<ServiceInstance> instances = services.getOrDefault(
                serviceId, Collections.emptyList());

        return instances.stream()
                .filter(i -> i.getStatus() ==
                        ServiceInstance.InstanceStatus.UP)
                .toList();
    }

    public Map<String, List<ServiceInstance>> getAllServices() {
        return Collections.unmodifiableMap(services);
    }

    private void evictExpired() {
        services.values().forEach(instances ->
            instances.removeIf(i -> {
                if (i.isExpired(heartbeatTimeoutMs)) {
                    System.out.printf("[Registry] Evicted (no heartbeat): "
                            + "%s%n", i.getInstanceId());
                    return true;
                }
                return false;
            })
        );
    }

    public void shutdown() {
        cleaner.shutdown();
    }

    public void printStatus() {
        System.out.println("\n=== Registry Status ===");
        if (services.isEmpty()) {
            System.out.println("  (empty)");
            return;
        }
        services.forEach((serviceId, instances) -> {
            System.out.printf("  %s: %d instance(s)%n",
                    serviceId, instances.size());
            instances.forEach(i -> System.out.printf("    %s%n", i));
        });
    }
}
```

### Client-Side Load Balancer

```java
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class LoadBalancer {
    public enum Strategy {
        ROUND_ROBIN, RANDOM
    }

    private final ServiceRegistry registry;
    private final Strategy strategy;
    private final AtomicInteger counter = new AtomicInteger(0);

    public LoadBalancer(ServiceRegistry registry, Strategy strategy) {
        this.registry = registry;
        this.strategy = strategy;
    }

    public ServiceInstance choose(String serviceId) {
        List<ServiceInstance> instances = registry.getInstances(serviceId);

        if (instances.isEmpty()) {
            throw new RuntimeException(
                "No instances available for: " + serviceId);
        }

        ServiceInstance chosen;
        switch (strategy) {
            case ROUND_ROBIN:
                int idx = counter.getAndIncrement() % instances.size();
                chosen = instances.get(idx);
                break;
            case RANDOM:
                chosen = instances.get(
                    (int) (Math.random() * instances.size()));
                break;
            default:
                chosen = instances.get(0);
        }

        System.out.printf("[LB] %s -> %s (from %d instances)%n",
                serviceId, chosen.getUrl(), instances.size());
        return chosen;
    }
}
```

### Discovery-Aware Service Client

```java
public class DiscoveryClient {
    private final LoadBalancer loadBalancer;

    public DiscoveryClient(LoadBalancer loadBalancer) {
        this.loadBalancer = loadBalancer;
    }

    public String call(String serviceId, String path) {
        ServiceInstance instance = loadBalancer.choose(serviceId);
        String url = instance.getUrl() + path;

        // Simulate HTTP call
        System.out.printf("[Client] Calling: %s%n", url);
        return String.format("Response from %s at %s",
                serviceId, instance.getUrl());
    }
}
```

### Demo

```java
public class DiscoveryDemo {
    public static void main(String[] args) throws InterruptedException {
        ServiceRegistry registry = new ServiceRegistry(10_000);

        // Services register at startup
        System.out.println("=== Service Registration ===");
        ServiceInstance user1 = registry.register(
                "user-service", "10.0.1.10", 8001);
        ServiceInstance user2 = registry.register(
                "user-service", "10.0.1.11", 8001);
        ServiceInstance user3 = registry.register(
                "user-service", "10.0.1.12", 8001);

        ServiceInstance order1 = registry.register(
                "order-service", "10.0.2.20", 8002);
        ServiceInstance order2 = registry.register(
                "order-service", "10.0.2.21", 8002);

        registry.printStatus();

        // Client-side discovery with load balancing
        LoadBalancer lb = new LoadBalancer(
                registry, LoadBalancer.Strategy.ROUND_ROBIN);
        DiscoveryClient client = new DiscoveryClient(lb);

        System.out.println("\n=== Client Calls (Round Robin) ===");
        for (int i = 0; i < 6; i++) {
            String response = client.call("user-service", "/api/users/1");
            System.out.println("  " + response);
        }

        // Simulate instance failure (no more heartbeats)
        System.out.println("\n=== Simulating Instance Failure ===");
        System.out.println("Instance user1 stops sending heartbeats...");
        user1.setStatus(ServiceInstance.InstanceStatus.DOWN);

        // Now calls only go to healthy instances
        System.out.println("\n=== Calls After Failure ===");
        for (int i = 0; i < 4; i++) {
            client.call("user-service", "/api/users/1");
        }

        // Simulate scale-up
        System.out.println("\n=== Auto-Scale: Adding Instance ===");
        registry.register("user-service", "10.0.1.13", 8001);

        registry.printStatus();

        // Graceful deregister
        System.out.println("\n=== Graceful Shutdown ===");
        registry.deregister(user2.getInstanceId());
        registry.printStatus();

        registry.shutdown();
    }
}
```

**Output:**
```
=== Service Registration ===
[Registry] Registered: user-service-10.0.1.10:8001 [UP] http://10.0.1.10:8001
[Registry] Registered: user-service-10.0.1.11:8001 [UP] http://10.0.1.11:8001
[Registry] Registered: user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
[Registry] Registered: order-service-10.0.2.20:8002 [UP] http://10.0.2.20:8002
[Registry] Registered: order-service-10.0.2.21:8002 [UP] http://10.0.2.21:8002

=== Registry Status ===
  user-service: 3 instance(s)
    user-service-10.0.1.10:8001 [UP] http://10.0.1.10:8001
    user-service-10.0.1.11:8001 [UP] http://10.0.1.11:8001
    user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
  order-service: 2 instance(s)
    order-service-10.0.2.20:8002 [UP] http://10.0.2.20:8002
    order-service-10.0.2.21:8002 [UP] http://10.0.2.21:8002

=== Client Calls (Round Robin) ===
[LB] user-service -> http://10.0.1.10:8001 (from 3 instances)
[Client] Calling: http://10.0.1.10:8001/api/users/1
  Response from user-service at http://10.0.1.10:8001
[LB] user-service -> http://10.0.1.11:8001 (from 3 instances)
[Client] Calling: http://10.0.1.11:8001/api/users/1
  Response from user-service at http://10.0.1.11:8001
[LB] user-service -> http://10.0.1.12:8001 (from 3 instances)
[Client] Calling: http://10.0.1.12:8001/api/users/1
  Response from user-service at http://10.0.1.12:8001
[LB] user-service -> http://10.0.1.10:8001 (from 3 instances)
...

=== Simulating Instance Failure ===
Instance user1 stops sending heartbeats...

=== Calls After Failure ===
[LB] user-service -> http://10.0.1.11:8001 (from 2 instances)
[Client] Calling: http://10.0.1.11:8001/api/users/1
[LB] user-service -> http://10.0.1.12:8001 (from 2 instances)
[Client] Calling: http://10.0.1.12:8001/api/users/1
...

=== Auto-Scale: Adding Instance ===
[Registry] Registered: user-service-10.0.1.13:8001 [UP] http://10.0.1.13:8001

=== Registry Status ===
  user-service: 4 instance(s)
    user-service-10.0.1.10:8001 [DOWN] http://10.0.1.10:8001
    user-service-10.0.1.11:8001 [UP] http://10.0.1.11:8001
    user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
    user-service-10.0.1.13:8001 [UP] http://10.0.1.13:8001
  order-service: 2 instance(s)
    ...

=== Graceful Shutdown ===
[Registry] Deregistered: user-service-10.0.1.11:8001

=== Registry Status ===
  user-service: 3 instance(s)
    user-service-10.0.1.10:8001 [DOWN] http://10.0.1.10:8001
    user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
    user-service-10.0.1.13:8001 [UP] http://10.0.1.13:8001
  order-service: 2 instance(s)
    ...
```

---

## Python Implementation: Service Discovery with Health Checks

```python
import time
import random
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class InstanceStatus(Enum):
    UP = "UP"
    DOWN = "DOWN"
    STARTING = "STARTING"


@dataclass
class ServiceInstance:
    service_id: str
    host: str
    port: int
    status: InstanceStatus = InstanceStatus.UP
    metadata: Dict[str, str] = field(default_factory=dict)
    last_heartbeat: float = field(default_factory=time.time)
    registered_at: float = field(default_factory=time.time)

    @property
    def instance_id(self):
        return f"{self.service_id}-{self.host}:{self.port}"

    @property
    def url(self):
        return f"http://{self.host}:{self.port}"

    def heartbeat(self):
        self.last_heartbeat = time.time()
        self.status = InstanceStatus.UP

    def is_expired(self, timeout_seconds):
        return time.time() - self.last_heartbeat > timeout_seconds

    def __repr__(self):
        return f"{self.instance_id} [{self.status.value}] {self.url}"


class ServiceRegistry:
    """Central service registry with health checking."""

    def __init__(self, heartbeat_timeout=30):
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._heartbeat_timeout = heartbeat_timeout
        self._lock = threading.Lock()

    def register(self, service_id, host, port, **metadata):
        instance = ServiceInstance(
            service_id=service_id,
            host=host,
            port=port,
            metadata=metadata
        )

        with self._lock:
            if service_id not in self._services:
                self._services[service_id] = []
            self._services[service_id].append(instance)

        print(f"[Registry] Registered: {instance}")
        return instance

    def deregister(self, instance_id):
        with self._lock:
            for instances in self._services.values():
                before = len(instances)
                instances[:] = [i for i in instances
                               if i.instance_id != instance_id]
                if len(instances) < before:
                    print(f"[Registry] Deregistered: {instance_id}")
                    return True
        return False

    def heartbeat(self, instance_id):
        with self._lock:
            for instances in self._services.values():
                for inst in instances:
                    if inst.instance_id == instance_id:
                        inst.heartbeat()
                        return True
        return False

    def get_instances(self, service_id):
        with self._lock:
            instances = self._services.get(service_id, [])
            return [i for i in instances
                    if i.status == InstanceStatus.UP]

    def get_all_services(self):
        with self._lock:
            return {
                sid: list(instances)
                for sid, instances in self._services.items()
            }

    def evict_expired(self):
        with self._lock:
            for sid, instances in self._services.items():
                expired = [i for i in instances
                          if i.is_expired(self._heartbeat_timeout)]
                for inst in expired:
                    inst.status = InstanceStatus.DOWN
                    print(f"[Registry] Expired: {inst.instance_id}")

    def print_status(self):
        print("\n--- Registry Status ---")
        for sid, instances in self._services.items():
            up_count = sum(1 for i in instances
                          if i.status == InstanceStatus.UP)
            print(f"  {sid}: {up_count}/{len(instances)} UP")
            for inst in instances:
                print(f"    {inst}")
        print()


class LoadBalancer:
    """Client-side load balancer."""

    def __init__(self, registry, strategy="round_robin"):
        self.registry = registry
        self.strategy = strategy
        self._counters: Dict[str, int] = {}

    def choose(self, service_id) -> ServiceInstance:
        instances = self.registry.get_instances(service_id)

        if not instances:
            raise RuntimeError(
                f"No healthy instances for: {service_id}")

        if self.strategy == "round_robin":
            idx = self._counters.get(service_id, 0)
            chosen = instances[idx % len(instances)]
            self._counters[service_id] = idx + 1
        elif self.strategy == "random":
            chosen = random.choice(instances)
        else:
            chosen = instances[0]

        return chosen


class ServiceClient:
    """Discovery-aware HTTP client."""

    def __init__(self, registry, strategy="round_robin"):
        self.lb = LoadBalancer(registry, strategy)

    def call(self, service_id, path, method="GET"):
        instance = self.lb.choose(service_id)
        url = f"{instance.url}{path}"
        print(f"[Client] {method} {url}")
        # In production: actual HTTP call here
        return {"url": url, "status": 200, "instance": instance.instance_id}


# --- Demo ---

registry = ServiceRegistry(heartbeat_timeout=30)

# Register service instances
print("=== Registration ===")
u1 = registry.register("user-service", "10.0.1.10", 8001, version="2.1")
u2 = registry.register("user-service", "10.0.1.11", 8001, version="2.1")
u3 = registry.register("user-service", "10.0.1.12", 8001, version="2.1")

o1 = registry.register("order-service", "10.0.2.20", 8002)
o2 = registry.register("order-service", "10.0.2.21", 8002)

p1 = registry.register("product-service", "10.0.3.30", 8003)

registry.print_status()

# Client calls with load balancing
client = ServiceClient(registry)

print("=== Round Robin Calls ===")
for i in range(6):
    result = client.call("user-service", "/api/users/1")
    print(f"  -> {result['instance']}")

# Simulate failure
print("\n=== Simulate Failure ===")
u1.status = InstanceStatus.DOWN
print(f"Instance {u1.instance_id} is DOWN")

print("\nCalls after failure:")
for i in range(4):
    result = client.call("user-service", "/api/users/1")
    print(f"  -> {result['instance']}")

# Scale up
print("\n=== Scale Up ===")
u4 = registry.register("user-service", "10.0.1.13", 8001, version="2.1")

print("\nCalls after scale-up:")
for i in range(4):
    result = client.call("user-service", "/api/users/1")
    print(f"  -> {result['instance']}")

# Graceful shutdown
print("\n=== Graceful Shutdown ===")
registry.deregister(u2.instance_id)
registry.print_status()
```

**Output:**
```
=== Registration ===
[Registry] Registered: user-service-10.0.1.10:8001 [UP] http://10.0.1.10:8001
[Registry] Registered: user-service-10.0.1.11:8001 [UP] http://10.0.1.11:8001
[Registry] Registered: user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
[Registry] Registered: order-service-10.0.2.20:8002 [UP] http://10.0.2.20:8002
[Registry] Registered: order-service-10.0.2.21:8002 [UP] http://10.0.2.21:8002
[Registry] Registered: product-service-10.0.3.30:8003 [UP] http://10.0.3.30:8003

--- Registry Status ---
  user-service: 3/3 UP
    user-service-10.0.1.10:8001 [UP] http://10.0.1.10:8001
    user-service-10.0.1.11:8001 [UP] http://10.0.1.11:8001
    user-service-10.0.1.12:8001 [UP] http://10.0.1.12:8001
  order-service: 2/2 UP
    order-service-10.0.2.20:8002 [UP] http://10.0.2.20:8002
    order-service-10.0.2.21:8002 [UP] http://10.0.2.21:8002
  product-service: 1/1 UP
    product-service-10.0.3.30:8003 [UP] http://10.0.3.30:8003

=== Round Robin Calls ===
[Client] GET http://10.0.1.10:8001/api/users/1
  -> user-service-10.0.1.10:8001
[Client] GET http://10.0.1.11:8001/api/users/1
  -> user-service-10.0.1.11:8001
[Client] GET http://10.0.1.12:8001/api/users/1
  -> user-service-10.0.1.12:8001
[Client] GET http://10.0.1.10:8001/api/users/1
  -> user-service-10.0.1.10:8001
...

=== Simulate Failure ===
Instance user-service-10.0.1.10:8001 is DOWN

Calls after failure:
[Client] GET http://10.0.1.11:8001/api/users/1
  -> user-service-10.0.1.11:8001
[Client] GET http://10.0.1.12:8001/api/users/1
  -> user-service-10.0.1.12:8001
...

=== Scale Up ===
[Registry] Registered: user-service-10.0.1.13:8001 [UP] http://10.0.1.13:8001

Calls after scale-up:
[Client] GET http://10.0.1.11:8001/api/users/1
  -> user-service-10.0.1.11:8001
[Client] GET http://10.0.1.12:8001/api/users/1
  -> user-service-10.0.1.12:8001
[Client] GET http://10.0.1.13:8001/api/users/1
  -> user-service-10.0.1.13:8001
...
```

---

## Kubernetes Service Discovery

Kubernetes has built-in service discovery. No external registry needed.

```
+------------------------------------------+
|            Kubernetes Cluster             |
|                                           |
|  Service: user-service                    |
|  ClusterIP: 10.96.0.1                    |
|  DNS: user-service.default.svc.cluster    |
|       |                                   |
|       +---> Pod 1 (10.244.0.10)          |
|       +---> Pod 2 (10.244.0.11)          |
|       +---> Pod 3 (10.244.0.12)          |
|                                           |
|  Any pod can call:                        |
|    http://user-service:8001/api/users     |
|  Kubernetes routes to a healthy pod.      |
+------------------------------------------+
```

**How Kubernetes discovery works:**

1. You deploy a Service object (YAML manifest)
2. Kubernetes creates a stable DNS name: `user-service.default.svc.cluster.local`
3. Kubernetes maintains a list of healthy Pods behind that DNS name
4. When a Pod starts, it is added; when it fails health checks, it is removed
5. Any Pod in the cluster can call `http://user-service:8001` -- Kubernetes handles
   the rest

```yaml
# Kubernetes Service manifest
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
    - port: 8001
      targetPort: 8001
  type: ClusterIP
```

**Kubernetes vs External Registry:**

```
+-------------------+---------------------------+---------------------------+
| Feature           | Eureka/Consul             | Kubernetes Service        |
+-------------------+---------------------------+---------------------------+
| Setup             | Install and configure     | Built-in, zero setup      |
| Health checks     | Service sends heartbeats  | Kubernetes probes Pods    |
| DNS               | Registry API calls        | Automatic DNS names       |
| Load balancing    | Client-side (need lib)    | Built-in (iptables/IPVS) |
| Works outside K8s | Yes                       | No                        |
| Extra component   | Yes (registry server)     | No                        |
+-------------------+---------------------------+---------------------------+
```

---

## Real-World: Eureka and Consul

### Eureka (Netflix)

Eureka is the most widely used service discovery for Java/Spring applications.

```
How Eureka Works:

1. Service starts -> registers with Eureka Server
2. Service sends heartbeat every 30 seconds
3. Eureka Server removes instance if no heartbeat for 90 seconds
4. Clients fetch registry every 30 seconds (cached locally)
5. If Eureka Server dies, clients use cached registry

Key features:
- Self-preservation mode (does not evict during network partitions)
- Zone-aware load balancing
- Dashboard UI for monitoring
```

### Consul (HashiCorp)

Consul provides service discovery plus health checking, key-value storage, and
service mesh.

```
How Consul Works:

1. Consul Agent runs on every node (as sidecar or daemon)
2. Service registers with local agent
3. Agent performs health checks (HTTP, TCP, script)
4. Agents gossip with each other to share state
5. DNS or HTTP API for lookups

Key features:
- Multi-datacenter support
- Built-in health checking (HTTP, TCP, gRPC, script)
- Key-value store for configuration
- Service mesh with automatic TLS
```

---

## Auto-Scaling and Service Discovery

Service discovery enables auto-scaling by making new instances automatically available.

```
Normal Load:
  user-service: 3 instances

Traffic Spike Detected (CPU > 80%):
  Auto-scaler creates 2 new instances
  New instances register with registry
  Load balancer immediately includes them
  user-service: 5 instances

Traffic Returns to Normal:
  Auto-scaler terminates 2 instances
  Instances deregister (or heartbeat times out)
  Load balancer removes them
  user-service: 3 instances

No configuration changes needed at any step!
```

---

## Before vs After Comparison

### Before: Static Configuration

```yaml
# application.yml -- hardcoded addresses
services:
  user-service: http://10.0.1.10:8001
  order-service: http://10.0.2.20:8002

# When 10.0.1.10 crashes:
#   1. Ops team notices (maybe)
#   2. Update config file
#   3. Restart all dependent services
#   4. Hope nothing else broke
```

### After: Dynamic Discovery

```python
# Service registration at startup
registry.register("user-service", my_host, my_port)

# Client lookup at call time
client.call("user-service", "/api/users/1")

# When an instance crashes:
#   1. Registry detects missing heartbeat (automatic)
#   2. Instance removed from registry (automatic)
#   3. Clients get updated list (automatic)
#   4. No config changes, no restarts
```

---

## When to Use / When NOT to Use

### Use Service Discovery When

- Services have multiple instances (horizontal scaling)
- Instances are ephemeral (containers, cloud VMs)
- Auto-scaling adds/removes instances dynamically
- You have more than 3-4 microservices
- Service locations change across deployments
- You need health-aware routing (skip unhealthy instances)

### Do NOT Use Service Discovery When

- You have a monolithic application (one process, one address)
- Services run on fixed, known infrastructure (bare metal, static VMs)
- You have only 1-2 services with 1 instance each
- A simple load balancer (Nginx, HAProxy) handles your needs
- You are already using Kubernetes (it has built-in discovery)

---

## Common Mistakes

### Mistake 1: Not Handling Registry Unavailability

```python
# WRONG: crash if registry is down
instances = registry.get_instances("user-service")
# If registry is unreachable -> exception -> service fails

# RIGHT: cache last known good instances
try:
    instances = registry.get_instances("user-service")
    self._cache["user-service"] = instances
except RegistryUnavailable:
    instances = self._cache.get("user-service", [])
    if not instances:
        raise
```

### Mistake 2: No Graceful Deregistration

```python
# WRONG: just kill the process
os.exit(1)  # instance disappears without deregistering
# Registry waits 90 seconds before evicting -- 90 seconds of errors!

# RIGHT: deregister before shutdown
import signal

def shutdown_handler(signum, frame):
    registry.deregister(my_instance_id)
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
```

### Mistake 3: Health Check Returns 200 When Unhealthy

```python
# WRONG: always returns healthy
@app.get("/health")
def health():
    return {"status": "UP"}  # even when DB is down!

# RIGHT: check actual dependencies
@app.get("/health")
def health():
    db_ok = check_database_connection()
    cache_ok = check_cache_connection()
    if db_ok and cache_ok:
        return {"status": "UP"}
    return Response(status_code=503,
                    content={"status": "DOWN",
                             "db": db_ok, "cache": cache_ok})
```

---

## Best Practices

1. **Implement graceful shutdown.** When a service stops, deregister from the registry
   before exiting. This prevents routing to dead instances.

2. **Cache the registry locally.** If the registry goes down, clients should use their
   last known good copy. Eureka does this by default.

3. **Use meaningful health checks.** Do not just return 200. Check database connections,
   downstream services, and disk space. Only report healthy when actually ready.

4. **Set appropriate timeouts.** Heartbeat intervals (30s) and eviction timeouts (90s)
   should balance between quick failure detection and false positives.

5. **Use Kubernetes discovery when possible.** If you are running on Kubernetes, its
   built-in service discovery eliminates the need for Eureka or Consul.

6. **Monitor registry health.** The registry itself is a critical component. Monitor
   its availability and set up alerts for anomalies (sudden drops in registered
   instances).

7. **Test failure scenarios.** Regularly test: What happens when an instance crashes?
   When the registry goes down? When a network partition occurs?

---

## Quick Summary

Service Discovery provides a dynamic registry where services register themselves and
clients look them up. It replaces static configuration with automatic, health-aware
routing. Client-side discovery puts the logic in each client; server-side discovery uses
a load balancer. Kubernetes provides built-in discovery. External registries like Eureka
and Consul serve non-Kubernetes environments.

```
Problem:  Service locations change dynamically in cloud/container environments.
Solution: Services register with a central registry; clients look up addresses.
Key:      Health checks automatically remove failed instances.
```

---

## Key Points

- **Service Discovery** replaces static configuration with dynamic service registration
- **Service Registration**: services announce themselves at startup, deregister at
  shutdown
- **Health Checks**: heartbeats detect failed instances and remove them automatically
- **Client-side discovery** (Eureka): client queries registry, picks an instance
- **Server-side discovery** (Kubernetes, AWS ALB): load balancer handles discovery
- **Kubernetes** has built-in discovery via DNS and Services -- no external registry
  needed
- **Eureka** (Netflix) and **Consul** (HashiCorp) are popular external registries
- Cache registry data locally to survive registry outages
- Graceful shutdown (deregister before exit) prevents routing to dead instances

---

## Practice Questions

1. Explain the difference between client-side and server-side service discovery. When
   would you choose each approach?

2. What happens when the service registry itself goes down? How do systems like Eureka
   handle this?

3. A service instance crashes without deregistering. How long before clients stop
   routing to it? What determines this delay?

4. You are migrating from VMs to Kubernetes. How does your service discovery strategy
   change? What can you remove?

5. Your service has a health check endpoint that returns 200 even when its database is
   down. What are the consequences? How would you fix it?

---

## Exercises

### Exercise 1: Service Registry with Health Dashboard

Build a service registry with a dashboard:

- Services register with name, host, port, and version
- Health checker pings services every 10 seconds
- Dashboard displays: service name, instance count (healthy/total), uptime
- Simulate: start 5 instances of 3 services, kill 2, add 3 more
- Print dashboard after each change showing real-time state

### Exercise 2: Multi-Zone Discovery

Implement zone-aware service discovery:

- Each instance registers with a zone (us-east-1a, us-east-1b, us-east-1c)
- Load balancer prefers instances in the same zone as the caller
- If no same-zone instances are healthy, fall back to other zones
- If a zone has fewer than 2 healthy instances, stop preferring it
- Demonstrate zone failover with 3 zones and selective instance failures

### Exercise 3: Service Discovery with API Gateway

Integrate service discovery with the API Gateway from Chapter 29:

- The gateway resolves service URLs dynamically from the registry
- When routing `/api/users/**`, look up "user-service" in the registry
- Use round-robin load balancing across discovered instances
- Handle the case where a backend call fails and retry with the next instance
- Demonstrate: register 3 instances, route requests, kill one instance, show automatic
  failover

---

## What Is Next?

The next chapter ties everything together in a comprehensive project. We build a
complete **E-Commerce Application** applying 15+ patterns from this book, including
Singleton, Factory, Builder, Strategy, Observer, Command, Repository, CQRS, Circuit
Breaker, Saga, API Gateway, and Service Discovery. It is the culmination of everything
you have learned.
