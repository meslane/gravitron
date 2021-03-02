Gravitron is an n-body Newtonian gravitational physics simulator intended for educational and personal (not scientific) use

Gravitron uses LINEAR INTERPOLATION to calculate the position of bodies.
This means that all bodes travel in a straight line for n seconds before re-calculating the forces upon them and adjusting their courses
Therefore, a lower tick period will result in more precise and, more importantly, MORE STABLE simulations, 
as bodies will travel in straight lines for a lower total amount of simulation time.

The highest available tick period is one hour, meaning that bodies will recalculate their applied forces once every hour of sim time.
This is suitable for producing fluid looking motion in things like solar system simulations, but will not be stable over a period of time
greater than ~100 years. 

Delivering frames to the screen is generally more computationally expensive than calculating body interactions, provided that the number
of simulated bodies is somewhat low. Therefore, increasing the time/frame is a good way to speed up your sim.