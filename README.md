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
