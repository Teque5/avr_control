//tq5 modded 2012.12.16
//taken from http://www.binrev.com/forums/index.php/topic/36656-rs232-control-of-harman-kardon-avr-525/
//PurpleJesus
//Revisited 15 AUG 2009

/* Harman Kardon AVR 525,325, 7200 serial control program
just to see if I could do it and I was really really bored and out of weed.

Enter arguments on the command line to do something
"mr set mr+ set"  to toggle multiroom on off
"mr mr+ set mr+"  to scroll up through multiroom sources
"mr mr+ set mr-"  to scroll down multiroom sources
"mr mr+ mr+ set mr+"  increases multi volume
"mr mr+ mr+ set mr-"  decreases multi volume
Beaware, you need to give it time to exit the menu before sending another command, or you could simply prepend a couple of set's to force it to jump back to normal..  remember the menus are nested, and the sets need to account for that.

"v+" master volume,  first call you might need to double it. if repeated <5 seconds or so, you don't need to.
"v-" master volume down,  
Read through the list, you'll get the idea..  it's a bit quirky and it'll tell you what it thinks you're asking..

Most stuff works so far.  Just have to play with it and learn what erks me about it now..

*/

#define PORT "/dev/ttyUSB0"

#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */
#include <stdlib.h>
#include <poll.h>
#include <time.h>

int fd;   //this will be the handle for the serial port Keep it global


int writeport(int fd, char *chars) {
        int len = strlen(chars);
        //chars[len] = 0x0d; // stick a <CR> after the command
        chars[len+1] = 0x00; // terminate the string properly
        int n = write(fd, chars, strlen(chars));
        if (n < 0) {
                fputs("write failed!\n", stderr);
                return 0;
        }
        return 1;                                                                                                                                                                                                               
}

int readport(int fd, char *result) {
        int iIn = read(fd, result, 254);
        result[iIn-1] = 0x00;
        if (iIn < 0) {
                if (errno == EAGAIN) {
                        printf("SERIAL EAGAIN ERROR\n");
                        return 0;
                } else {
                        printf("SERIAL read error %d %s\n", errno, strerror(errno));
                        return 0;
                }
        }                                       
        return 1;
}


int getch(void)  //this is to get a key without waiting for enter to be pressed...  I think it temporally turns off 'line buffering' not sure though.
{
int ch;
struct termios oldt;
struct termios newt;
tcgetattr(STDIN_FILENO, &oldt); /*store old settings */
newt = oldt; /* copy old settings to new settings */
newt.c_lflag &= ~(ICANON | ECHO); /* make one change to old settings in new settings */
tcsetattr(STDIN_FILENO, TCSANOW, &newt); /*apply the new settings immediatly */
ch = getchar(); /* standard getchar call */
tcsetattr(STDIN_FILENO, TCSANOW, &oldt); /*reapply the old settings */
return ch; /*return received char */
}


int initport(int fd) {
        struct termios options;
        // Get the current options for the port... 
        tcgetattr(fd, &options);
        // Set the baud rates to 4800...
        cfsetispeed(&options, B9600);
        cfsetospeed(&options, B9600);
        // Enable the receiver and set local mode...
        options.c_cflag |= (CLOCAL | CREAD);
        options.c_cflag &= ~PARENB;
        options.c_cflag &= ~CSTOPB;
        options.c_cflag &= ~CSIZE;
        options.c_cflag |= CS8;
        tcsetattr(fd, TCSANOW, &options);
        return 1;
};


