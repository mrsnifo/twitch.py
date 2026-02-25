---
icon: lucide/clock
---

# Loop System

Run your code repeatedly at regular intervals with advanced control features.

## Basic Usage

```python
from twitch.ext.tasks import loop

@loop(seconds=5)  # Every 5 seconds
async def my_task():
    print(f"Execution #{my_task.current_execution}")

my_task.start()
```

## Time Options

```python
@loop(seconds=5.0)      # Every 5 seconds
@loop(minutes=1.0)      # Every minute  
@loop(hours=2.0)        # Every 2 hours
@loop(seconds=1, count=10)  # Run exactly 10 times
```

## Control

```python
# Start/stop
my_task.start()
my_task.stop()

# Pause/resume
my_task.pause()
my_task.resume()

# Status
print(my_task.is_running)
print(my_task.current_execution)

# Skip next run
my_task.skip_next_execution()
```

## Event Callbacks

```python
@my_task.on_error
async def handle_error(error, count):
    print(f"Error: {error}")

@my_task.before_execution
async def before_run(count):
    print(f"About to run #{count}")
```

Perfect for automation without manual triggers!