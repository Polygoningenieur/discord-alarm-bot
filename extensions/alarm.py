import lightbulb
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta


alarm_plugin = lightbulb.Plugin("Alarm Plugin")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(alarm_plugin)


@alarm_plugin.command
@lightbulb.option(
    name="set",
    type=str,
    description="[optional] - Specify when the alarm should sound. Format: hh:mm",
    required=False
)
@lightbulb.command('alarm', 'Sets an Alarm or sounds it immediately!')
@lightbulb.implements(lightbulb.SlashCommand)
async def alarm(ctx: lightbulb.Context) -> None:
    # get user
    username: str = "Unknown User"
    try:
        username = ctx.author.username
    except Exception as e:
        # not critical, continue
        print("Username could not be read.")

    # set was not specified -> sound alarm immediately
    if not ctx.options.set:
        await ctx.respond(f"@everyone @{username} ALARM")
    # set alarm
    else:
        delims = r"[:,.\-_;#\+\*\|\/\\]"
        try:
            time_array: list[str] = re.split(delims, ctx.options.set)
            print(f'{time_array=}')
        except Exception as e:
            await ctx.respond(f"Please specify your time in the format hh:mm.")

        hours = int(time_array[0])
        minutes = int(time_array[1])

        # convert to datetime
        # Create a datetime object for today with the given hour and minute
        # without timezone information
        try:
            naive_datetime = datetime.now().replace(
                hour=hours, minute=minutes, second=0, microsecond=0)
        except Exception as e:
            await ctx.respond(f"Please specify your time in the format hh:mm.")

        # TODO if time is in past -> advance one day

        # TODO get timezone of user

        # time from now
        difference = relativedelta(naive_datetime, datetime.now())

        print(f'{hours=}')
        print(f'{minutes=}')
        response: str = f'{username} set the `ALARM` for `{
            naive_datetime.ctime()}` which is in `{difference.hours} hours and {difference.minutes} minutes`.'
        await ctx.respond(response)
