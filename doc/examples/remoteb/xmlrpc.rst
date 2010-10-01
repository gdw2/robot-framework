.. Run tools/robotremoteserverB.py on the target platform
   The "OperatingSystem" library will be sent over

===============  ======================== ========================= =====================
    Setting                Value              Value                     Value
===============  ======================== ========================= =====================
Library          RemoteB                  http://localhost:8270     OperatingSystem
Library          String
===============  ======================== ========================= =====================


.. This is a comment
                                       ${cmdout}=                          Read Command Output



======================================  ==================================  ==================  ================
            Test Case                                 Action                   Argument             Argument
======================================  ==================================  ==================  ================
Make sure /etc/passwd file exists       File Should Exist                   /etc/passwd
Make sure user is gwarner               ${user}=                            Run                 whoami
\                                       Should Be Equal                     gwarner             ${user}
Make sure I don't have root access      Failed Create File                  /root/blah
Make sure I have tmp access             Create File                         /tmp/blah
======================================  ==================================  ==================  ================


