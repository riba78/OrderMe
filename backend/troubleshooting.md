# Troubleshooting: 500 Internal Server Error on Signin

## Problem
When attempting to sign in via the `/auth/signin` endpoint, a `500 Internal Server Error` is returned. The backend logs show an error similar to:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?
```

## Symptoms
- The API returns a 500 error on signin attempts.
- The backend log contains a traceback ending with `sqlalchemy.exc.MissingGreenlet` and a message about `greenlet_spawn`.
- The error occurs when accessing a relationship (e.g., `user.admin_manager`) in an async context.

## Root Cause
- SQLAlchemy relationships are lazy-loaded by default. In async mode, accessing a relationship property (like `user.admin_manager`) triggers a synchronous database call, which is not allowed in an async context.
- This results in the `MissingGreenlet` error.

## Solution
- Use eager loading for relationships in async queries. Specifically, use `.options(selectinload(...))` in your repository methods to ensure related objects are loaded with the main query.

### Example Fix
In `user_repository.py`, update your query as follows:

```python
from sqlalchemy.orm import selectinload

async def find_by_email(self, email: str) -> Optional[User]:
    stmt = (
        select(User)
        .options(selectinload(User.admin_manager))
        .where(User.admin_manager.has(email=email))
    )
    result = await self.session.execute(stmt)
    return result.scalars().first()
```

Repeat for any other repository methods that access relationships in async context.

## Verification
- Restart your backend server after making the change.
- Retry the signin request. You should now receive a 200 OK response with a valid token if credentials are correct.

---

**If you encounter other async/sync errors with SQLAlchemy, always check for lazy-loaded relationships and use eager loading as needed.** 