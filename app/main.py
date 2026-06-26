from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.database import engine
from app.core.redis import get_redis, close_redis
from app.api.v1.router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting Wamato API", version=settings.APP_VERSION, env=settings.ENVIRONMENT)
    await get_redis()
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    yield
    await close_redis()
    await engine.dispose()
    logger.info("Wamato API shut down")


limiter = Limiter(key_func=get_remote_address, default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"])

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Uganda's Trusted Property Marketplace — REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API routes
app.include_router(router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": settings.APP_VERSION}


_PRIVACY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Privacy Policy – Wamato Estates Uganda</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f8fafc; color: #1e293b; line-height: 1.7; }
  .wrap { max-width: 760px; margin: 0 auto; padding: 48px 24px 80px; }
  .logo { font-size: 22px; font-weight: 800; color: #1d4ed8; margin-bottom: 4px; }
  .logo span { color: #f59e0b; }
  h1 { font-size: 28px; font-weight: 700; margin: 24px 0 6px; }
  .meta { color: #64748b; font-size: 14px; margin-bottom: 36px; }
  h2 { font-size: 17px; font-weight: 700; margin: 32px 0 10px; color: #1d4ed8; }
  p, li { font-size: 15px; color: #334155; margin-bottom: 10px; }
  ul { padding-left: 20px; }
  a { color: #1d4ed8; }
  .footer { margin-top: 56px; padding-top: 20px; border-top: 1px solid #e2e8f0;
            font-size: 13px; color: #94a3b8; }
</style>
</head>
<body>
<div class="wrap">
  <div class="logo">Wamato <span>Estates</span></div>
  <p style="color:#64748b;font-size:13px">Uganda's Trusted Property Marketplace</p>
  <h1>Privacy Policy</h1>
  <p class="meta">Effective date: 26 June 2026 &nbsp;|&nbsp; Last updated: 26 June 2026</p>

  <h2>1. Introduction</h2>
  <p>Wamato Estates Uganda ("we", "our", or "us") operates the Wamato mobile application. This policy explains what information we collect, how we use it, and your rights regarding your data.</p>

  <h2>2. Information We Collect</h2>
  <ul>
    <li><strong>Account data</strong> – full name, email address, phone number and role (Seeker, Agent, or Owner) when you register.</li>
    <li><strong>Property listings</strong> – photos, descriptions, location coordinates and pricing that owners and agents submit.</li>
    <li><strong>Messages</strong> – conversations between users conducted through the in-app messaging system.</li>
    <li><strong>Device &amp; usage data</strong> – device type, operating system version, and anonymised usage analytics to improve the app.</li>
    <li><strong>Location data</strong> – approximate location (with your permission) to show properties near you.</li>
  </ul>

  <h2>3. How We Use Your Information</h2>
  <ul>
    <li>To create and manage your account and verify your identity.</li>
    <li>To display property listings and connect seekers with owners and agents.</li>
    <li>To enable in-app messaging between parties.</li>
    <li>To send notifications about saved properties, messages and platform updates.</li>
    <li>To improve and personalise the app experience.</li>
    <li>To comply with applicable Ugandan laws and regulations.</li>
  </ul>

  <h2>4. Sharing of Information</h2>
  <p>We do not sell your personal data. We may share information with:</p>
  <ul>
    <li><strong>Other users</strong> – your display name and property contact details are visible to relevant parties as part of the marketplace function.</li>
    <li><strong>Service providers</strong> – cloud hosting, image storage (Cloudinary) and payment processors who process data on our behalf under strict confidentiality.</li>
    <li><strong>Legal authorities</strong> – where required by Ugandan law or court order.</li>
  </ul>

  <h2>5. Data Storage &amp; Security</h2>
  <p>Your data is stored on secure servers. We use industry-standard encryption (TLS) for data in transit and access controls to protect data at rest. We retain your data for as long as your account is active or as required by law.</p>

  <h2>6. Your Rights</h2>
  <ul>
    <li>Access, correct or delete your personal information at any time via the app's profile settings.</li>
    <li>Withdraw consent for location access through your device settings.</li>
    <li>Request a copy of your data or ask us to delete your account by contacting us below.</li>
  </ul>

  <h2>7. Children's Privacy</h2>
  <p>Wamato is intended for users aged 18 and older. We do not knowingly collect data from children under 18.</p>

  <h2>8. Changes to This Policy</h2>
  <p>We may update this policy from time to time. We will notify you of significant changes via the app or email. Continued use of the app after changes constitutes acceptance of the updated policy.</p>

  <h2>9. Contact Us</h2>
  <p>For privacy questions or data requests, contact us at:</p>
  <p>
    <strong>Wamato Estates Uganda</strong><br>
    Kampala, Uganda<br>
    Email: <a href="mailto:privacy@wamato.ug">privacy@wamato.ug</a>
  </p>

  <div class="footer">
    &copy; 2026 Wamato Estates Uganda. All rights reserved.
  </div>
</div>
</body>
</html>"""


@app.get("/privacy", response_class=HTMLResponse, include_in_schema=False)
async def privacy_policy():
    return HTMLResponse(content=_PRIVACY_HTML)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", path=request.url.path, method=request.method)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
