---
date: November 1996
section: 6
title: XBOING
---

# NAME

xboing - An X Window System based blockout clone. V2.4

# SYNOPSIS

**xboing** \[-version\] \[-usage\] \[-help\] \[-sync\] \[-display
\<displayName\>\] \[-speed \<1-10\>\] \[-scores\] \[-keys\] \[-sound\]
\[-setup\] \[-nosfx\] \[-grab\] \[-maxvol \<1-100\>\] \[-startlevel
\<1-MAXLEVELS\>\] \[-usedefcmap\] \[-nickname \<name\>\] \[-noicon\]

> -speed \<n\> - The game speed, 1 - 9. 9=Fast\
> -maxvol \<n\> - The maximum volume as percentage\
> -startlevel \<n\> - The starting level for game\
> -help - Produce this help message\
> -sync - Turn on X synchronisation\
> -usage - Print a brief help message\
> -version - Print out the current version\
> -scores - Print out current highscores\
> -keys - Use keys instead of mouse control\
> -sound - Turn audio ON for game\
> -setup - Print setup information\
> -nosfx - Turn off special effects\
> -grab - Turn pointer grabbing on\
> -usedefcmap - Use the default colourmap\
> -nickname \<name\> - Use nickname instead of real one\
> -noicon - Do not create a custom icon\
> -display \<display\> - Set the display for the game

# DESCRIPTION

XBoing is a blockout type game where you have a paddle which you control
to bounce a ball around the game zone destroying blocks with a proton
ball.

Each block carries a different point value. The more blocks you destroy,
the better your score. The person with the highest score wins.

The arena is filled with blocks and other objects. You have a paddle
that can move from left to right at the bottom of the arena. You control
the paddle so that the proton ball bounces around blowing up blocks and
that it does not go past the paddle and out the bottom, much like a
pinball game.

You may like to check out my WWW Home Page for XBoing at the following
URL http://www.catt.rmit.edu.au/xboing/xboing.html

# BLOCK TYPES

The blocks exhibit different behaviour. The bomb block when hit will
explode all other blocks around it. You will score the points for the
blocks exploded by the bomb. If another bomb is beside it then it will
explode also causing a chain reaction. The solid wall brick will not
explode unless next a bomb. The ammunition block will give you four
bullets and so on. Special blocks such as reverse and machine gun will
only last for one ball/level.

There is also a unlimited ammo block that will enable unlimited ammo for
that level. You will always have bullets to shoot with. Cool.

There are random blocks that change their colour and therefore their
points every now and then. They add a bit of interest to the levels.

There is a pirate symbol that will kill your ball if touched. You can
shoot this block 3 times to kill it. Keep away from the Death block, it
terminates your ball! The walls off block will turn the wall bounce off
on both the left and right side of the arena. This will mean the ball
will not bounce off the walls but continue through the wall and wrap
around to the opposite side respectively.

The extra time block will add an extra 20 seconds to the clock to help
you out.

The reverse block will when hit, reverse the controls to the paddle.
This block should be avoided as it makes the game really hard. Hitting
another reverse while already in reverse mode will turn it off. This
control mode is reset to normal for each new ball.

The teleport block will teleport the ball somewhere else on that level.
It will not place you too close to the bottom of the screen or on
another block. If the teleport cannot teleport the ball anywhere as the
board may be full - it will teleport your ball to the paddle and shoot
it off there.

The sticky paddle block will stick the ball to your paddle each time it
is hit and wait until you press fire to shoot it off again.

Some blocks will drop from their starting positions and head off down
the screen until they nearly hit your paddle. These are normal blocks
except they move\... They will not clobber an existing block or move
into a ball. Note that their score will decrease as the move down the
screen!! Get in early I suspect.

There is a roaming dude that just roams around the arena. It has logic
to stop it bouncing into something and will not roam off screen! It is
worth a few hundred points and must be killed.

There is a machine gun block that allows you to shoot much faster. Note
that you will also use your bullets at a greater rate. Can be fun to let
off a burst every now and then. Erases counter blocks very fast.

An extra ball symbol may appear and when hit by a proton ball it will
give you an extra ball!

There is a shrink paddle block that will shrink your paddle to a smaller
size for the level. If you currently have the smallest paddle then it
has no effect.

There is also an expand paddle block that will grow you paddle to a
larger size for the level. If you currently have the largest paddle then
it has no effect.

