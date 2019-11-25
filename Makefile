

cpp = g++

ifeq ($(debug), yes)
	CPPFLAGS = -static -s
else
	CPPFLAGS = -Wl,--subsystem,windows -O2 -static -s
endif

wx_dir = D:/wxWidgets304
source = wx2048.cpp
executable = wx2048.exe


ifeq ($(shared),yes)
	type = gcc_dll
	libs = -lwxbase30u -lwxmsw30u_core
else
	type = gcc_lib
	libs = -lwxmsw30u_xrc -lwxmsw30u_html -lwxmsw30u_adv -lwxmsw30u_core -lwxbase30u_xml -lwxbase30u -lwxtiff -lwxjpeg -lwxpng -lwxzlib -lwxexpat -lkernel32 -luser32 -lgdi32 -lcomdlg32 -lwxregexu -lwinspool -lwinmm -lshell32 -lcomctl32 -lole32 -loleaut32 -luuid -lrpcrt4 -ladvapi32
endif

lib_dir = $(wx_dir)/lib/$(type)
LIBRARY = -L$(lib_dir) $(libs)
INCLUDE = -I$(wx_dir)/include -I$(lib_dir)/mswu


$(executable): icon.o $(source)
	$(cpp) -o $@ $^ $(CPPFLAGS) $(INCLUDE) $(LIBRARY)

icon.o: .rc
	windres -o $@ $^


compress: $(executable)
	upx --best $(executable)


.PHONY:

clean:
		rm -f icon.o
	    rm -f $(executable)
