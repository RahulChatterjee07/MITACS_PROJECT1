#The following illustrates the motor task is programmed with this software:
# There are always two bars appearing on the screen during task time:
# ● Target​ ​bar: this bar is always white and fixed on a specific position on the screen.
# ● Moving​ ​bar: this bar is always green and its height will change as the subject starts applying force
#red color means rest ​time: when the bar turns red the subject should not apply force
#task time is 4 secs and rest time will vary from 8 secs to 10 secs.
#total number of trials = 50


#setting screen parameters 
screen_height=768;
screen_width=1366;
screen_bit_depth=32;
max_y=384;
default_background_color=72,72,72;

#defining the write_codes header parameter to be true, Presentation will write user defined codes to the output port when an event occurs.
write_codes=true;
pulse_width = 10;

begin;

#setting the parameters(font size, color, position, trial duration) for the 'Text Picture Parts', For more info please visit,
#Help Guide : Presentation : Stimuli : Visual Stimuli : Picture Stimuli : 2D Graphics.

picture {
    text { 
        caption = "Enter Subject ID here:"; 
        font_size = 48;
    } instruct_text2;
    x = 0; y = 200;
    
    text { 
        caption = " ";
        font_size = 48;
    } my_text2;
    x = 0; y = 0;
} my_pic5;

picture {
    text { 
        caption = "Type your MVC below:"; 
        font_size = 48;
    } instruct_text;
    x = 0; y = 200;
    
    text { 
        caption = " ";
        font_size = 48;
    } my_text;
    x = 0; y = 0;
} my_pic;

picture {
    text { 
        caption = "Type your choice below \n press 1 for left hand \n 2 for right hand";
        font_size = 48;
    } instruct_text1;
    x = 0; y = 200;
    
    text { 
        caption = " ";
        font_size = 48;
    } my_text4;
    x = 0; y = 0;
} my_pic4;



picture {} default; 
trial { 
    
trial_duration = 3000; 
    
    picture { 
        text { caption = "Loading please wait!!!"; font_size = 40; font_color=0,0,0; }; x = 0; y = 0;
    } ; time = 0; 
    code = "inst";
} inst;

#setting the parameters for the Scenario Objects related to stimulus delivery 
#color code is as follows: green = [0 255 0]; red = [255 0 0]; blue = [0 0 255];
#For more info please visit  Help Guide : Presentation : Writing Scenarios : PCL Programming : Scenario Object Access

trial {
stimulus_event {
picture { 
box { height = 0.1; width = 150; color = 153, 255, 153; } moving_bar;#moving_bar's height will change based on the applied force.
x = 0; y = 0;
box { height = 10; width = 150; color = 255,255,255; } target_bar;#target_bar's position is at the target force level(15% of MVC).
x = 0; y = 0;
} my_pic1;
code = "Main Feedback";
port_code=255; #To assign a code to a stimulus, you must define the stimulus event port_code parameter. The value of port_code must be an integer between and including 0 and 2147483647
#though some port codes may not be reasonable for your specific port output device. As example, to send trigger to brain vision EEG system, we can send port_code 255(2^8 -1) because trigger box of this EEG system can take upto 8 bit digital inputs.

} my_event1;
} my_trial1;


trial {
stimulus_event {
picture { 
box { height = 10; width = 350; color = 255,0,0; } rest_box;# rest_box is shown during the rest time and the subject don't need to apply force at that time
x = 0; y = 0;

} my_pic3;
code = "Main FeedbackRest";

} my_event3;
} my_trial3;

trial {
    trial_duration = 6000;
} wait_trial;

trial { 
        picture { text { caption = "Prepare for the task."; font_size = 24;}instructions; 
x = 0; y = 0; 
        } pic1;
time = 0;
duration = 3000;
}trial1;

# PLC starts
begin_pcl;

# taking input values from the participant using keyboard
string input2 = system_keyboard.get_input( my_pic5, my_text2, "" );#input for file name
string input = system_keyboard.get_input( my_pic, my_text, "" );#input for MVC
string input1 = system_keyboard.get_input( my_pic4, my_text4, "" );#input for their choice of hand(left or right)

double MVC = -int(input)*0.15; # computing the 15 % of the MVC
double MVC2 = abs(350/MVC);

int joyoffset = 0;
int threshold = 0;

joystick joy = response_manager.get_joystick( 1 ); # Initialize the grip device
inst.present();
string filename=input2;
output_file ofile = new output_file;
ofile.open( filename + ".txt");
# visual feedback for left hand

if int(input1)==1 then
	int start_y = clock.time();
	loop until clock.time()>= start_y+1000
	begin
    trial1.present();
            joy.poll();
            joyoffset = joy.y();  # measuring the offset of the '932' device   
	end;
	trial1.present();
	my_pic1.set_part_y( 1, -150,  my_pic1.BOTTOM_COORDINATE); #align the cursor_bar at the bottom of the screen


		loop int j = 1 until    j > 50  #setting the number of trials                                           
	begin;
            int st_time = clock.time();
            int joyval = 1; #push up the screen center
            my_trial1.present();
            loop until clock.time()>= st_time+4000  #setting the task time 4000 secs
            begin;
                 joy.poll();
                 #wait_interval( 40 );
                 moving_bar.set_height(MVC2*abs(((joy.y() - joyoffset)-joyval)) );
						my_pic1.set_part_y( 2, 200);
						ofile.print(abs(joy.y() - joyoffset)) ;# saving force values to the output file
						ofile.print("\t");
						ofile.print("\t");
						ofile.print("\t");
						ofile.print(j);
					
						ofile.print( "\n" );
						
                 my_pic1.present();
            end;
             moving_bar.set_height(10);
				 my_pic3.set_part_y( 1, 0);
				 	
				 my_pic3.present();
             wait_trial.set_duration(random(8000,10000));  #setting the rest time
             wait_trial.present();
		j = j + 1;
	end;
end;

#visual feedback for right hand

if int(input1)==2 then
	int start_y = clock.time();
loop until clock.time()>= start_y+1000
begin
    trial1.present();
            joy.poll();
            joyoffset = joy.x();     
end;
trial1.present();
my_pic1.set_part_y( 1, -150,  my_pic1.BOTTOM_COORDINATE);


loop int j = 1 until    j > 50                                           
begin;
            int st_time = clock.time();
            int joyval = 1; #push up / 0 - screen center
            my_trial1.present();
            loop until clock.time()>= st_time+4000
            begin;
                 joy.poll();
                 
                 moving_bar.set_height(MVC2*abs(((joy.x() - joyoffset)-joyval)) );
						
                 my_pic1.set_part_y( 2, 200);
						
						ofile.print(abs(joy.x() - joyoffset)) ; # saving force values to the output file
						ofile.print("\t");
						ofile.print("\t");
						ofile.print("\t");
						ofile.print(j);
					
						ofile.print( "\n" );
					  	
                 my_pic1.present();
            end;
             moving_bar.set_height(10);
				 my_pic3.set_part_y( 1, 0);
				 	
				 
             my_pic3.present();
             wait_trial.set_duration(random(8000,10000));
             wait_trial.present();
    j = j + 1;
end;
end;


