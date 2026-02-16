import os
import time
import re
from redis import Redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

STREAM_KEY = "agent_events"
GROUP = "workers"
CONSUMER = "worker-1"


def ensure_group():
    try:
        redis_client.xgroup_create(STREAM_KEY, GROUP, id="0", mkstream=True)
    except Exception:
        pass


def publish(run_id: str, event_type: str, message: str):
    redis_client.xadd(STREAM_KEY, {"run_id": run_id, "type": event_type, "message": message})


def extract_discount(goal: str):
    m = re.search(r"(\d{1,2})\s*%|\b(\d{1,2})\s*percent\b", goal.lower())
    if not m:
        return None
    return m.group(1) or m.group(2)


def make_email_from_goal(goal: str) -> str:
    g = goal.strip()

    # Simple dynamic rules (enough to impress recruiters)
    if "refund" in g.lower():
        return (
            "Subject: Refund Approved – Next Steps\n\n"
            "Hi [Customer Name],\n\n"
            "Thanks for reaching out. I’ve reviewed your request and I’m happy to confirm your refund has been approved.\n\n"
            "Next steps:\n"
            "1) We’ve initiated the refund to your original payment method.\n"
            "2) Processing time is typically 3–7 business days depending on your bank/card provider.\n"
            "3) You’ll receive a confirmation email once the refund is completed.\n\n"
            "If you have any questions or need help with anything else, just reply to this message.\n\n"
            "Best regards,\n"
            "Support Team"
        )

    if "apology" in g.lower() or "late" in g.lower() or "delay" in g.lower():
        disc = extract_discount(g)
        if disc:
            code = f"SORRY{disc}"
            offer_line = f"To make it right, we’d like to offer you {disc}% off your next purchase. Use code: {code} at checkout.\n\n"
        elif "free shipping" in g.lower():
            offer_line = "To make it right, we’ve applied free shipping on your next order.\n\n"
        else:
            offer_line = "To make it right, we’d like to offer a discount on your next purchase.\n\n"

        return (
            "Subject: Apology for the Delivery Delay\n\n"
            "Hi [Customer Name],\n\n"
            "I’m really sorry your order arrived later than expected. We understand how frustrating that can be, and we appreciate your patience.\n\n"
            f"{offer_line}"
            "We’re reviewing what happened to prevent this from happening again. If there’s anything else I can do to help, please reply here and I’ll take care of it.\n\n"
            "Best regards,\n"
            "Support Team"
        )

    # Default fallback
    return (
        "Subject: Response to Your Request\n\n"
        "Hi [Customer Name],\n\n"
        f"Thanks for reaching out. Here’s a response based on your request:\n\n"
        f"{g}\n\n"
        "If you can share any additional details, I can tailor this more precisely.\n\n"
        "Best regards,\n"
        "Support Team"
    )


def main():
    ensure_group()
    print("Worker running... waiting for RUN_STARTED events")

    while True:
        resp = redis_client.xreadgroup(
            groupname=GROUP,
            consumername=CONSUMER,
            streams={STREAM_KEY: ">"},
            count=10,
            block=5000,
        )

        if not resp:
            continue

        for _, messages in resp:
            for msg_id, fields in messages:
                run_id = fields.get("run_id")
                event_type = fields.get("type")

                if event_type == "RUN_STARTED":
                    goal = fields.get("message", "")

                    publish(run_id, "STEP", "Analyzing goal")
                    time.sleep(0.5)

                    publish(run_id, "TOOL_CALLED", "Calling tool: search_kb")
                    time.sleep(0.5)

                    publish(run_id, "STEP", "Synthesizing response")
                    time.sleep(0.5)

                    final_text = make_email_from_goal(goal)
                    publish(run_id, "FINAL_OUTPUT", final_text)

                    publish(run_id, "RUN_COMPLETED", "Run completed successfully")

                redis_client.xack(STREAM_KEY, GROUP, msg_id)


if __name__ == "__main__":
    main()
