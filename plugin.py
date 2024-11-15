import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.world as world
import requests

class Kalshi(callbacks.Plugin):
    """Kalshi Prediction Market IRC Bot Plugin"""
    threaded = True  # Make network calls in a separate thread
    
    def kalshi(self, irc, msg, args, query_string):
        """<query>
        
        Search Kalshi prediction markets and display current prices.
        Example: kalshi house seats
        """
        try:
            url = "https://api.elections.kalshi.com/v1/search/series"
            params = {
                "query": query_string,
                "order_by": "querymatch",
                "page_size": 5,
                "fuzzy_threshold": 4
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or 'current_page' not in data or not data['current_page']:
                irc.reply("No results found.")
                return
            
            # Get the top result
            top_series = data['current_page'][0]
            
            # Format header with series information
            series_title = top_series['series_title']
            event_title = top_series['event_title']
            event_subtitle = top_series['event_subtitle']
            
            # Build single output message
            parts = []
            parts.append(f"{ircutils.bold(series_title)} {event_subtitle} |hi {event_title}")
            
            # Get markets and sort by yes_bid price
            if top_series.get('markets'):
                markets = top_series['markets']
                # Filter for markets with active prices and sort by yes_bid
                active_markets = [m for m in markets if m.get('yes_bid', 0) > 0]
                sorted_markets = sorted(active_markets, key=lambda x: x.get('yes_bid', 0), reverse=True)
                
                # Format market outcomes
                market_strs = []
                for market in sorted_markets[:8]:
                    subtitle = market.get('yes_subtitle', 'No subtitle')
                    current_price = market.get('yes_bid', 'N/A')
                    price_delta = market.get('price_delta', 0)
                    
                    # Format price changes with colors
                    if price_delta > 0:
                        delta_str = ircutils.mircColor(f"+{price_delta}¢", 'green')
                    elif price_delta < 0:
                        delta_str = ircutils.mircColor(f"{price_delta}¢", 'red')
                    else:
                        delta_str = f"±{price_delta}¢"
                    
                    market_strs.append(f"{subtitle}: {current_price}¢ ({delta_str})")
                
                if market_strs:
                    parts.append(" | ".join(market_strs))
                
                # If there are more markets with non-zero prices, add count
                remaining = len([m for m in markets if m.get('yes_bid', 0) > 0]) - 8
                if remaining > 0:
                    parts.append(f"(+{remaining} more)")
            
            # Send single combined message
            irc.reply(" | ".join(parts))
            
        except requests.RequestException as e:
            irc.reply(f"Error fetching data: {str(e)}")
        except Exception as e:
            irc.reply(f"Error: {str(e)}")
    
    kalshi = wrap(kalshi, ['text'])


Class = Kalshi
