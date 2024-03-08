import lightbulb

exception_plugin = lightbulb.Plugin("Alarm Plugin")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(exception_plugin)


# TODO error handling
# https://hikari-lightbulb.readthedocs.io/en/latest/api_references/events.html
@exception_plugin.listener(lightbulb.CommandErrorEvent)
async def on_error(event: lightbulb.CommandErrorEvent) -> None:
    if isinstance(event.exception, lightbulb.CommandInvocationError):
        await event.context.respond(f'Something went wrong during invocation of command `{event.context.command.name}`.')
        raise event.exception

    # Unwrap the exception to get the original cause
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.NotOwner):
        await event.context.respond("You are not the owner of this bot.")
    elif isinstance(exception, lightbulb.CommandIsOnCooldown):
        await event.context.respond(f"This command is on cooldown. Retry in `{exception.retry_after:.2f}` seconds.")
    else:
        raise exception
