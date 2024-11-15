import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Kalshi', True)

class KalshiConfig(conf.registryValue):
    """Configuration for the Kalshi plugin."""
    pass

conf.registerPlugin('Kalshi', KalshiConfig)
