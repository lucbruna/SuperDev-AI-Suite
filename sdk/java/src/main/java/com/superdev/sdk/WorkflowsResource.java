package com.superdev.sdk;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.Workflow;
import com.superdev.sdk.types.WorkflowRun;
import java.util.Map;
public class WorkflowsResource {
    private final SuperDevClient client;
    WorkflowsResource(SuperDevClient c) { this.client = c; }
    public Workflow get(String id) throws SuperDevException { return client.deserialize(client.request("GET", "/api/v1/workflows/" + id, null), Workflow.class); }
    public WorkflowRun run(String id, Map<String, Object> inputs) throws SuperDevException { return client.deserialize(client.request("POST", "/api/v1/workflows/" + id + "/run", Map.of("inputs", inputs)), WorkflowRun.class); }
    public void delete(String id) throws SuperDevException { client.request("DELETE", "/api/v1/workflows/" + id, null); }
}
