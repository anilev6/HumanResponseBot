# Human Response Bot Framework ✅ - A Telegram Tool for Data Collection

The Human Response Bot is a specialized framework designed for the collection of human performance data on specific tasks via Telegram messenger.
This approach can be particularly useful in the development phases of large language models (LLMs),
where it's critical to gather human-generated solutions to the same problems the model will eventually tackle.
<div align="center">
  <img src="3.gif" width="370" alt="bot">
</div>

The user presses `/start`, accepts [Terms and Conditions](ConsentForm_v2.pdf), and receives a one-button menu with the number of tasks left. After pressing the button, a task appears. Once the task is answered, the menu appears again. This cycle continues until all tasks are completed.
The single button menu design allows users to safely exit the chat after completing any task without leaving the conversation in an unresolved state.
To entartain the contributor a little bit [a trivial gamification approach was applied](https://www.researchgate.net/publication/274963385_How_enterprises_play_Towards_a_taxonomy_for_enterprise_gamification) via emoji.

The bot delivers the results to the admins in their chats as soon as the results are ready, in the form of a .json file that includes human answers to the tasks.
The admin can additionally export logs and other documents from MongoDB, or any other chosen database that is used for [persistence](app.py) in order to document the process.

## Usage

To leverage the Human Response Bot for your data collection needs, ensure you have the following prerequisites:

- A structured task database in .json format.
- A Telegram Bot API key, obtainable at no cost by messaging [@BotFather](https://t.me/BotFather) with the command `/newbot`.
- Your Telegram ID and the IDs of any additional administrators, which can be acquired for free through [@getmyid_bot](https://t.me/getmyid_bot).

1. Adopt the [clear_data](clear_data.py) file for your .json tasks "database" and launch the script to clear the data.
2. Adopt the [User Consent Form](ConsentForm_v2.pdf) before gathering the data.
3. Modify the [handlers](handlers.py) file - primarily adjust the constants and the `get_options_from_question` function as per your requirements.
4. Adopt the [settings](settings.py) file and modify anything else if needed.
5. Launch the bot via Docker or any other means.

### In this repository, each branch represents a single task-set from my own use-cases.
