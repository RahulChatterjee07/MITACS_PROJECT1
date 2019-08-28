#Subject should squeeze the gripper 'X' the hardest possible, using their right hand during 'trialTime' seconds and the calibration bar will go up based on the applied force
#The maximum force level reached (MVC value) will be displayed in the screen after trial time
#The offset and the MVC value will be printed in the terminal as well


#setting screen parameters
screen_height=768;
screen_width=1366;
screen_bit_depth=32;
max_y=384;
default_background_color=72,72,72;

begin;

#setting the parameters(font size, color, position, trial duration) for the 'Text Picture Parts', For more info please visit,
#Help Guide : Presentation : Stimuli : Visual Stimuli : Picture Stimuli : 2D Graphics.
trial { 
    
trial_duration = 1000; 
    
    picture { 
        text { caption = "In a moment, the MVC measurement will start"; font_size = 40; font_color=0,0,0; }; x = 0; y = 0;
    } ; time = 0; 
    code = "inst";
} inst;
trial { 
    
trial_duration = 4000; 
    
    picture { 
        text { caption = "Be ready to squeeze your right hand as hard as possible"; font_size = 40; font_color=0,0,0; }; x = 0; y = 0;
    } ; time = 0; 
    code = "inst1";
} inst1;

trial {
    trial_duration = 4000;
stimulus_event {
picture { 
                text { caption = "your MVC is ... "; font_size = 70; font_color=0,0,0; } my_text2; x = 0; y = 0;
} my_pic2;
code = "Main Observ";
} my_event2;
} my_trial2;

#setting the parameters for the Scenario Objects related to stimulus delivery 
#color code is as follows: green = [0 255 0]; red = [255 0 0]; blue = [0 0 255];
#For more info please visit  Help Guide : Presentation : Writing Scenarios : PCL Programming : Scenario Object Access


trial {
stimulus_event {
picture { 
box { height = 10; width = 150; color = 153, 255, 153; } cursor_bar;#cursor_bar will move based on the latest maximum force value.
x = 30; y = 0;
box { height = 550; width = 1; color = 153, 255, 153; } side_bar1;
x = -45; y = 0;
box { height = 550; width = 1; color = 153, 255, 153; } side_bar2;
x = 105; y = 0;
box { height = 2; width = 150; color = 255, 0, 0; } cursor_bar2;#cursor_bar2 will move based on the applied force.
x = 30; y = -250;
text {
    caption = "hi";
    font_size = 24;
    width = 100;
    height = 100;
    font = "Courier";
    font_color = 51,51,0;
    background_color = 255, 255, 255;
} text1;
x=400;y=250;
} my_pic1;
code = "Main Feedback";


} my_event1;
} my_trial1;

# PLC starts
begin_pcl;

# Initialize the grip device
joystick grip = response_manager.get_joystick( 1 );

# Will fill these values later based on grip 
array<int> grip_vals[0];
int max_x = -1000;
int joyoffset = 0;

inst.present();
#offset measure
int start_os = clock.time();
loop until clock.time()>= start_os+1000
begin
            grip.poll();
            joyoffset = grip.x();     
end;

inst1.present();


# Present the picture and log the onset time
my_trial1.present();
stimulus_data last = stimulus_manager.last_stimulus_data();
my_pic1.set_part_y( 1, -250,  my_pic1.BOTTOM_COORDINATE);
my_pic1.set_part_y( 2, -250,  my_pic1.BOTTOM_COORDINATE);
my_pic1.set_part_y( 3, -250,  my_pic1.BOTTOM_COORDINATE);
# Now loop for 5000 ms while polling the grip device
loop
until
    clock.time() >= last.time() + 5000
begin
    # Get the updated grip val
	int joyval = 10;
    grip.poll();
    int grip_val = grip.x();
	
	 cursor_bar.set_height(0.6*(abs((max_x - joyoffset)-joyval)) );
    my_pic1.set_part_y(4, -250+0.6*(abs((grip.x() - joyoffset)-joyval)));
    # Update max_x if current val exceeds current max
    if ( grip_val > max_x ) then
        max_x = grip_val;
    end;
    text1.set_caption(string(abs(max_x - joyoffset)));
	text1.redraw();
    # Add current value to list
    grip_vals.add( grip_val );
    
    # Present the picture
    my_pic1.present();
end;
int mvcvalue = abs(max_x - joyoffset);
string mvctext = " MVC is : " + string(mvcvalue); 
my_text2.set_caption( mvctext);
my_text2.redraw();
my_trial2.set_duration(5000);
my_trial2.present();   

#Printing MVC and offset value in the terminal 
term.print( "Offset: " + string(joyoffset) );
term.print( "\n mvc: " + string(abs(max_x - joyoffset)) );