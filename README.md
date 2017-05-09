# paradigms-final

- snake movement (Danny) 

Jessica
- collision detection (with food) /growth
- (possible collision detection with self)

- boosting (spacebar/mouse)

- food generation
    - once a certain amount is eaten, regenerate randomly

- win conditions
	- other player runs into wall or other snake
- if one player closes a window, make the other player's window close

Danny
- networking
    - each keypress, send data to other player
        - send "up" ...
    - each food regeneration - send location of new food - take away old food - a big list with booleans for show/not show
    - syncing up:
        - send (size), exact position of each block


Written Tutorial for Snake
--------------------------

Player 1 Information
- player one is the green snake with the pink head
- player one is controlled by the arrow keys

Player 2 Information
- player two is the yellow snake with the blue head
- player two is controlled by WASD

Starting the Game Connection
- please fill in danny!

General Game Play
- food displays as orange squares on the game screen
- move your snake around the screen to collect food to grow in length
- as players collect food, new food objects regenerate in random spots in the game window
- colliding with the walls or the other player results in death, and the game ends
- the goal is to last longer than your enemy by growing the largest and having them die before you
- on the client side, hitting r once the game is over will restart the game
