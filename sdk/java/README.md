# SuperDev Java SDK

The official Java SDK for the SuperDev platform. This library provides a convenient way to interact with the SuperDev API from Java applications.

## Features

- **Builder Pattern Client**: Easy to configure and initialize.
- **Immutable Types**: Thread-safe and predictable data objects.
- **Comprehensive API Coverage**: Access Users, Projects, Agents, Workflows, Providers, Plugins, Chat, and Deployments.
- **Streaming Support**: (Planned) Support for streaming responses.
- **Error Handling**: Strongly typed exceptions for common HTTP errors.

## Requirements

- Java 17 or higher
- Maven

## Installation

Add the following dependency to your `pom.xml`:

```xml
<dependency>
    <groupId>com.superdev</groupId>
    <artifactId>sdk</artifactId>
    <version>1.0.0-SNAPSHOT</version>
</dependency>
```

## Usage

### Initialization

```java
import com.superdev.sdk.SuperDevClient;

SuperDevClient client = SuperDevClient.builder()
    .apiKey("your-api-key-here")
    .baseUrl("https://api.superdev.com/v1") // Optional, default is provided
    .build();
```

### Users

```java
import com.superdev.sdk.types.User;
import com.superdev.sdk.types.PaginatedResponse;

// Get a single user
User user = client.getUser("user-123");
System.out.println(user.getName());

// List users with pagination
PaginatedResponse<User> users = client.listUsers(1, 10);
for (User u : users.getItems()) {
    System.out.println(u.getEmail());
}
```

### Agents & Chat

```java
import com.superdev.sdk.types.Agent;
import com.superdev.sdk.types.ChatResponse;

// List agents
Agent agent = client.listAgents(1, 1).getItems().get(0);

// Send a chat message
ChatResponse response = client.chat(agent.getId(), "Hello, how can you help me?");
System.out.println(response.getContent());
```

### Workflows

```java
import com.superdev.sdk.types.Workflow;
import com.superdev.sdk.types.WorkflowRun;

Workflow workflow = client.getWorkflow("workflow-abc");

// Run a workflow
WorkflowRun run = client.runWorkflow(workflow.getId(), "{\"prompt\": \"Analyze this code\"}");
System.out.println("Run started: " + run.getId());

// Check run status
WorkflowRun status = client.getWorkflowRun(run.getId());
System.out.println("Status: " + status.getStatus());
```

## Error Handling

The SDK throws specific exceptions for different error scenarios:

```java
import com.superdev.sdk.exceptions.AuthenticationException;
import com.superdev.sdk.exceptions.NotFoundException;
import com.superdev.sdk.exceptions.SuperDevException;

try {
    client.getUser("non-existent-id");
} catch (NotFoundException e) {
    System.err.println("User not found: " + e.getMessage());
} catch (AuthenticationException e) {
    System.err.println("Auth failed: " + e.getMessage());
} catch (SuperDevException e) {
    System.err.println("General error: " + e.getMessage());
}
```

## License

MIT License
