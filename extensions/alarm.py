from datetime import datetime, timezone
import asyncio
import re
import pytz
import hikari
import lightbulb
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from alarm import filemanager
from alarm.bot_context import BotContext


alarm_plugin: lightbulb.Plugin = lightbulb.Plugin("Alarm Plugin")

timezones: list[str] = pytz.all_timezones
# current alarma - set the alarm to none initially (this is global for the bot)
ALARM_TIME: datetime | None = None
# if the alarm is currently turned on, i.e. it still has to sound
ALARM_ON: bool = True
# currently set timezone
TIME_ZONE: pytz.tzinfo.DstTzInfo = pytz.timezone("GMT")
USER_ID: str = None


def load(bot: lightbulb.BotApp) -> None:

    bot.add_plugin(alarm_plugin)

    # load alarm time and timezone
    global ALARM_TIME
    global TIME_ZONE
    global USER_ID

    loaded_data = filemanager.load_data()
    ALARM_TIME = loaded_data['alarm']
    TIME_ZONE = loaded_data["time_zone"]

    # start async loop which checks if alarm time was reached every few seconds
    loop = asyncio.get_event_loop()
    loop.create_task(alarm_checker())


@alarm_plugin.command
@lightbulb.command('help', 'See available commands')
@lightbulb.implements(lightbulb.SlashCommand)
async def help(ctx: lightbulb.Context) -> None:

    help_general: str = f"Here are the available commands and their options:\n"
    alarm_help: str = f"`/alarm` - Sounds the alarm immediately.\n"
    set_help: str = f"`/alarm set hh:mm` - Set the alarm.\n"
    time_zone_help: str = f"`/alarm timezone ...` - Set the timezone. The command allows you to search all timezones.\n"
    combined_help: str = f"`/alarm set hh:mm timezone ...` - Set the alarm for the specified timezone. The command allows you to search all timezones.\n"
    countdown_help: str = f"`/countdown` - Shows time remaining for alarm.\n"
    tz_info_help: str = f"`/timezone` - Shows the currently set timezone.\n"

    response: str = help_general + alarm_help + set_help + \
        time_zone_help + combined_help + countdown_help + tz_info_help

    await ctx.respond(response)