struct 
{
 char remote_button[48];  //text of the remote button name
 char avr_function[48];  //text of the AVR_function name
 unsigned int command_hex[4]; //the actual command sequence
 char comment[255]; //the function comment as seen on pdf.  //Why can't I set this to [] and not get stuct <anonymous> problems with the printf %s-formatter lines?
 
} command_list[] =
{
{"Power On", "Power On", {0x80, 0x70, 0xc0, 0x3f},},
{"Power Off", "Power Off", {0x80, 0x70, 0x9f, 0x60},},
{"1", "1",{0x80, 0x70, 0x87, 0x78},},
{"2", "2",{0x80,0x70, 0x88, 0x77},},
{"3", "3", {0x80, 0x70, 0x89, 0x76},},
{"4", "4", {0x80, 0x70, 0x8a, 0x75},},
{"5", "5", {0x80, 0x70, 0x8b, 0x74},},
{"6", "6", {0x80, 0x70, 0x8c, 0x73},},
{"7", "7", {0x80, 0x70, 0x8d, 0x72},},
{"8", "8", {0x80, 0x70, 0x8e, 0x71},},
{"9", "9", {0x80, 0x70, 0x9d, 0x62},},
{"0", "0", {0x80, 0x70, 0x9e, 0x61},},

{"Down<down>", "Down <down>", {0x82, 0x72, 0x9a, 0x65},"Downward directional movement when navigating through OSD menus"},
{"Left<left>", "Left <left>", {0x82, 0x72, 0xc1, 0x3e},"Left directional movement when navigating through OSD menus"},
{"SET", "SET", {0x82, 0x72, 0x84, 0x7b},},
{"Right<right>", "Right<right>", {0x82, 0x72, 0xc2, 0x3d},"Right directional movement when navigating through OSD menus"},
{"Up<up>" ,"Up<up>", {0x82, 0x72, 0x99, 0x66},"Upward directional movement when navigating through OSD menus"},

{"AVR", "AVR Power On", {0x80, 0x70, 0xc0, 0x3f},},
{"DVD", "DVD", {0x80, 0x70, 0xd0, 0x2f},},
{"CD", "CD", {0x80, 0x70, 0xc4, 0x3b},},
{"TAPE", "TAPE", {0x80, 0x70, 0xcc, 0x33},},

{"Stereo", "Stereo", {0x82, 0x72, 0x9b, 0x64},"^"},

{"Mute", "Mute", {0x80, 0x70, 0xc1, 0x3e},},
{"VID1(VCR)", "VID1/VCR", {0x80, 0x70, 0xca, 0x35},},
{"VID2(TV)", "VID2/TV", {0x80, 0x70, 0xcb, 0x34},},
{"VID3(CBL/SAT)", "VID3/CBL/SAT", {0X80, 0x70, 0xce, 0x31},},
{"VID4", "VID4", {0x80, 0x70, 0xd1, 0x2e},},
{"AM/FM", "AM/FM", {0x80, 0x70, 0x81, 0x7e},},
{"CH./Guide", "Channel Guide", {0x82, 0x72, 0x5d, 0xa2},"Access the Channel Trim Settings menu"},
{"6CH/8CH", "6CH / 8CH", {0x82, 0x72, 0xdb, 0x24},"The first transmission of this code shows the current mode.  Subsequent transmissions step through the available modes."},
{"Level-/Down", "Level - Down", {0x82, 0x72, 0x9a,0x65},"Decreases the channel trim level"},
{"Level+/Up", "Level+/Up", {0x82, 0x72, 0x99, 0x66},"Increaces the channel trim level"},
{"Sleep/CH++", "Sleep", {0x80, 0x70, 0xdb, 0x24},},
{"Test Tone", "Test Tone", {0x82, 0x72, 0x8c, 0x73},},
{"Vol Up", "Vol Up +", {0x80, 0x70, 0xc7, 0x38},},
{"Sur/CH", "Surr", {0x82, 0x72, 0x58, 0xa7},"Initates surround mode and displays current mode"},
{"-------", "Surr <down> -", {0x82, 0x72, 0x86, 0x79},"Scroll down through surround choices (down arrow)"},
{"-------", "Surr <up> +", {0x82, 0x72, 0x85, 0x7a},"Scroll up through surround choices (up arrow)"},

{"Night", "Night", {0x82, 0x72, 0x96, 0x69},},
{"Multiroom", "Multiroom", {0x82, 0x72, 0xdf, 0x20},"Accesses the Multiroom menu and displays current status"},
{"-------", "MRmulti<down> -", {0x82, 0x72, 0x5f, 0xa0},"Scroll down through multiroom choices (down arrow)"},
{"-------", "MRmulti<up> +", {0x82, 0x72, 0x5e, 0xa1},"Scroll up through multiroom choices (up arrow)"},
{"Vol Down", "Vol Down -", {0x80, 0x70, 0xc8, 0x37}},


{"Speaker/Menu", "Speaker", {0x82, 0x72, 0x53, 0xac},"Accesses the Speaker Configuration menu"},
{"-------", "Speaker<down>-", {0x82, 0x72, 0x8f, 0x70},"Scrolls down through the speaker configuration choices"},
{"-------", "Speaker<up>+", {0x82, 0x72, 0x8e, 0x71},"Scrolls up through the speaker configuration choices"},

{"Digital/Exit", "Digital", {0x82, 0x72, 0x54, 0xab},"Accesses Digital Input menu and displays input for current source"},
{"-------", "Digital<down>-", {0x82, 0x72, 0x56, 0xa9},"Scrolls down through the list of digital inputs"},
{"-------", "Digital<up>+", {0x82, 0x72, 0x57, 0xa8},"Scrolls up through the list of digital inputs"},
{"Delay/Prev.CH", "Delay", {0x82, 0x72, 0x52, 0xad},"Accesses delay settings"},
{"-------", "Delay<down>-", {0x82, 0x72, 0x8b, 0x74},"Scrolls down through the list of digital inputs"},
{"-------", "Delay<up>+", {0x82, 0x72, 0x8a, 0x75},"Scrolls up through the list of digital inputs"},

{"TUN-M", "TUN/M", {0x80, 0x70, 0x93, 0x6c},},
{"Memory", "Memory", {0x80, 0x70, 0x86, 0x79},},
{"Tuning Up", "Tuning Up +", {0x80, 0x70, 0x84, 0x7b},},
{"Direct", "Direct", {0x80, 0x70, 0x9b, 0x64},},
{"Clear", "Clear", {0x82, 0x72, 0xd9, 0x26},},
{"Preset Up", "Preset Up +", {0x82,0x72,0xd0, 0x2f},},
{"Tuning Down", "Tuning Down -", {0x80, 0x70, 0x85, 0x7a}},
{"OSD", "OSD", {0x82, 0x72,0x5c, 0xa3},},
{"D. Skip", "D. Skip", {0x82, 0x72, 0xdd, 0x22},},
{"Preset Down", "Preset Down -", {0x82, 0x72, 0xd1, 0x2e},},
{"Dolby", "Dolby", {0x82, 0x72, 0x50, 0xaf},"To access a Surround Mode group, first use one of these commands to select the desired mode group.  Issue the command again, as needed, to scroll through the list of available modes."},
{"DTS Surround", "DTS Surround", {0x82, 0x72, 0xa0, 0x5f},"^"},
{"DTS NEO:6", "DTS NEO:6", {0x82, 0x72, 0xa1, 0x5e},"^"},
{"Logic 7", "Logic 7", {0x82, 0x72, 0xa2, 0x5d},"^"},
};
 
