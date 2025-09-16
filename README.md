A simple Telegram bot to organize weekly football matches.  
The bot manages a players list, approvals, ball responsibility, and even shuffles players into teams.  
It also resets automatically every week and posts reminders on match day.

---
  Features
- Open and close a weekly players list
- Add / remove yourself from the list
- Approve attendance
- Volunteer to bring the ball
- Shuffle players randomly into 3 teams
- Weekly automatic reset (list cleared & closed)
- Scheduled match-day reminders

 Commands
 Command                   Description 
 `/start`      Check the bot is alive & get your chat ID 
 `/create`     Open a new player list (clears old one) 
 `/add`        Add yourself to the current list 
 `/remove`     Remove yourself from the list 
 `/print`      Show the current players list 
 `/approve`    Confirm that you’re attending the match 
 `/Ball`       Volunteer to bring the ball 
 `/shuffle`    Randomly split players into 3 teams 
 `/help`       Show available commands


To use :
Clone the code and make sure to change the bot token to yours in the file 'env' .
for testing I recommend just running on terminal, but for activating the project I used heroku to commit the code and keeping it running 24/7 .