You can use the bullets to shoot the last pesky blocks or to collect
lots of bonus coins. You will be given 4 bullets when a new level
starts. If you lose a ball you will be given a token 2 bullets. Use
bullets wisely as you will hate yourself when there is one brick left
and the ball is missing it for ever.

Throughout the game the bonus coins will appear. Collect these for bonus
points awarded when the level is finished. Sometimes the coin may appear
as a x2 or x4 symbol which will indicate that the scoring from then
onwards will be multiplied by 2 or 4 respectively. Note: if you get a x2
then x4 then x2 you will go back to x2 mode. Also note that this x2 or
x4 mode will be disabled after each ball death.

Also during the game some special blocks will appear like reverse,
death, extra ball, etc. and then disappear like the bonus coins. These
blocks behave like normal but will disappear.

Sometimes a little eye dude will walk across the top and if shot or hit
by the ball will earn you 10000 points! He will only walk across if the
top row is clear.

If you collect more than 10 bonuses during a level the killer mode is
activated which will turn the ball red and the ball will plough through
all blocks except the solid ones and finish the level very quickly.

The bonus screen will tell you how you went in the last level. Your
bonuses will be added plus the bullet and level bonus. You get 500
points for each bullet not used. You get 3000 points for each bonus and
if you get more than 8 bonuses you get a SUPER BONUS of 50,000 points.
You also receive a new ball every 100,000 points. Pressing space will
skip the bonus animations when the bonus screen appears and your bonus
points will still be added.

Like the special popup blocks you may see a dynamite block that will
when hit kill all other blocks of the same type. Pretty good block
really.

There is a level timer that counts down while playing each level. If you
don\'t complete the level in the allotted time you will not receive the
time bonus which is 100 points per second remaining. You will miss out
on the level bonus if your time runs out.

