"""StandX Maker Bot - Web UI (Gradio) with Modern Dark Design.

Usage:
    python web_ui.py
"""
import gradio as gr
import asyncio
import threading
import logging
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, List
# from collections import deque  # No longer needed

# import plotly.graph_objects as go  # No longer needed

from config import Config
from api.auth import StandXAuth
from api.http_client import StandXHTTPClient
from api.ws_client import MarketWSClient, UserWSClient
from core.state import State, OpenOrder
from core.maker import Maker
from referral import check_if_referred, apply_referral


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Modern Dark Theme CSS with Fintech/Crypto styling
CUSTOM_CSS = """
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@400;500;600;700&display=swap');

/* Root variables */
:root {
    --bg-primary: #0A0E27;
    --bg-secondary: #121829;
    --bg-card: rgba(18, 24, 41, 0.8);
    --border-color: rgba(139, 92, 246, 0.15);
    --border-hover: rgba(139, 92, 246, 0.4);
    --primary: #8B5CF6;
    --primary-glow: rgba(139, 92, 246, 0.4);
    --accent: #F59E0B;
    --accent-glow: rgba(245, 158, 11, 0.4);
    --success: #10B981;
    --success-glow: rgba(16, 185, 129, 0.4);
    --danger: #EF4444;
    --danger-glow: rgba(239, 68, 68, 0.4);
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
}

/* Global container */
.gradio-container {
    background: var(--bg-primary) !important;
    min-height: 100vh;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Background mesh gradient animation */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background:
        radial-gradient(ellipse at 20% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(245, 158, 11, 0.06) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(16, 185, 129, 0.04) 0%, transparent 70%);
    pointer-events: none;
    z-index: -1;
}

/* Main container */
.main {
    background: transparent !important;
    padding: 24px !important;
}

/* Headers - Space Grotesk */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
}

h1 {
    font-size: 2rem !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none !important;
}

h2, h3 {
    color: var(--text-primary) !important;
    text-shadow: none !important;
}

/* Labels */
.label, .gr-label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
}

/* Glass card style */
.glass-card {
    background: var(--bg-card) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border-color) !important;
    padding: 20px !important;
    box-shadow:
        0 4px 24px rgba(0, 0, 0, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
    transition: all 0.25s ease !important;
}

.glass-card:hover {
    border-color: var(--border-hover) !important;
    box-shadow:
        0 8px 32px rgba(139, 92, 246, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

/* Text input styling */
input[type="text"], input[type="password"], textarea {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    font-size: 0.9375rem !important;
    transition: all 0.2s ease !important;
}

input[type="text"]:focus, input[type="password"]:focus, textarea:focus {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-glow) !important;
    outline: none !important;
}

input[type="text"]::placeholder, input[type="password"]::placeholder, textarea::placeholder {
    color: var(--text-muted) !important;
}

/* Number input */
input[type="number"] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* Radio buttons */
input[type="radio"] {
    accent-color: var(--primary) !important;
}

/* Slider styling */
input[type="range"] {
    -webkit-appearance: none !important;
    appearance: none !important;
    height: 6px !important;
    background: var(--bg-secondary) !important;
    border-radius: 3px !important;
    outline: none !important;
}

input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none !important;
    appearance: none !important;
    width: 18px !important;
    height: 18px !important;
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border-radius: 50% !important;
    cursor: pointer !important;
    box-shadow: 0 0 10px var(--primary-glow) !important;
    transition: transform 0.2s ease !important;
}

input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.1) !important;
}

input[type="range"]::-moz-range-thumb {
    width: 18px !important;
    height: 18px !important;
    background: linear-gradient(135deg, var(--primary), var(--accent)) !important;
    border: none !important;
    border-radius: 50% !important;
    cursor: pointer !important;
    box-shadow: 0 0 10px var(--primary-glow) !important;
}

/* Dropdown/Select */
.select, .wrap-inner.svelte-1g5ybmg {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}

/* Button styling - Primary */
.primary {
    background: linear-gradient(135deg, var(--primary) 0%, #7C3AED 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 12px 24px !important;
    box-shadow:
        0 4px 16px var(--primary-glow),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
    letter-spacing: 0.02em !important;
}

.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 6px 24px var(--primary-glow),
        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}

.primary:active {
    transform: translateY(0) !important;
}

/* Button styling - Secondary */
.secondary {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    padding: 12px 20px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

.secondary:hover {
    border-color: var(--border-hover) !important;
    background: rgba(139, 92, 246, 0.1) !important;
}

/* Button styling - Stop/Danger */
.stop {
    background: linear-gradient(135deg, var(--danger) 0%, #DC2626 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 12px 24px !important;
    box-shadow:
        0 4px 16px var(--danger-glow),
        inset 0 1px 0 rgba(255, 255, 255, 0.15) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

.stop:hover {
    transform: translateY(-2px) !important;
    box-shadow:
        0 6px 24px var(--danger-glow),
        inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
}

/* Preset buttons */
.preset-conservative {
    background: linear-gradient(135deg, var(--success) 0%, #059669 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 16px var(--success-glow) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

.preset-conservative:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px var(--success-glow) !important;
}

.preset-balanced {
    background: linear-gradient(135deg, var(--primary) 0%, #7C3AED 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 16px var(--primary-glow) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

.preset-balanced:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px var(--primary-glow) !important;
}

.preset-aggressive {
    background: linear-gradient(135deg, var(--accent) 0%, #D97706 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    box-shadow: 0 4px 16px var(--accent-glow) !important;
    transition: all 0.25s ease !important;
    cursor: pointer !important;
}

.preset-aggressive:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px var(--accent-glow) !important;
}

/* Accordion */
details {
    background: var(--bg-card) !important;
    backdrop-filter: blur(12px) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border-color) !important;
    overflow: hidden !important;
}

summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 16px 20px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

summary:hover {
    color: var(--primary) !important;
}

/* Markdown content */
.markdown {
    color: var(--text-secondary) !important;
}

.markdown a {
    color: var(--primary) !important;
    text-decoration: none !important;
    transition: color 0.2s ease !important;
}

.markdown a:hover {
    color: var(--accent) !important;
}

/* Status indicators */
.status-running {
    color: var(--success) !important;
    text-shadow: 0 0 20px var(--success-glow) !important;
}

.status-stopped {
    color: var(--danger) !important;
}

/* Metric cards */
.metric-value {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}

.metric-label {
    font-size: 0.8125rem !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* Plot background */
.plot {
    background: var(--bg-card) !important;
    border-radius: 16px !important;
    border: 1px solid var(--border-color) !important;
}

/* Hide footer */
footer {
    display: none !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px !important;
    height: 8px !important;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary) !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb {
    background: var(--border-color) !important;
    border-radius: 4px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--border-hover) !important;
}

/* Tab styling */
.tab-nav {
    background: var(--bg-secondary) !important;
    border-radius: 12px !important;
    padding: 4px !important;
}

.tab-item {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.tab-item:hover {
    color: var(--text-secondary) !important;
}

.tab-item.selected {
    color: var(--text-primary) !important;
    background: var(--bg-card) !important;
    border-radius: 8px !important;
}

/* Info text */
.gr-html, .gr-markdown {
    color: var(--text-secondary) !important;
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
"""


