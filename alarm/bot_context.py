class BotContext:
    bot_instance = None

    @classmethod
    def set_bot(cls, bot):
        cls.bot_instance = bot

    @classmethod
    def get_bot(cls):
        return cls.bot_instance
