# Ball Launch Sequence (XBoing)

This diagram shows the sequence of events and method calls when a player launches a ball from the paddle in XBoing.

```
Player         GameController      BallManager         Ball           Paddle         GameState      Pygame Event
  |                  |                 |                |                |               |                |
  |  (press K/click) |                 |                |                |               |                |
  |----------------->|                 |                |                |               |                |
  |                  | handle_events   |                |                |               |                |
  |                  |---------------->| has_ball_in_play()              |               |                |
  |                  |<----------------|                |                |               |                |
  |                  | if no ball in play:              |                |               |                |
  |                  |  balls = ball_manager.balls      |                |               |                |
  |                  |  for ball in balls:              |                |               |                |
  |                  |------------------------------->> | release_from_paddle()          |                |
  |                  |                                  |---> get_launch_velocity_from_guide_pos()
  |                  |                                  |<---                                             
  |                  |                                  | set vx, vy, stuck_to_paddle=False
  |                  |  game_state.set_timer()          |                |               |                |
  |                  |--------------------------------->|                |               |                |
  |                  |<---------------------------------|                |               |                |
  |                  |  post_game_state_events          |                |               |                |
  |                  |--------------------------------->|                |               |                |
  |                  |  post(BallShotEvent)             |                |               |                |
  |                  |--------------------------------->|                |               |                |
  |                  |  post(level title message)       |                |               |                |
  |                  |--------------------------------->|                |               |                |
  |                  |                 |                |                |               |                |
  |                  |                 |                |                |               |                |
== Ball is now moving, not stuck to paddle ==

== Game Loop Update ==
  |                  | update()        |                |                |               |                |
  |                  |---------------->|                |                |               |                |
  |                  |  for ball in balls:              |                |               |                |
  |                  |-------------------------------->>| update()       |               |                |
  |                  |                                  |---> update_rect()
  |                  |                                  |---> _check_paddle_collision()
  |                  |                                  |---> _add_random_factor() (if bounced)
  |                  |                                  |<---
  |                  |                 |                |                 |               |               |

== Rendering ==
  |                  | draw()           |               |                |               |                |
  |                  |---------------->|                |                |               |                |
  |                  |  for ball in balls:              |                |               |                |
  |                  |------------------------------->>| draw()          |               |                |
  |                  |                                 | (draws guide if stuck)          |                |
```

This covers all main steps and self-calls for launching a ball from the paddle.