class BotController:
    """Controls the bot lifecycle with historical data tracking."""

    def __init__(self):
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.stop_event = threading.Event()

        # Bot components
        self.config: Optional[Config] = None
        self.auth: Optional[StandXAuth] = None
        self.http_client: Optional[StandXHTTPClient] = None
        self.market_ws: Optional[MarketWSClient] = None
        self.user_ws: Optional[UserWSClient] = None
        self.state: Optional[State] = None
        self.maker: Optional[Maker] = None

        # Status data for UI
        self.status_data = {
            "connected": False,
            "price": "--",
            "price_float": 0.0,
            "position": 0.0,
            "upnl": 0.0,
            "buy_order": None,
            "sell_order": None,
            "points": "--",
            "start_time": None,
            "logs": [],
            "error": None,
        }

    def start(self, config_dict: dict) -> str:
        """Start the bot."""
        if self.running:
            return "Bot 已在运行中"

        # Clear previous error
        self.status_data["error"] = None

        try:
            # Create config
            self.config = Config.from_dict(config_dict)

            # Start bot thread
            self.stop_event.clear()
            self.thread = threading.Thread(target=self._run_bot, daemon=True)
            self.thread.start()

            # Wait for loop to be ready
            while self.loop is None and self.thread.is_alive():
                threading.Event().wait(0.01)

            if self.loop:
                self.status_data["start_time"] = datetime.now()
                return "✅ Bot 启动成功！"
            else:
                self.status_data["start_time"] = None
                error_msg = self.status_data.get("error", "Bot 启动失败")
                return f"❌ Bot 启动失败: {error_msg}"

        except Exception as e:
            logger.error(f"Failed to start bot: {e}", exc_info=True)
            self.status_data["error"] = str(e)
            self.status_data["start_time"] = None
            return f"❌ 启动失败: {e}"

    def stop(self) -> str:
        """Stop the bot."""
        if not self.running:
            return "Bot 未运行"

        # Set running to False immediately
        self.running = False
        self.stop_event.set()

        # Schedule stop on event loop (don't wait)
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._stop_async(), self.loop)

        # Clear status immediately
        self.status_data["connected"] = False
        self.status_data["start_time"] = None
        self.status_data["error"] = None
        self.status_data["buy_order"] = None
        self.status_data["sell_order"] = None

        return "Bot 已停止"

    def _run_bot(self):
        """Run the bot event loop in separate thread."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._run_async())
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
            self.status_data["logs"].append(f"ERROR: {e}")
        finally:
            self.running = False
            self.loop.close()
            self.loop = None

    async def _run_async(self):
        """Async bot main logic."""
        self.running = True
        self.status_data["connected"] = True
        self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Bot 启动中...")

        try:
            # Initialize authentication
            logger.info("Initializing authentication...")
            self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 正在认证...")
            self.auth = StandXAuth()
            await self.auth.authenticate(self.config.wallet.chain, self.config.wallet.private_key)
            logger.info("Authentication successful")
            self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 认证成功")

            # Check and apply referral
            try:
                is_referred = await check_if_referred(self.auth)
                if not is_referred:
                    logger.info(f"Applying referral code: 0xdalang")
                    result = await apply_referral(self.auth, "0xdalang")
                    if result.get("success") or result.get("code") == 0:
                        logger.info("Referral applied successfully")
                        self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 推荐码已绑定")
            except Exception as e:
                logger.warning(f"Referral check/apply failed: {e}")

            # Initialize clients
            self.http_client = StandXHTTPClient(self.auth)
            self.market_ws = MarketWSClient()
            self.user_ws = UserWSClient(self.auth)

            # Initialize state
            self.state = State()

            # Initialize maker
            self.maker = Maker(self.config, self.http_client, self.state)

            # Setup callbacks
            self._setup_callbacks()

            # Connect WebSockets
            await self.market_ws.connect()
            await self.market_ws.subscribe_price(self.config.symbol)

            # Try to connect user stream, but don't fail if it doesn't work
            try:
                await self.user_ws.connect()
                self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 用户流连接成功")
            except Exception as e:
                logger.warning(f"User stream connection failed: {e}")
                self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 用户流连接失败，将仅使用市场数据")

            # Initialize state from exchange
            await self.maker.initialize()

            # Query initial points and position
            await self._query_initial_data()

            self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Bot 运行中")

            # Start tasks
            tasks = [
                asyncio.create_task(self.market_ws.run(), name="market_ws"),
                asyncio.create_task(self.maker.run(), name="maker"),
                asyncio.create_task(self._periodic_display_update(), name="display_update"),
            ]

            # Only start user_ws if it connected successfully
            if self.user_ws._running:
                tasks.append(asyncio.create_task(self.user_ws.run(), name="user_ws"))

            # Run until stopped
            await asyncio.gather(*tasks, return_exceptions=True)

        except asyncio.CancelledError:
            logger.info("Bot cancelled")
        except Exception as e:
            logger.error(f"Bot error: {e}", exc_info=True)
            error_msg = str(e)
            self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {error_msg}")
            self.status_data["error"] = error_msg
        finally:
            await self._cleanup()

    def _setup_callbacks(self):
        """Setup WebSocket callbacks."""
        # Price callback
        def on_price(data):
            price_data = data.get("data", {})
            last_price = price_data.get("last_price")
            if last_price:
                price = float(last_price)
                self.maker.on_price_update(price)
                self.status_data["price"] = f"${price:,.2f}"
                self.status_data["price_float"] = price

        self.market_ws.on_price(on_price)

        # Order callback
        def on_order(data):
            order_data = data.get("data", {})
            status = order_data.get("status")
            side = order_data.get("side")
            cl_ord_id = order_data.get("cl_ord_id", "")

            logger.info(f"Order update: {side} {status}")

            if status in ("filled", "cancelled", "rejected"):
                if side in ("buy", "sell"):
                    current_order = self.state.get_order(side)
                    if current_order and current_order.cl_ord_id == cl_ord_id:
                        self.state.set_order(side, None)
                        self.maker._pending_check.set()

            # Update order display
            self._update_order_display()

        self.user_ws.on_order(on_order)

        # Position callback
        def on_position(data):
            pos_data = data.get("data", {})
            qty = float(pos_data.get("qty", 0))
            symbol = pos_data.get("symbol", "")

            if symbol == self.config.symbol:
                self.state.update_position(qty)
                self.status_data["position"] = qty

        self.user_ws.on_position(on_position)

    def _update_order_display(self):
        """Update order status display."""
        buy_order = self.state.get_order("buy")
        sell_order = self.state.get_order("sell")

        if buy_order:
            self.status_data["buy_order"] = f"{buy_order.price:.2f} @ {buy_order.qty:.3f}"
        else:
            self.status_data["buy_order"] = "无"

        if sell_order:
            self.status_data["sell_order"] = f"{sell_order.price:.2f} @ {sell_order.qty:.3f}"
        else:
            self.status_data["sell_order"] = "无"

    async def _query_initial_data(self):
        """Query initial points and position."""
        try:
            # Query position with uPNL
            positions = await self.http_client.query_positions(self.config.symbol)
            if positions:
                self.status_data["position"] = positions[0].qty
                self.status_data["upnl"] = positions[0].upnl

            # Query maker points
            import httpx
            headers = {"Authorization": f"Bearer {self.auth.token}", "Accept": "application/json"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get("https://api.standx.com/v1/offchain/maker-campaign/points", headers=headers)
                if r.status_code == 200:
                    points = float(r.json().get("maker_point", 0) or 0) / 1_000_000
                    self.status_data["points"] = f"{points:,.0f}"

            # Update order display
            self._update_order_display()

        except Exception as e:
            logger.debug(f"Failed to query initial data: {e}")

    async def _periodic_display_update(self):
        """Periodically update display data from local state."""
        while self.running:
            try:
                await asyncio.sleep(1)  # Update every 1 second
                # Update display from local state
                self._update_order_display()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Display update error: {e}")

    async def _periodic_status_sync(self):
        """Periodically sync status when user WebSocket is not connected."""
        while self.running:
            try:
                await asyncio.sleep(2)  # Sync every 2 seconds

                # Query positions
                positions = await self.http_client.query_positions(self.config.symbol)
                if positions:
                    self.state.update_position(positions[0].qty)
                    self.status_data["position"] = positions[0].qty
                    self.status_data["upnl"] = positions[0].upnl

                # Query open orders and update local state
                orders = await self.http_client.query_open_orders(self.config.symbol)

                # Clear local orders first
                self.state.set_order("buy", None)
                self.state.set_order("sell", None)

                # Update from server
                for order in orders:
                    if order.side == "buy":
                        self.state.set_order("buy", OpenOrder(
                            cl_ord_id=order.cl_ord_id,
                            side="buy",
                            price=float(order.price),
                            qty=float(order.qty),
                        ))
                    elif order.side == "sell":
                        self.state.set_order("sell", OpenOrder(
                            cl_ord_id=order.cl_ord_id,
                            side="sell",
                            price=float(order.price),
                            qty=float(order.qty),
                        ))

                # Update display
                self._update_order_display()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Status sync error: {e}")

    async def _stop_async(self):
        """Async stop logic."""
        if self.maker:
            await self.maker.stop()
        if self.market_ws:
            await self.market_ws.close()
        if self.user_ws:
            await self.user_ws.close()

        # Cancel orders
        if self.state and self.http_client:
            try:
                orders_to_cancel = []
                if self.state.has_order("buy"):
                    orders_to_cancel.append(self.state.get_order("buy").cl_ord_id)
                if self.state.has_order("sell"):
                    orders_to_cancel.append(self.state.get_order("sell").cl_ord_id)

                if orders_to_cancel:
                    logger.info(f"Cancelling {len(orders_to_cancel)} orders on exit")
                    await self.http_client.cancel_orders(orders_to_cancel)
                    self.state.clear_all_orders()
            except Exception as e:
                logger.error(f"Failed to cancel orders: {e}")

        if self.http_client:
            await self.http_client.close()

    async def _cleanup(self):
        """Cleanup resources."""
        logger.info("Cleaning up...")
        try:
            await self._stop_async()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        finally:
            self.running = False
            self.status_data["connected"] = False
            self.status_data["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] Bot 已停止")

    def get_status(self) -> dict:
        """Get current bot status."""
        # Calculate runtime
        runtime = "00:00:00"
        if self.status_data["start_time"]:
            delta = datetime.now() - self.status_data["start_time"]
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            runtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        return {
            "running": self.running,
            "connected": self.status_data["connected"],
            "price": self.status_data["price"],
            "position": self.status_data["position"],
            "upnl": self.status_data["upnl"],
            "buy_order": self.status_data["buy_order"] or "无",
            "sell_order": self.status_data["sell_order"] or "无",
            "points": self.status_data["points"],
            "runtime": runtime,
            "error": self.status_data.get("error"),
        }


# Global bot controller
bot = BotController()


# Preset configurations
PRESETS = {
    "conservative": {
        "name": "保守模式 🛡️",
        "leverage": 1,
        "order_distance": 20,
        "cancel_distance": 10,
        "rebalance_distance": 30,
        "order_size": 0.005,
        "max_position": 0.05,
        "vol_window": 5,
        "vol_threshold": 3,
    },
    "balanced": {
        "name": "平衡模式 ⚖️",
        "leverage": 3,
        "order_distance": 10,
        "cancel_distance": 5,
        "rebalance_distance": 20,
        "order_size": 0.01,
        "max_position": 0.1,
        "vol_window": 5,
        "vol_threshold": 5,
    },
    "aggressive": {
        "name": "激进模式 🔥",
        "leverage": 10,
        "order_distance": 5,
        "cancel_distance": 3,
        "rebalance_distance": 10,
        "order_size": 0.02,
        "max_position": 0.2,
        "vol_window": 3,
        "vol_threshold": 8,
    },
}


def apply_preset(preset_name: str):
    """Apply a preset configuration."""
    preset = PRESETS.get(preset_name, PRESETS["balanced"])
    return (
        preset["leverage"],
        preset["order_distance"],
        preset["cancel_distance"],
        preset["rebalance_distance"],
        preset["order_size"],
        preset["max_position"],
        preset["vol_window"],
        preset["vol_threshold"],
        f"✅ 已应用 {preset['name']}",
    )


def start_bot(chain, private_key, symbol, order_distance, cancel_distance,
              rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage):
    """Start the bot with given configuration."""
    config = {
        "wallet": {
            "chain": chain,
            "private_key": private_key,
        },
        "symbol": symbol,
        "order_distance_bps": int(order_distance),
        "cancel_distance_bps": int(cancel_distance),
        "rebalance_distance_bps": int(rebalance_distance),
        "order_size_btc": float(order_size),
        "max_position_btc": float(max_position),
        "volatility_window_sec": int(vol_window),
        "volatility_threshold_bps": int(vol_threshold),
        "leverage": int(leverage),
    }

    return bot.start(config)


def stop_bot():
    """Stop the bot."""
    return bot.stop()


def get_bot_status_html():
    """Get current bot status as HTML with modern styling."""
    status = bot.get_status()

    # Modern color variables matching CSS
    PRIMARY = "#8B5CF6"
    ACCENT = "#F59E0B"
    SUCCESS = "#10B981"
    DANGER = "#EF4444"
    TEXT_MUTED = "#64748B"
    TEXT_PRIMARY = "#F8FAFC"

    upnl_color = SUCCESS if status['upnl'] >= 0 else DANGER
    position_color = SUCCESS if status['position'] >= 0 else DANGER

    error_section = ""
    if status.get("error") and not status['running']:
        error_section = f'''
        <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 12px 16px; margin-top: 10px;">
            <p style="color: {DANGER}; margin: 0; font-size: 0.9em;">错误: {status["error"]}</p>
        </div>'''

    return f"""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">运行状态</div>
            <div style="font-size: 1.25rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; color: {SUCCESS if status['running'] else DANGER};">
                {'运行中' if status['running'] else '已停止'}
            </div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">连接状态</div>
            <div style="font-size: 1.25rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; color: {SUCCESS if status['connected'] else DANGER};">
                {'已连接' if status['connected'] else '未连接'}
            </div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">当前价格</div>
            <div style="font-size: 1.5rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: {PRIMARY};">{status['price']}</div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">运行时间</div>
            <div style="font-size: 1.25rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; color: {TEXT_PRIMARY};">{status['runtime']}</div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">持仓 (BTC)</div>
            <div style="font-size: 1.5rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: {position_color};">{status['position']:+.4f}</div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">未实现盈亏 (USD)</div>
            <div style="font-size: 1.5rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: {upnl_color};">{status['upnl']:+.2f}</div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">买单挂单</div>
            <div style="font-size: 1.1rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; color: {TEXT_PRIMARY};">{status['buy_order']}</div>
        </div>
        <div class="glass-card" style="padding: 16px;">
            <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">卖单挂单</div>
            <div style="font-size: 1.1rem; font-weight: 600; font-family: 'Space Grotesk', sans-serif; color: {TEXT_PRIMARY};">{status['sell_order']}</div>
        </div>
    </div>
    <div class="glass-card" style="margin-top: 10px; padding: 16px; background: linear-gradient(135deg, rgba(139, 92, 246, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%); border-color: rgba(139, 92, 246, 0.3);">
        <div style="font-size: 0.75rem; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Maker Points 积分</div>
        <div style="font-size: 1.75rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; color: {ACCENT};">{status['points']}</div>
    </div>
    {error_section}
    """


# Chart functions removed - using text-only display

def save_config(chain, private_key, symbol, order_distance, cancel_distance,
                rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage):
    """Save configuration to file."""
    config = {
        "wallet": {
            "chain": chain,
            "private_key": private_key,
        },
        "symbol": symbol,
        "order_distance_bps": int(order_distance),
        "cancel_distance_bps": int(cancel_distance),
        "rebalance_distance_bps": int(rebalance_distance),
        "order_size_btc": float(order_size),
        "max_position_btc": float(max_position),
        "volatility_window_sec": int(vol_window),
        "volatility_threshold_bps": int(vol_threshold),
        "leverage": int(leverage),
    }

    try:
        with open("config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        return "✅ 配置已保存"
    except Exception as e:
        return f"❌ 保存失败: {e}"


def load_config():
    """Load configuration from file."""
    try:
        if Path("config.yaml").exists():
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            return (
                config.get("wallet", {}).get("chain", "bsc"),
                config.get("wallet", {}).get("private_key", ""),
                config.get("symbol", "BTC-USD"),
                config.get("order_distance_bps", 10),
                config.get("cancel_distance_bps", 5),
                config.get("rebalance_distance_bps", 20),
                config.get("order_size_btc", 0.01),
                config.get("max_position_btc", 0.1),
                config.get("volatility_window_sec", 5),
                config.get("volatility_threshold_bps", 5),
                config.get("leverage", 1),
            )
    except Exception as e:
        logger.error(f"Failed to load config: {e}")

    return (
        "bsc",
        "",
        "BTC-USD",
        10,
        5,
        20,
        0.01,
        0.1,
        5,
        5,
        1,
    )


def create_ui():
    """Create the Gradio UI with Glassmorphism design."""

    with gr.Blocks(
        title="StandX Maker Bot",
        delete_cache=(0, 0)
    ) as app:

        # Modern header with gradient
        gr.HTML("""
        <div style='text-align: center; padding: 20px 0 24px;'>
            <h1 style='margin: 0; font-size: 2.25rem; background: linear-gradient(135deg, #8B5CF6 0%, #F59E0B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;'>StandX Maker Bot</h1>
            <p style='margin-top: 8px; color: #64748B; font-size: 0.9375rem;'>自动化做市商交易机器人</p>
        </div>
        """)

        # Top row: Presets and Control
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML("<h3 style='margin: 0 0 12px 0; color: #94A3B8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>⚡ 快捷预设</h3>")
                with gr.Row():
                    preset_conservative = gr.Button("保守模式 🛡️", variant="secondary", elem_classes=["preset-conservative"])
                    preset_balanced = gr.Button("平衡模式 ⚖️", variant="secondary", elem_classes=["preset-balanced"])
                    preset_aggressive = gr.Button("激进模式 🔥", variant="secondary", elem_classes=["preset-aggressive"])

            with gr.Column(scale=1):
                gr.HTML("<h3 style='margin: 0 0 12px 0; color: #94A3B8; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>🎮 控制</h3>")
                with gr.Row():
                    start_btn = gr.Button("启动", variant="primary", scale=2, elem_classes=["primary"])
                    stop_btn = gr.Button("停止", variant="stop", scale=1, elem_classes=["stop"])

                start_status = gr.Textbox(label="", interactive=False, show_label=False, elem_classes=["glass-card"])

        # Main content - Status display (text only)
        status_html = gr.HTML(value=get_bot_status_html(), label="Bot 状态")

        # Configuration section (collapsible)
        with gr.Accordion("⚙️ 参数配置", open=False):
            with gr.Row():
                # Left - Basic settings
                with gr.Column(scale=1):
                    gr.Markdown("#### 基础设置")

                    chain = gr.Radio(
                        choices=["bsc", "solana"],
                        value="bsc",
                        label="区块链网络",
                        interactive=True
                    )

                    private_key = gr.Textbox(
                        label="私钥",
                        type="password",
                        placeholder="输入钱包私钥（不会上传）",
                    )

                    symbol = gr.Textbox(
                        label="交易对",
                        value="BTC-USD",
                    )

                # Right - Trading parameters
                with gr.Column(scale=1):
                    gr.Markdown("#### 交易参数")

                    with gr.Row():
                        leverage = gr.Slider(
                            minimum=1, maximum=40, value=1, step=1,
                            label="杠杆倍数",
                            info="1-40倍",
                            interactive=True
                        )

                    with gr.Row():
                        order_distance = gr.Slider(
                            minimum=1, maximum=50, value=10, step=1,
                            label="挂单距离 (bps)",
                            info="价格两侧挂单距离",
                            interactive=True
                        )
                        cancel_distance = gr.Slider(
                            minimum=1, maximum=20, value=5, step=1,
                            label="撤单距离 (bps)",
                            info="太近时撤单",
                            interactive=True
                        )

                    with gr.Row():
                        order_size = gr.Slider(
                            minimum=0.001, maximum=0.1, value=0.01, step=0.001,
                            label="订单大小 (BTC)",
                            interactive=True
                        )
                        max_position = gr.Slider(
                            minimum=0.01, maximum=1, value=0.1, step=0.01,
                            label="最大持仓 (BTC)",
                            interactive=True
                        )

                    with gr.Row():
                        vol_window = gr.Slider(
                            minimum=1, maximum=30, value=5, step=1,
                            label="观察窗口 (秒)",
                            interactive=True
                        )
                        vol_threshold = gr.Slider(
                            minimum=1, maximum=20, value=5, step=1,
                            label="波动阈值 (bps)",
                            interactive=True
                        )

                    rebalance_distance = gr.Slider(
                        minimum=5, maximum=50, value=20, step=1,
                        label="重平衡距离 (bps)",
                        info="太远时重挂",
                        interactive=True
                    )

            # Save/Load buttons
            with gr.Row():
                save_btn = gr.Button("💾 保存配置", variant="secondary", elem_classes=["secondary"])
                load_btn = gr.Button("📂 加载配置", variant="secondary", elem_classes=["secondary"])

            save_status = gr.Textbox(label="", interactive=False, show_label=False, elem_classes=["glass-card"])

        # Footer
        gr.HTML("""
        <div style='text-align: center; padding: 24px 0 16px;'>
            <div style='display: inline-flex; align-items: center; gap: 8px; padding: 12px 20px; background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 12px;'>
                <span style='color: #EF4444;'>⚠️</span>
                <span style='color: #94A3B8; font-size: 0.875rem;'>加密货币交易存在高风险，请谨慎使用</span>
            </div>
            <div style='margin-top: 16px;'>
                <a href='https://x.com/frozenraspberry' target='_blank' style='color: #8B5CF6; text-decoration: none; font-size: 0.875rem; transition: color 0.2s;'>@frozenraspberry</a>
                <span style='color: #64748B; margin: 0 8px;'>•</span>
                <span style='color: #64748B; font-size: 0.8125rem;'>StandX Maker Bot v1.0</span>
            </div>
        </div>
        """)

        # Event handlers
        preset_conservative.click(
            fn=apply_preset,
            inputs=[gr.State("conservative")],
            outputs=[leverage, order_distance, cancel_distance, rebalance_distance,
                     order_size, max_position, vol_window, vol_threshold, start_status]
        )

        preset_balanced.click(
            fn=apply_preset,
            inputs=[gr.State("balanced")],
            outputs=[leverage, order_distance, cancel_distance, rebalance_distance,
                     order_size, max_position, vol_window, vol_threshold, start_status]
        )

        preset_aggressive.click(
            fn=apply_preset,
            inputs=[gr.State("aggressive")],
            outputs=[leverage, order_distance, cancel_distance, rebalance_distance,
                     order_size, max_position, vol_window, vol_threshold, start_status]
        )

        start_btn.click(
            fn=start_bot,
            inputs=[chain, private_key, symbol, order_distance, cancel_distance,
                    rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage],
            outputs=start_status
        )

        stop_btn.click(
            fn=stop_bot,
            outputs=start_status
        )

        save_btn.click(
            fn=save_config,
            inputs=[chain, private_key, symbol, order_distance, cancel_distance,
                    rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage],
            outputs=save_status
        )

        load_btn.click(
            fn=load_config,
            outputs=[chain, private_key, symbol, order_distance, cancel_distance,
                     rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage]
        )

        # Auto-refresh status and charts
        app.load(
            fn=get_bot_status_html,
            outputs=status_html
        )

        # Timer for updates (every 2 seconds)
        def refresh_all():
            import time
            time.sleep(2)
            return get_bot_status_html()

        gr.Timer(2).tick(
            fn=refresh_all,
            outputs=status_html
        )

        # Load config on startup
        app.load(
            fn=load_config,
            outputs=[chain, private_key, symbol, order_distance, cancel_distance,
                     rebalance_distance, order_size, max_position, vol_window, vol_threshold, leverage]
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    logger.info("Starting StandX Maker Bot Web UI with Glassmorphism design...")
    logger.info("Open your browser to access the interface")
    app.launch(
        server_name="127.0.0.1",
        server_port=7861,
        share=False,
        inbrowser=True,
        show_error=True,
        css=CUSTOM_CSS,
    )
