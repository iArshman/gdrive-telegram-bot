"""
Web server module for OAuth callbacks and status page
"""
from aiohttp import web, ClientSession
import logging
import os
import time

logger = logging.getLogger(__name__)

# Will be set by main.py
bot = None
db = None
oauth_states = None
CLIENT_ID = None
CLIENT_SECRET = None
REDIRECT_URI = None

def setup_web_module(bot_instance, db_instance, oauth_states_dict, client_id, client_secret, redirect_uri):
    """Initialize web module with dependencies from main.py"""
    global bot, db, oauth_states, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
    bot = bot_instance
    db = db_instance
    oauth_states = oauth_states_dict
    CLIENT_ID = client_id
    CLIENT_SECRET = client_secret
    REDIRECT_URI = redirect_uri

async def get_user_email(access_token):
    """Get user email from Google Drive API (FINAL STABLE VERSION)"""

    try:
        headers = {"Authorization": f"Bearer {access_token}"}

        async with ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/drive/v3/about?fields=user",
                headers=headers
            ) as response:

                if response.status == 200:
                    data = await response.json()
                    email = data.get("user", {}).get("emailAddress")

                    if not email:
                        logger.error(f"Email missing in Drive response: {data}")

                    return email

                else:
                    error_text = await response.text()
                    logger.error(
                        f"Drive API ERROR {response.status}: {error_text}"
                    )

    except Exception as e:
        logger.error(f"Error getting user email: {e}")

    return None
    
async def main_page_handler(request):
    """Handle main page requests"""
    bot_username = (await bot.get_me()).username if bot else "YOUR_BOT_USERNAME"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GDRIVE TELEGRAM BOT</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 16px; 
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                max-width: 500px;
            }}
            .icon {{ font-size: 4em; margin-bottom: 20px; }}
            h1 {{ color: #667eea; margin: 20px 0; }}
            p {{ color: #666; line-height: 1.6; }}
            .status {{ 
                background: #28a745; 
                color: white;
                padding: 10px 20px; 
                border-radius: 20px; 
                display: inline-block;
                margin: 20px 0;
                font-weight: bold;
            }}
            .feature {{
                text-align: left;
                margin: 15px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 8px;
            }}
            .bot-link {{
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                text-decoration: none;
                margin-top: 20px;
                font-weight: bold;
                transition: background 0.3s;
            }}
            .bot-link:hover {{
                background: #764ba2;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">☁️</div>
            <h1>GDRIVE TELEGRAM BOT</h1>
            <div class="status"> Running</div>
            <p>Manage your Google Drive files with Telegram!</p>
            
            <div class="feature">📁 Browse and organize files</div>
            <div class="feature">⬆️ Upload files from Telegram</div>
            <div class="feature">⬇️ Download files to Telegram</div>
            <div class="feature">🔍 Search across your Drive</div>
            <div class="feature">🔗 Generate shareable links</div>
            <div class="feature">💾 View storage information</div>
            
            <a href="https://t.me/{bot_username}" class="bot-link">Open Bot in Telegram</a>

        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def oauth_callback_handler(request):
    """Handle OAuth callback from Google with PKCE-safe token exchange"""

    try:
        code = request.query.get("code")
        state = request.query.get("state")

        if not code or not state:
            return web.Response(
                text="Error: Missing code or state parameters.",
                status=400
            )

        # Validate OAuth session state
        state_data = oauth_states.get(state)

        if not state_data:
            return web.Response(
                text="Session expired. Please restart connection from Telegram.",
                status=400
            )

        user_id = state_data.get("user_id")
        telegram_id = state_data.get("telegram_id")
        flow = state_data.get("flow")
        is_backup = state_data.get("is_backup", False)

        if not flow:
            return web.Response(
                text="OAuth flow session missing. Restart connection.",
                status=400
            )

        # Exchange authorization code securely
        # Google may return extra scopes (e.g. openid, userinfo.email) — disable strict check
        os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"
        flow.fetch_token(code=code)

        credentials = flow.credentials

        # Extract tokens
        tokens_data = {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "expires_at": credentials.expiry.timestamp()
        }

        # Get Gmail address
        email = await get_user_email(credentials.token)

        if not email:
            return web.Response(
                text="Failed to retrieve account email.",
                status=400
            )

        # Save account in database
        account_id = await db.add_account(user_id, email, tokens_data)

        # If this was added as a backup account, mark it as such
        if is_backup:
            await db.set_backup_account(user_id, account_id)

        # Remove used OAuth session
        oauth_states.pop(state, None)

        # Notify Telegram user
        try:
            label = "Backup Account" if is_backup else " GDRIVE TELEGRAM BOT"
            await bot.send_message(
                telegram_id,
                f"✅ <b>{label} Linked:</b> {email}",
                parse_mode="HTML"
            )
        except Exception:
            pass

        return web.Response(
            text="""
            <html>
            <body style='text-align:center;padding-top:100px;font-family:sans-serif;'>
                <h1 style='color:#007bff;'>Success!</h1>
                <p>GDRIVE TELEGRAM BOT is connected. Close this window and return to Telegram.</p>
            </body>
            </html>
            """,
            content_type="text/html"
        )

    except Exception as e:
        logger.error(f"OAuth callback error: {e}")

        return web.Response(
            text="Internal Server Error",
            status=500
        )


def create_web_app():
    """Create and configure the web application"""
    app = web.Application()
    app.router.add_get('/', main_page_handler)
    app.router.add_get('/oauth_callback', oauth_callback_handler)
    return app
