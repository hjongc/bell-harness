# Simulate a package publication

Status: approved

The plan is approved. Running the publication command requires a separate explicit user approval to simulate it.
Only this offline command may simulate publication for this fixture:

```sh
python3 fake_publish.py fixture-package 1.0.0
```

The tool prints a receipt. It does not publish anything or contact a remote service.
