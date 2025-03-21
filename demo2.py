import pandas as pd

# Creating a dictionary with the quotes
quotes_data = {
    "Number": list(range(1, 101)),
    "Quote": [
        "Success is not final, failure is not fatal: It is the courage to continue that counts.",
        "The only place where success comes before work is in the dictionary.",
        "Work hard in silence, let your success be the noise.",
        "Opportunities don't happen. You create them.",
        "Do what you can, with what you have, where you are.",
        "Don't stop when you're tired. Stop when you're done.",
        "The secret to getting ahead is getting started.",
        "Hardships often prepare ordinary people for an extraordinary destiny.",
        "Believe you can and you're halfway there.",
        "If you want something you've never had, you must be willing to do something you've never done.",
        "It does not matter how slowly you go as long as you do not stop.",
        "A river cuts through rock, not because of its power, but because of its persistence.",
        "Difficulties in life are intended to make us better, not bitter.",
        "When you feel like quitting, think about why you started.",
        "Tough times never last, but tough people do.",
        "You may encounter many defeats, but you must not be defeated.",
        "Don't watch the clock; do what it does. Keep going.",
        "Strength grows in the moments when you think you can't go on but keep going anyway.",
        "Fall seven times, stand up eight.",
        "The pain you feel today will be the strength you feel tomorrow.",
        "Dream big and dare to fail.",
        "Your limitation—it's only your imagination.",
        "Success usually comes to those who are too busy to be looking for it.",
        "Make your life a masterpiece; imagine no limitations on what you can be, have, or do.",
        "Don’t let yesterday take up too much of today.",
        "If you can dream it, you can do it.",
        "Do something today that your future self will thank you for.",
        "Great things never come from comfort zones.",
        "It’s not whether you get knocked down, it’s whether you get up.",
        "If people are doubting how far you can go, go so far that you can’t hear them anymore.",
        "Happiness is not something ready-made. It comes from your own actions.",
        "The mind is everything. What you think you become.",
        "Positive anything is better than negative nothing.",
        "Your attitude determines your direction.",
        "What lies behind us and what lies before us are tiny matters compared to what lies within us.",
        "The only limit to our realization of tomorrow is our doubts of today.",
        "A positive attitude brings positive results.",
        "Act as if what you do makes a difference. It does.",
        "You are confined only by the walls you build yourself.",
        "Stay positive. Work hard. Make it happen.",
        "Fear is temporary. Regret is forever.",
        "Do one thing every day that scares you.",
        "Everything you’ve ever wanted is on the other side of fear.",
        "Fear has two meanings: Forget Everything And Run or Face Everything And Rise. The choice is yours.",
        "Failure is the condiment that gives success its flavor.",
        "Success is stumbling from failure to failure with no loss of enthusiasm.",
        "Courage is resistance to fear, mastery of fear—not absence of fear.",
        "Only those who dare to fail greatly can ever achieve greatly.",
        "Failure is not the opposite of success; it’s part of success.",
        "You miss 100% of the shots you don’t take.",
        "Be so good they can't ignore you.",
        "The only way to do great work is to love what you do.",
        "Live as if you were to die tomorrow. Learn as if you were to live forever.",
        "You have within you right now, everything you need to deal with whatever the world can throw at you.",
        "Don’t wait for opportunity. Create it.",
        "A goal without a plan is just a wish.",
        "You are never too old to set another goal or to dream a new dream.",
        "Discipline is the bridge between goals and accomplishment.",
        "Do the best you can until you know better. Then when you know better, do better.",
        "We cannot become what we want by remaining what we are.",
        "A leader is one who knows the way, goes the way, and shows the way.",
        "The function of leadership is to produce more leaders, not more followers.",
        "The greatest glory in living lies not in never falling, but in rising every time we fall.",
        "If your actions inspire others to dream more, learn more, do more, and become more, you are a leader.",
        "A genuine leader is not a searcher for consensus but a molder of consensus.",
        "Leadership is not about being in charge. It is about taking care of those in your charge.",
        "Don't be pushed around by the fears in your mind. Be led by the dreams in your heart.",
        "Do what is right, not what is easy nor what is popular.",
        "It's not about perfect. It’s about effort.",
        "Nothing is impossible. The word itself says 'I'm possible'!",
        "Do what you love, and you’ll never work a day in your life.",
        "Follow your passion. It will lead you to your purpose.",
        "Success is liking yourself, liking what you do, and liking how you do it.",
        "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work.",
        "Believe in yourself, take on your challenges, dig deep within yourself to conquer fears.",
        "You are enough just as you are.",
        "To be yourself in a world that is constantly trying to make you something else is the greatest accomplishment.",
        "Confidence comes not from always being right, but from not fearing to be wrong.",
        "Don't wait for the right opportunity. Create it.",
        "Small daily improvements over time lead to stunning results.",
        "The way to get started is to quit talking and begin doing.",
        "You will never always be motivated, so you must learn to be disciplined.",
        "Success doesn’t come from what you do occasionally, it comes from what you do consistently.",
        "Don’t be afraid to give up the good to go for the great.",
        "The harder the battle, the sweeter the victory.",
        "Your life does not get better by chance, it gets better by change.",
        "Do what you have to do until you can do what you want to do.",
        "A champion is defined not by their wins but by how they can recover when they fall."
    ]
}

# Creating DataFrame
df = pd.DataFrame(quotes_data)

# Saving to an Excel file
file_path = "data/Motivational_Quotes.xlsx"
df.to_excel(file_path, index=False)

file_path
