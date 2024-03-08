import lightbulb

alarm_plugin = lightbulb.Plugin("Alarm Plugin")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(alarm_plugin)


@alarm_plugin.command
@lightbulb.option(
    name="set",
    type=str,
    description="[optional] - Specify when the alarm should sound.",
    required=False
)
@lightbulb.command('alarm', 'Sets an Alarm or sounds it immediately!')
@lightbulb.implements(lightbulb.SlashCommand)
async def alarm(ctx: lightbulb.Context) -> None:
    # set was not specified -> sound alarm immediately
    if not ctx.options.set:
        await ctx.respond("ALARM")
    # set alarm
    else:
        print(f'{ctx.options.set=}')
        response: str = f'Alarm set for `{ctx.options.set}`.'
        await ctx.respond(response)
