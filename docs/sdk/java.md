# Java SDK

## Requirements

- Java 17+
- Maven 3.8+

## Installation

```xml
<dependency>
    <groupId>com.superdev</groupId>
    <artifactId>superdev-sdk</artifactId>
    <version>0.1.0</version>
</dependency>
```

## Usage

```java
SuperDevClient client = SuperDevClient.builder()
    .baseUrl("http://localhost:8000")
    .apiKey("sk-...")
    .build();

User me = client.users().me();
Project p = client.projects().get("proj_123");
ChatResponse resp = client.chat().send("Hello!", null);
```