The ball will be automatically shot off the paddle after about 5 seconds
unless you press the space bar. You can always press \`P\' to pause the
game.

If the ball gets stuck in an infinite loop it will automatically tilt
the board if the ball hasn\'t hit the paddle after a certain time span.
The time span is about 8 seconds I think.

When you get a new ball you will see a small red arc with a moving
yellow dot go from left to right and back again. This yellow dot
indcates the direction of the ball when you start it.

XBoing was started like many other projects to learn Xlib better. I had
the XPM library and was already using it in a Motif application. I
thought that it would be cool to have nice colour pictures/animations in
an Xlib game. So I did. Without the XPM library I would be still playing
with the colours I think.

# OPTIONS

The speed option will adjust the speed of the overall game. It will
except integer numbers between 1 and 9. The speed of the game can be
changed from within the game as well. See Game Control. The default
value is warp 3.

The maxvol option allows you to adjust the maximum volume to be used for
the sound effects if sound is supported. It doesn\'t mean all sounds
will be this volume but they will use that volume as the top volume to
scale against.

The startlevel option allows you to set the starting level for your
games. Note that when your score is placed in the highscore table the
level number is the number of levels completed and not the level number
attained. Also, in the bonus screen your level bonus will be the number
of levels completed multiplied by the level bonus value and not the
current level number! Unless this option is used the first level will
always be level one.

The help option will display a brief one line description of all the
command line options used with xboing.

The sync option will turn on the X Window System synchronisation of all
Xlib calls which means that all calls are flushed by the X server before
continuing. This will cause the game to become slower but enable some
debugging. The default is OFF.

The usage option will print a very brief synopsis of all the command
line options and there value ranges.

The version option prints the version of xboing that you are running.

The scores option will print both the roll of honour and your personal
best scores to standard out. This can be useful if you are not running
the program on an X window display and still want to see what the scores
are.

The keys option will enable the use of the keyboard for game control.
Within the game you may press \<g\> to toggle between mouse and key
control. The default is MOUSE control.

The sound option will enable sound to be turned on if possible. Within
the game you may press \<s\> to toggle sound on or off. The default is
OFF.

The setup option is useful when you have just compiled the program. It
will display the paths of the level & sound directories and also give
you some information on other things.

The nosfx option will turn OFF special effects. The special effect in
question at this stage is the explosion shake. Turning it off will speed
the game up a little bit. The default is ON. Servers without backing
store will have it turn off automatically as the shaking is shocking.

The grab option will tell xboing to grab the mouse pointer when the game
is visible. Pointer grabbing has the effect of stopping you move the
pointer outside the game window. This is useful as it constrains the
mouse and you don\'t get colourmap flashes. The default is Off.

The usedefcmap option will make xboing try to use the default colourmap.
This will be fine if the default colourmap is reasonabily empty (ie: 200
free colour cells!). If you have a complex picture on your background
then this option will not work and xboing will be unable to allocate
enough colours.

The nickname option allows you to specify a nick name for you instead of
using your real name found in the password file. This can be useful for
hiding your identity. Please note that I store the user id in the
highscore file and use that for checking and sorting. You will still
appear only once in the global highscore table.

The noicon option will tell xboing not to create a custom icon. This is
needed with some window managers as they only allow a small number of
colours and the icon uses a quite a few. You may not like this icon
either and want to use your own.

The display option will force the game to be viewed on another display.
The format of the display name is \<xserver:0.0\> like most other
programs where xserver is the name of the display. The default is your
display of course.

You may also set three environment variables used by xboing. They
specify the location of the level files, sounds and the highscore file.
They are listed below.

These environment variables will override the settings that are compiled
into the program.

> XBOING_SCORE_FILE = the highscore file to be used.\
> XBOING_LEVELS_DIR = the directory with the levels.\
> XBOING_SOUND_DIR = the directory with the sounds.\

# GAME CONTROL

Use the mouse to move the paddle left and right by moving the mouse left
and right. All mouse buttons shoot bullets, start ball. The paddle will
follow the mouse pointer. This is the best method and easiest to use by
far IMHO.

Below are the keyboard controls. (Non case sensitive)

> Space = Start game\
> J = Paddle Left\
> K = Shoot bullet\
> L = Paddle Right\
> Right = Paddle Right\
> Left = Paddle Left\
> Escape = End game and return to introduction.\
> i = iconify the game and pause.\
> H = View roll of honour.\
> h = View personal highscores.\
> p = Pause game.\
> d = Kill the ball.\
> a = Toggle audio on/off.\
> s = Toggle special effects on/off.\
> c = Cycle through the intro screens.\
> 1-9 = Game speed where 9 is fastest.\
> + = Increase maximum volume level.\
> - = Decrease maximum volume level.\
> t = Tilt board bumping ball.\
> z = Save current game.\
> x = Load saved game.\
> w = Set starting level.\
> e = Change to level editor.\
> q = Quit XBoing.\

# SAVE/LOAD GAME

XBoing supports a one level save game facility. Every five levels you
complete you have the ability to save the game once. The game will be
saved in your home directory in your account. The ability to save will
be indicated by the highlighted word \"Save\" in the specials area below
the arena.

When playing you can press the save key (see GAME CONTROL) and the
current state of the game will be saved. If you save it will overwrite
any previously saved games. If you had more than 1 saved game it would
make it too easy IMHO.

To load a game that has been saved you start a normal game and then
press the load game key. The saved game will appear and you can start
playing from where you saved.

Please note that the paddle position and ball position is not saved. The
paddle will start from where the mouse is and the ball will start from
the beginning position.

# LEVEL EDITOR

The built in level editor allows you to design your own levels
interactively. You can simply click on a block type and then draw into
the level to add blocks. The level editor can also let you play test the
level before saving it.

To change to the level editor simply press \"e\" while watching the
intro screens. The window will grow right a bit and a tool bar will be
shown. You are now ready to draw away.

The left mouse button is the draw button while the middle mouse button
is the eraser. You can press the mouse button down and also move the
mouse to provide continuous drawing until you release the button in both
draw and erase modes.

The right most most button can be used to find out how much a block is
worth in points. Simply click on a block in the toolbar or level area
and the score will change to the score for that block.

You can play test the level. You will have infinite lives and the level
never finishes. Simply press \"p\" to enter test mode and \"p\" to exit
test mode.

Some basic editing facilities are available such as flipping the board
vertically and horizontally and also scrolling 1 block vertically and
horizontally.

Within the editor there are several keys that can be used.

Below are the keyboard controls. Case sensitive.

> q = Exit editor.\
> p = Start/End play test.\
> r = Redraw the level.\
> s = Save the level.\
> l = Load the level.\
> c = Clear the level.\
> t = Change the time bonus.\
> n = Change the level name.\
> v = Flip board vertically.\
> h = Flip board horizontally.\
> V = Scroll 1 block vertically.\
> H = Scroll 1 block horizontally.\

Level management is

# SCORING

Note: Highscores are saved at the end of each game. If you quit a game
while playing your score will be added to the highscores.

Each block has a point score. Some blocks such as the counter block will
have more than one score associated with it.

Each time the paddle is hit with the ball your earn 10 points. I\'m
nice.

There is a death symbol (a pirate) that when hit by a ball will destroy
your ball. You can shoot them three times to remove them.

At the end of each level you are awarded a level bouns which is level
\<n\> x 100 points. So for level 20 you get 20,000 points! If you fail
to complete the level in the time allotted you will not receive a level
bonus.

XBoing uses two highscore files. One displays the global scores which
will be your best score to date. The other is a personal high score
table with all your attempts (stored in your home directory).

If you obtain the highest score then you will be asked to imput some
words of wisdom to your fellow game players. This short message is
displayed under the Boing Master\'s name and is there for all to see.
This message is saved with the high score file so watch out if it rude.

> red = 100\
> blue = 110\
> green = 120\
> yellow = 140\
> tan = 130\
> purple = 150\
> bomb = 50\
> wall = 0\
> roamer = 400\
> drop = row \* 100\
> specials = 100\
> ammo = 50 plus bullets\
> counter = 200 (each number).\

# SOUND SUPPORT

Xboing has support for sound. It has sound code for the following
machines :-

HP, SUN, NetAudio, LINUX & NetBSD PC Soundblaster, RPLAY sound system,
and DEC Audiofile.

Most support and use the .au format sound files. The linux version just
sends the data down to the audio device which may cause slight clicking
sounds due to the audio file header. Future versions of xboing will
support other machines if patches are sent to me or if I learn the sound
format. I am not going to have heaps of converted files all over the
place in different formats as the archive would be HUGE.

# LEVELS

The levels are not increasingly harder to play - some are but some are
easy. This is because it takes ages to create and design levels.

The level data is specified in a simple ASCII file that can be edited.
The levels are loaded when required from the directory specified when
the game was made.

You can create more levels if you like making sure that they are in the
correct format and that they have a correct filename.

Copy newlevel.data to level??.data and use that for the editing of new
levels.

The format of the level is shown in the newlevel.data file in the source
distribution in the levels directory.

Make sure you have a level title and a time bonus in seconds.

level format: (case sensitive)

> \
> w = wall block\
> r = red block\
> g = green block\
> b = blue block\
> t = tan block\
> p = purple block\
> y = yellow block\
> X = Bomb\
> B = Ammo\
> c = Unlimited Ammo\
> D = Death\
> R = Reverse\
> H = Teleport\
> L = Extra ball\
> M = Machine Gun\
> W = Walls off\
> ? = Random block\
> d = Drop Block\
> + = Roaming dude\
> m = Multiple balls\
> s = sticky block\
> \< = Shrink paddle block\
> \> = Grow paddle block\
> T = Extra Time block\

# NOTES

I will place all new versions of XBoing in /contrib on the site
ftp.x.org. I will post an announcement of the new release in the
newsgroup comp.windows.x.

# REDISTRIBUTION

XBoing - An X11 blockout style computer game

\(c\) Copyright 1993-1997, Justin C. Kibell, All Rights Reserved

The X Consortium, and any party obtaining a copy of these files from the
X Consortium, directly or indirectly, is granted, free of charge, a full
and unrestricted irrevocable, world-wide, paid up, royalty-free,
nonexclusive right and license to deal in this software and
documentation files (the \"Software\"), including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons who receive
copies from any such party to do so. This license includes without
limitation a license to do the foregoing actions under any patents of
the party supplying this software to the X Consortium.

In no event shall the author be liable to any party for direct,
indirect, special, incidental, or consequential damages arising out of
the use of this software and its documentation, even if the author has
been advised of the possibility of such damage.

The author specifically disclaims any warranties, including, but not
limited to, the implied warranties of merchantability and fitness for a
particular purpose. The software provided hereunder is on an \"AS IS\"
basis, and the author has no obligation to provide maintenance, support,
updates, enhancements, or modifications.

# AUTHOR

Justin C. Kibell - Systems Programmer/System Administrator CATT Centre
RMIT - Melbourne - Victoria - Australia. email: jck@catt.rmit.edu.au
SnailMail: PO BOX 260, Eltham, Victoria, Australia, 3095

Computer Science Graduate Royal Melbourne Institute of Technology (RMIT)
Australia

# BUGS

See README documents in source distribution for list of bugs and bug
fixes.

Mail all bug reports/suggestions to jck@catt.rmit.edu.au specifying the
version and machine type you are using. Use \'uname -a\' to explain the
machine type. Please note the version of X11 that you have installed as
well, ie: X11R6, X11R5, X11R4, etc.

Please read all documentation before asking for help - only fair.
