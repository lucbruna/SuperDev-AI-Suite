# SuperDev Plugins

Plugins extend SuperDev with custom functionality.

## Quick Start

See [creating-plugins.md](creating-plugins.md) for a step-by-step guide.

## Plugin Structure

```
my-plugin/
  manifest.json      # Plugin metadata
  src/
    index.ts         # Plugin entry point
  README.md
```

## manifest.json

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My awesome plugin",
  "author": "Your Name",
  "main": "src/index.ts",
  "permissions": ["filesystem:read", "network:outbound"]
}
```

## Documentation

- [Creating Plugins](creating-plugins.md)
- [Plugin API](plugin-api.md)
- [Sandboxing](sandbox.md)
- [Permissions](permissions.md)
- [Publishing](publishing.md)
- [Examples](examples.md)
