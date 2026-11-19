# FlowPilot · Reel POSTER (agent instructions)

Publishes **exactly one** reel per Toronto day to Instagram **@flowpilot2026** from `reels/queue.json`.
It runs three times a day (6:57 AM, backups at 9:17 AM and 12:23 PM Toronto). The first run that finds
nothing posted today posts; the later runs see the post and stop. It needs **no git clone and no rendering**:
only Composio (Instagram) and a public GitHub download, so very little can go wrong.
The scheduled task's prompt contains these same steps; this file is the readable copy.

1. Load tools: ToolSearch `select:mcp__Composio__COMPOSIO_SEARCH_TOOLS,mcp__Composio__COMPOSIO_REMOTE_WORKBENCH,PushNotification`.
   Call COMPOSIO_SEARCH_TOOLS once (use case "publish a reel video to instagram business account",
   session `{generate_id: true}`) and use its session id.
2. **Cell 1** (COMPOSIO_REMOTE_WORKBENCH): read the queue, check Instagram, pick, upload, create the container.

```python
import json, urllib.request, datetime, time
from zoneinfo import ZoneInfo
ACC = "instagram_aum-yade"; IG = "30456987787222787"          # @flowpilot2026 ONLY
BR = "https://raw.githubusercontent.com/stellanrowbotham/Stellan/claude/inspiring-carson-j2hy8y/"
TZ = ZoneInfo("America/Toronto")
q = json.loads(urllib.request.urlopen(BR + "reels/queue.json?cb=" + str(int(time.time()))).read())
r, e = run_composio_tool("INSTAGRAM_GET_IG_USER_MEDIA", {"ig_user_id": IG, "fields": "id,caption,timestamp,permalink", "limit": 30}, account=ACC)
d = (r or {}).get("data", {}); posts = d.get("data", []) if isinstance(d, dict) else []
if e or not isinstance(posts, list): print("ERROR listing posts:", e, str(r)[:300]); raise SystemExit
today = datetime.datetime.now(TZ).date()
pday = lambda ts: datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ).date()
if any(pday(p["timestamp"]) == today for p in posts): print("STOP already posted today"); raise SystemExit
caps = [(p.get("caption") or "").strip() for p in posts]
first = lambda it: it["caption"].strip().split("\n")[0].strip()
done = lambda it: any(c.startswith(first(it)) for c in caps)
cand = [it for it in q["items"] if it.get("status") == "ready" and not done(it)] or [it for it in q.get("reserve", []) if not done(it)]
if not cand: print("EMPTY queue and reserve"); raise SystemExit
it = cand[0]; path = "/home/user/" + it["id"] + ".mp4"
urllib.request.urlretrieve(BR + it["video"], path)
up, err = upload_local_file(path)
if err: print("ERROR upload", err); raise SystemExit
c, ce = run_composio_tool("INSTAGRAM_POST_IG_USER_MEDIA", {"ig_user_id": IG, "media_type": "REELS", "share_to_feed": True, "thumb_offset": it.get("thumb_ms", 0), "caption": it["caption"], "video_file": {"name": it["id"] + ".mp4", "mimetype": "video/mp4", "s3key": up["s3key"]}}, account=ACC)
CID = (c or {}).get("data", {}).get("id"); PICK = it["id"]
print("PICKED", PICK, "CREATION", CID, ce)
```

3. **Cell 2**: publish (same creation id, up to 3 tries) and get the permalink.

```python
pub = None
for i in range(3):
    pr, pe = run_composio_tool("INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH", {"ig_user_id": IG, "creation_id": CID, "max_wait_seconds": 150}, account=ACC)
    pub = (pr or {}).get("data", {}).get("id")
    if pub and not pe: break
    time.sleep(15)
m, _ = run_composio_tool("INSTAGRAM_GET_IG_MEDIA", {"ig_media_id": pub, "fields": "id,permalink,timestamp"}, account=ACC) if pub else (None, None)
print("POSTED" if pub else "FAILED", PICK, (m or {}).get("data", {}).get("permalink"), pe)
```

4. Results:
   - `STOP already posted today` → end, no notification.
   - `POSTED` → end with "Posted <id> <permalink>". Do **not** edit the repo (the producer records it).
   - `EMPTY`, `ERROR` or `FAILED` → send one **PushNotification**: "FlowPilot reel NOT posted: <reason>", then
     end with the same text. If a cell timed out, re-run it once. Never create a second container for a
     creation id that is still processing, and never post more than one reel in a day.
