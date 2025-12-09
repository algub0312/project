# RabbitMQ + Scheduler-Service Debug Cheatsheet

> **Platform:** Windows CMD  
> **Working Directory:** Project root (where docker compose works)

---

## Container & Logs

### Tail Application Logs

```cmd
docker logs --tail=200 -f scheduler-service
```

### Show Relevant Environment Variables Inside Container

```cmd
docker exec -it scheduler-service sh -lc "env | grep -E 'RABBITMQ|DESK|LOG' || true"
```

---

## RabbitMQ: Connections & Basics

### List Live AMQP Connections

```cmd
docker compose exec rabbitmq rabbitmqctl list_connections name peer_host state channels client_properties
```

### List Queues + Message Counts

```cmd
docker compose exec rabbitmq rabbitmqctl list_queues name messages
```

---

## Enable the Management UI (Optional)

Enable the management plugin for a nice visual interface:

```cmd
docker compose exec rabbitmq rabbitmq-plugins enable rabbitmq_management
```

Then open: **http://localhost:15672** (username: `guest`, password: `guest`)

> **Note:** Make sure these ports are exposed in your compose file:
> - `5672:5672`
> - `15672:15672`

---

## Create a "Spy" Queue (Catch-All)

### Declare Non-Durable Spy Queue

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin declare queue name=spy_desk_scheduler durable=false"
```

### Bind to Exchange with Wildcard Routing Key

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin declare binding source=desk_scheduler_events destination_type=queue destination=spy_desk_scheduler routing_key='#'"
```

### Verify Bindings

```cmd
docker compose exec rabbitmq rabbitmqctl list_bindings source_name source_kind destination_name destination_kind routing_key arguments
```

---

## Publish Test Messages

### Method A: From Broker (rabbitmqadmin)

#### Single Test Message

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin publish exchange=desk_scheduler_events routing_key=test.message payload='{"ping":"ok"}'"
```

#### Five Test Messages (1 per second)

```cmd
for /l %i in (1,1,5) do @docker compose exec rabbitmq sh -lc "rabbitmqadmin publish exchange=desk_scheduler_events routing_key=debug.test payload='{"from":"rabbitmqadmin","n":%i}'" & @timeout /t 1 >nul
```

### Method B: From Inside Scheduler Container

Uses the same environment variables as your application:

```cmd
docker exec -it scheduler-service sh -lc "python - <<'PY'
import os, json, pika, time

host=os.getenv('RABBITMQ_HOST','rabbitmq'); port=int(os.getenv('RABBITMQ_PORT','5672'))
user=os.getenv('RABBITMQ_USERNAME','guest'); pw=os.getenv('RABBITMQ_PASSWORD','guest')
ex=os.getenv('RABBITMQ_EXCHANGE','desk_scheduler_events')
ext=os.getenv('RABBITMQ_EXCHANGE_TYPE','topic')
rk='debug.scheduler.test'

conn=pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(user,pw)))
ch=conn.channel(); ch.exchange_declare(exchange=ex, exchange_type=ext, durable=True)

for i in range(5):
    body=json.dumps({'from':'scheduler-container','i':i,'ts':time.time()})
    ch.basic_publish(exchange=ex, routing_key=rk, body=body)
    print('published', rk, body); time.sleep(0.5)

conn.close()
PY"
```

---

## Consume / Peek Messages from Spy Queue

### Get & Consume Messages (Acknowledge, No Requeue)

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin get queue=spy_desk_scheduler ackmode=ack_requeue_false count=50 encoding=auto"
```

### Peek Without Consuming (Acknowledge but Requeue)

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin get queue=spy_desk_scheduler ackmode=ack_requeue_true count=5 encoding=auto"
```

### Live Loop (Peek Every 2 Seconds)

```cmd
for /l %i in (1,1,999) do @docker compose exec rabbitmq sh -lc "rabbitmqadmin get queue=spy_desk_scheduler ackmode=ack_requeue_true count=5 encoding=auto" & @timeout /t 2 >nul
```

---

## Extra Useful Checks

### Verify Exchange Exists + Type

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin list exchanges name type | grep desk_scheduler_events || true"
```

### List All Bindings

```cmd
docker compose exec rabbitmq sh -lc "rabbitmqadmin list bindings source destination_key destination"
```

### Check Queue Depth

```cmd
docker compose exec rabbitmq rabbitmqctl list_queues name messages
```

---

## Common Gotchas & Tips

### Timezone Considerations

Your scheduler logs show jobs scheduled in UTC. In Europe/Copenhagen, triggers are +1h local time.

**Quick Testing Tip:** Temporarily change one cron expression to `*/1 * * * *` and redeploy.

### Windows CMD Syntax

On Windows CMD, prefer **double quotes** around `sh -lc " … "` strings.

### Docker Compose Issues

If `docker compose exec ...` says "no such service," you're either:
- In the wrong folder, or
- Using a different compose file

Point to it explicitly:

```cmd
docker compose -f PATH\docker-compose.yml exec ...
```

### Container-Level Commands (Always Work)

If you only need logs or exec access, these container-level commands always work:

```cmd
docker logs -f scheduler-service
```

```cmd
docker exec -it scheduler-service sh
```

---

## Quick Reference

| Command Category | Description |
|-----------------|-------------|
| **Logs** | View application logs in real-time |
| **Connections** | Monitor active RabbitMQ connections |
| **Queues** | Inspect queue depths and message counts |
| **Publish** | Send test messages to exchanges |
| **Consume** | Read messages from queues |
| **Debug** | Spy queue for catching all messages |

---

**Happy Debugging! 🐰**