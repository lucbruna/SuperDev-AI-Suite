package com.superdev.sdk;
import com.superdev.sdk.exceptions.SuperDevException;
import com.superdev.sdk.types.User;
public class UsersResource {
    private final SuperDevClient client;
    UsersResource(SuperDevClient c) { this.client = c; }
    public User me() throws SuperDevException { return client.deserialize(client.request("GET", "/api/v1/users/me", null), User.class); }
}
