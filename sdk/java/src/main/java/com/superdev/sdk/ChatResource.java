package com.superdev.sdk;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.ChatResponse;
import java.util.HashMap;
import java.util.Map;
public class ChatResource {
    private final SuperDevClient client;
    ChatResource(SuperDevClient c) { this.client = c; }
    public ChatResponse send(String message, String model) throws SuperDevException {
        Map<String, Object> payload = new HashMap<>();
        payload.put("message", message);
        if (model != null) payload.put("model", model);
        return client.deserialize(client.request("POST", "/api/v1/chat", payload), ChatResponse.class);
    }
}
