# MITACS_PROJECT1

All the scripts are written in PCL and SDL languages, supported by 'Presenation - neurobehavioral systems', a stimulus delivery and experiment control program for neuroscience.

Firstly, run the ‘mvcmeasure_x’ script to measure the maximum voluntary contraction of the right hand and use the gripper ‘X’ (Current Design Grip Force Device - HHSC-2X1-GRFC) for this purpose. Alternatively, run the ‘mvcmeasure_y’ script to measure the maximum voluntary contraction of the left hand and use the gripper ‘Y’ for this purpose.

Run the ‘motor_task_trigger’ script to load the visual stimuli and send trigger to the EEG system or run the ‘motor_task’ script if you want to show the visual stimuli but not using the EEG system.

Details of the Motor Task:
The following illustrates the motor task that is programmed with this software:
There are always two bars appearing on the screen during task time:
Target bar: this bar is always white and fixed on a specific position on the screen.
Moving bar: this bar is always green, and its height will change as the subject starts applying force.
Red color means rest time: when the bar turns red the subject should not apply any force.
Task time is 4 secs and rest time will vary from 8 secs to 10 secs.