@alarm_plugin.command
@lightbulb.option(
    name="timezone",
    type=str,
    description=f'[optional] Set the timezone the alarm should be set in.',
    required=False,
    autocomplete=True
)
@lightbulb.option(
    name="set",
    type=str,
    description=f'[optional] [hh:mm] Set the alarm for a time.',
    required=False,
)
@lightbulb.command('alarm', 'Sets an Alarm or sounds it immediately!')
@lightbulb.implements(lightbulb.SlashCommand)
async def alarm(ctx: lightbulb.Context) -> None:
    global ALARM_TIME
    global ALARM_ON
    global TIME_ZONE
    global USER_ID

    response: str = "Could not set alarm or timezone."

    # get user
    USER_ID = "Unknown User"
    try:
        USER_ID = f"<@{ctx.author.id}>"
    except Exception as e:
        # not critical, continue
        print("Username could not be read.")

    print(f"{USER_ID=}")

    # ! nothing was specified -> sound alarm immediately
    if not ctx.options.set and not ctx.options.timezone:
        response = f"@everyone ALARM! from {USER_ID}"

    # ! set timezone but not alarm
    if not ctx.options.set and ctx.options.timezone:
        TIME_ZONE = pytz.timezone(ctx.options.timezone)
        response = f"Timezone set to `{TIME_ZONE.zone}`."
    print(f"{TIME_ZONE=}")

    # ! set alarm
    if ctx.options.set:
        delims = r"[:,.\-_;#\+\*\|\/\\]"
        try:
            time_array: list[str] = re.split(delims, ctx.options.set)
            print(f'{time_array=}')
        except Exception as e:
            await ctx.respond(f"Please specify your time in the format hh:mm.")

        hours: int = int(time_array[0])
        minutes: int = int(time_array[1])
        print(f'{hours=}')
        print(f'{minutes=}')

        # Get the current time in the desired timezone
        current_time: datetime = datetime.now(TIME_ZONE)

        # Create a new datetime object for today with the given hour and minute,
        # directly in the desired timezone
        time_in_tz: datetime = current_time.replace(
            hour=hours, minute=minutes, second=0, microsecond=0)

        # ! if time is in past -> advance one day
        # Compare the target date with the current date
        if time_in_tz <= current_time:
            # add one day to alarm time so it is in the future
            time_in_tz += timedelta(days=1)
            print("Past")

        print(f"{time_in_tz=}")
        ALARM_TIME = time_in_tz
        ALARM_ON = True

        # NOTE get timezone of user
        # discord doesn't have that information without getting the IP address,
        # which would be a privacy concern

        # time from now
        difference: datetime = relativedelta(time_in_tz, current_time)

        time_str: str = ALARM_TIME.strftime("%a %b %d %Y %I:%M %p")
        in_hours: str = "hour" if difference.hours == 1 else "hours"
        in_minutes: str = "minute" if difference.minutes == 1 else "minutes"
        response = f'{USER_ID} set the `ALARM` for `{
            time_str}` in `{TIME_ZONE.zone}` which is in `{difference.hours} {in_hours} and {difference.minutes} {in_minutes}`.'

    # bot respond
    await ctx.respond(response)

    # whatever the alarm was set to, change it in the data json
    filemanager.save_data(alarm_time=ALARM_TIME, time_zone=TIME_ZONE)


@alarm.autocomplete("timezone")
async def timezone_autocomplete(option: hikari.AutocompleteInteractionOption, interaction: hikari.AutocompleteInteraction) -> None:
    try:
        # Get the user's input
        user_input = option.value.lower()

        # Filter timezones based on user input
        filtered_timezones = [
            tz for tz in timezones if user_input in tz.lower()]

        # Limit to first 25 matches to adhere to Discord's limit
        choices = filtered_timezones[:25]

        # Create choice objects for the autocompletion
        await interaction.create_response([
            hikari.CommandChoice(name=choice, value=choice) for choice in choices
        ])
    except Exception as e:
        pass


@alarm_plugin.command
@lightbulb.command('countdown', 'Countdown to the set alarm')
@lightbulb.implements(lightbulb.SlashCommand)
async def countdown(ctx: lightbulb.Context) -> None:
    global ALARM_TIME
    global TIME_ZONE
    global USER_ID

    current_time: datetime = datetime.now(TIME_ZONE)
    # time from now
    difference: datetime = relativedelta(ALARM_TIME, current_time)

    response: str = "No alarm set."
    # if alarm is in past, alarm already rang
    if ALARM_TIME > current_time:
        time_str: str = ALARM_TIME.strftime("%a %b %d %Y %I:%M %p")
        in_hours: str = "hour" if difference.hours == 1 else "hours"
        in_minutes: str = "minute" if difference.minutes == 1 else "minutes"
        alarm_in: str = f'The alarm will sound in `{difference.hours} {
            in_hours} and {difference.minutes} {in_minutes}`.'
        alarm_info: str = f"({time_str} {TIME_ZONE.zone})"
        response = alarm_in + " " + alarm_info

    await ctx.respond(response)


@alarm_plugin.command
@lightbulb.command('timezone', 'Show currently set timezone for the alarm')
@lightbulb.implements(lightbulb.SlashCommand)
async def timezone(ctx: lightbulb.Context) -> None:
    global TIME_ZONE
    await ctx.respond(f"Currently set timezone: `{TIME_ZONE.zone}`")


async def alarm_checker():
    global ALARM_TIME
    global TIME_ZONE

    while True:
        current_time: datetime = datetime.now(TIME_ZONE)

        if ALARM_TIME and current_time >= ALARM_TIME:
            # Sound the alarm
            await sound_alarm()
            # Reset alarm_time to None or to the next scheduled time
            # reset_alarm()

        # Wait for some second before checking again
        await asyncio.sleep(10)


async def sound_alarm():
    global ALARM_ON

    # don't sound alarm if it as not on
    if not ALARM_ON:
        return

    bot = BotContext.get_bot()

    # id of my general channel on my server
    try:
        await bot.rest.create_message(1215341287264354356, "@everyone Alarm!")
    except Exception as e:
        print("Exception when sounding the alarm", e)
        pass
    else:
        print("ALARM")
        ALARM_ON = False