////////////////////////////////////////////////////////////////////////////////////////////////
//Send the HEX command over the wire
int send_command(int cmd)
{
int loop;
printf("%i\n",cmd);
char data [4] = ""; //create the null.

for (loop =0; loop < 4; loop++)  //build the command string.
        data[loop] = command_list[cmd].command_hex[loop]; 
        
        if (!writeport(fd, data)){
                printf("write failed\n");  //something went horribly wrong.. 
                return -1;
                }
                
return 0;  
}

//Display command summary and all the other tasty bits...
void show_commands (void)
{
        int loop,loop2 = 0;
        printf("\nCommand List\n");
        for (loop = 0; loop <sizeof(command_list)/sizeof(command_list[0]); loop++)
        {
                printf("%2i%20s%20s\t",loop,command_list[loop].remote_button
                ,command_list[loop].avr_function);
                
                for (loop2 = 0; loop2 < 4; loop2++)
                printf(" %x",command_list[loop].command_hex[loop2]);
                
                printf("\n");
        }
        return;
}

//parse input to determin which command is desired
int parse_input (char *string)
{
        char c;
        char    command_string[256];
        int command =-1;
        int strength = 0;
        int x,y,z = 0; //loops
        //printf("Parsing:%s\n",string);
        for (x=0; x<sizeof(command_list)/sizeof(command_list[0]); x++)
                {
                        strcpy (command_string, command_list[x].avr_function);
                        
                        y = z = 0;
                                                
                        while ((c = tolower(command_string[y])))
                        {
                                if (c == tolower(string[z]))
                                        z++;    
                                                                        
                                y++;
                        }
                        
                        if ((z > strength))
                        {
                                strength = z;
                                command = x;            
                        }                       
                }
                
                if (command < 0) 
                        printf("Not understood\n");
                        else
                printf("My guess is \"%s\" means command # %i: %s (strength= %i)\n",string,command,command_list[command].avr_function,strength);
        
        return command;
}



//***************************************************************************************************************
int main(int argc, char **argv) {

        int loop = 0;
        int command =0;

         fd = open(PORT, O_RDWR | O_NOCTTY | O_NDELAY);  
         
        if (fd == -1) {
                perror("open_port: Unable to open PORT - ");  //opps something bad happened...
                return 1;
        } else {
                fcntl(fd, F_SETFL, 0);
        }
        initport(fd);
        
//check to see if commandline arguments are present
        if (argc >= 2)
        {               
                for (loop =1; loop < argc; loop++)
                {
                        if ((command = parse_input(argv[loop] )) >=0 )
                        send_command( command );
                        usleep(1000000/4);
                }
                
                printf("\n");                   
                return 0;  //exit
        }
        
        show_commands();
        return 0;
                
}
