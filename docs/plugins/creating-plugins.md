# Creating Plugins

## Step 1: Scaffold

```bash
superdev plugin create my-plugin
```

## Step 2: Implement

Edit `src/index.ts`:

```typescript
import { PluginContext } from "@superdev/plugin-sdk";

export function activate(ctx: PluginContext) {
  // Register commands
  ctx.commands.register("hello", () => {
    ctx.window.showInformationMessage("Hello from my plugin!");
  });

  // Register event listeners
  ctx.events.on("project:opened", (project) => {
    console.log(`Project opened: ${project.name}`);
  });
}

export function deactivate() {
  // Cleanup
}
```

## Step 3: Test

```bash
superdev plugin test my-plugin
```

## Step 4: Package

```bash
superdev plugin package my-plugin
```

## Step 5: Publish

```bash
superdev plugin publish my-plugin
```
