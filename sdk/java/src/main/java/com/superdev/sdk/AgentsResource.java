package com.superdev.sdk;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.Agent;
import java.util.Map;
public class AgentsResource {
    private final SuperDevClient client;
    AgentsResource(SuperDevClient c) { this.client = c; }
    public Agent get(String id) throws SuperDevException { return client.deserialize(client.request("GET", "/api/v1/agents/" + id, null), Agent.class); }
    public Agent start(String id) throws SuperDevException { return client.deserialize(client.request("POST", "/api/v1/agents/" + id + "/start", Map.of()), Agent.class); }
    public Agent stop(String id) throws SuperDevException { return client.deserialize(client.request("POST", "/api/v1/agents/" + id + "/stop", Map.of()), Agent.class); }
}
