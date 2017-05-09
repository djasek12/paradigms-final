# paradigms-final

Written Tutorial for Snake
--------------------------

Player 1 Information
- player one is the green snake with the pink head
- player one is controlled by the arrow keys

Player 2 Information
- player two is the yellow snake with the blue head
- player two is controlled by WASD

Starting the Game Connection
- player 1: $python snake.py master
- after player 1 runs the above command, player 2 runs: $python snake.py client [optional ip address]
	- default IP address is localhost

General Game Play
- food displays as orange squares on the game screen
- move your snake around the screen to collect food to grow in length
- as players collect food, new food objects regenerate in random spots in the game window
- colliding with the walls or the other player results in death, and the game ends
- the goal is to last longer than your enemy by growing the largest and having them die before you
- on the client side, hitting r once the game is over will restart the game
