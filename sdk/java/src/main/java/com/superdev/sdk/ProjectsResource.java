package com.superdev.sdk;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.Project;
import java.util.Map;
public class ProjectsResource {
    private final SuperDevClient client;
    ProjectsResource(SuperDevClient c) { this.client = c; }
    public Project get(String id) throws SuperDevException { return client.deserialize(client.request("GET", "/api/v1/projects/" + id, null), Project.class); }
    public Project create(String name, String desc) throws SuperDevException { return client.deserialize(client.request("POST", "/api/v1/projects", Map.of("name", name, "description", desc)), Project.class); }
    public void delete(String id) throws SuperDevException { client.request("DELETE", "/api/v1/projects/" + id, null); }
}
