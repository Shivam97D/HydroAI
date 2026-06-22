"""One-time script: promote shivam1771dahifale@gmail.com to admin."""
import asyncio, sys
sys.path.insert(0, ".")

from database.mongo import get_mongo_db

async def main():
    target = "shivam1771dahifale@gmail.com"
    db = get_mongo_db()

    # If the user doesn't exist yet, create a stub so admin is ready even before first login
    result = await db.users.update_one(
        {"email": target},
        {"$set": {"role": "admin", "email": target}},
        upsert=False,
    )

    if result.matched_count:
        print(f"✅  {target} → role set to 'admin'")
    else:
        print(f"ℹ️   {target} not found in users collection.")
        print("    Register that account via the signup page first, then re-run this script.")
        print("    OR: the user will be auto-promoted to admin on next login if you run this after registration.")

asyncio.run(main())
