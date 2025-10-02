
import os
import asyncio
import logging
from typing import Set

import discord
from discord import Intents

# ------------- CONFIGURE THESE -------------
# Role names must match exactly (case-sensitive as seen in Discord role settings)
CLAN_ROLE_NAMES = {
    "Main",
    "HaG",
    "Wolverines",
    "Dynasty",
    "Phoenix",
    "Blast",
    "Asylum",
    "Ravens",
}
MEMBER_ROLE_NAME = "Knight"

# If True, when a user no longer has ANY clan roles, remove the Knight role too.
# If False, Knight remains even if they remove all clan roles.
REMOVE_MEMBER_WHEN_NO_CLAN = False
# -------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto-member-linker")

intents = Intents.default()
intents.guilds = True
intents.members = True  # REQUIRED to see role updates

bot = discord.Client(intents=intents)

def role_names_set(member: discord.Member) -> Set[str]:
    return {r.name for r in member.roles}

@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info("Bot is ready. Monitoring role changes...")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    try:
        before_roles = role_names_set(before)
        after_roles = role_names_set(after)

        # Quick exit if no changes
        if before_roles == after_roles:
            return

        # Identify the guild roles for actions
        guild = after.guild
        member_role = discord.utils.get(guild.roles, name=MEMBER_ROLE_NAME)
        if member_role is None:
            logger.warning(f"Member role '{MEMBER_ROLE_NAME}' not found in guild '{guild.name}'.")
            return

        # Make sure the bot can actually manage the Member role
        me = guild.me  # the bot's member in this guild
        if not me.guild_permissions.manage_roles:
            logger.warning("Bot lacks 'Manage Roles' permission.")
            return

        # Role position check: bot role must be above the Member role
        if me.top_role.position <= member_role.position:
            logger.warning(f"Bot's top role must be above '{MEMBER_ROLE_NAME}' to manage it.")
            return

        # Detect clan role addition/removal
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        added_clan = any(r in CLAN_ROLE_NAMES for r in added_roles)
        removed_clan = any(r in CLAN_ROLE_NAMES for r in removed_roles)

        # If a clan role was ADDED -> ensure Member is present
        if added_clan and MEMBER_ROLE_NAME not in after_roles:
            try:
                await after.add_roles(member_role, reason="Auto-add Member when clan role selected")
                logger.info(f"Gave {MEMBER_ROLE_NAME} to {after} due to clan role selection.")
            except discord.Forbidden:
                logger.exception("Forbidden: cannot add Member role (hierarchy or permissions).")
            except discord.HTTPException:
                logger.exception("HTTPException while adding Member role.")

        # If clan role was REMOVED -> (optionally) remove Member when no clan roles remain
        if removed_clan and REMOVE_MEMBER_WHEN_NO_CLAN:
            # Recompute current roles after any additions
            current_roles = role_names_set(after)
            has_any_clan = any(r in CLAN_ROLE_NAMES for r in current_roles)
            if not has_any_clan and MEMBER_ROLE_NAME in current_roles:
                try:
                    await after.remove_roles(member_role, reason="Auto-remove Member when no clan roles remain")
                    logger.info(f"Removed {MEMBER_ROLE_NAME} from {after} (no clan roles left).")
                except discord.Forbidden:
                    logger.exception("Forbidden: cannot remove Member role (hierarchy or permissions).")
                except discord.HTTPException:
                    logger.exception("HTTPException while removing Member role.")
    except Exception:
        logger.exception("Unexpected error in on_member_update")

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("Set your bot token in the DISCORD_TOKEN environment variable.")
    bot.run(token)

if __name__ == "__main__":
    main()
