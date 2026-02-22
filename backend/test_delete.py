import asyncio
from db.supabase_client import get_supabase

async def test_delete():
    sb = get_supabase()
    print("SB initialized")
    try:
        # just try to delete a fake uuid
        res = sb.table("links").delete().eq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("Result:", res)
        print("Len data:", len(res.data))
    except Exception as e:
        print("Exception:", e)

asyncio.run(test_delete())
